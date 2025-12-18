{{
    config(
        materialized='table',
        schema='marts_rh',
        tags=['rh', 'performance', 'P1'],
        indexes=[
            {'columns': ['agent_key']},
            {'columns': ['etape_key']},
            {'columns': ['action']},
            {'columns': ['niveau_performance']}
        ]
    )
}}

/*
    ================================================================
    Mart: Performance des Agents par Étape de Traitement
    ================================================================
    
    ARCHITECTURE: Star Schema (Kimball)
    -----------------------------------
    Sources:
    - fait_traitements (table de faits)
    - dim_agents (dimension)
    - dim_etapes (dimension)
    
    Granularité: Agent × Étape (action)
    
    Objectifs métier:
    - Identifier les agents les plus performants par étape
    - Détecter les besoins en formation
    - Analyser la charge de travail
    - Comparer les performances entre agents
    - Fournir des recommandations de coaching
*/

-- =====================================================
-- SECTION 1: Agrégation depuis la table de faits
-- =====================================================
with stats_agent_action as (
    select
        -- Clés dimensions
        f.agent_key,
        f.etape_key,
        f.action,
        f.agent_id,
        
        -- Volume de travail (mesures agrégées)
        count(*) as nb_actions,
        count(distinct f.dossier_id) as nb_dossiers_traites,
        count(distinct f.jour_action) as nb_jours_actifs,
        
        -- Temps de traitement
        avg(f.duree_minutes) as duree_moyenne_minutes,
        percentile_cont(0.5) within group (order by f.duree_minutes) as mediane_minutes,
        stddev(f.duree_minutes) as ecart_type_minutes,
        min(f.duree_minutes) as min_minutes,
        max(f.duree_minutes) as max_minutes,
        percentile_cont(0.25) within group (order by f.duree_minutes) as p25_minutes,
        percentile_cont(0.75) within group (order by f.duree_minutes) as p75_minutes,
        percentile_cont(0.90) within group (order by f.duree_minutes) as p90_minutes,
        sum(f.duree_minutes) as temps_total_minutes,
        
        -- Période d'activité
        min(f.date_action) as premiere_action,
        max(f.date_action) as derniere_action,
        
        -- Patterns temporels
        avg(f.heure_action) as heure_moyenne_travail,
        mode() within group (order by f.jour_semaine) as jour_prefere
        
    from {{ ref('fait_traitements') }} f
    where f.duree_minutes is not null
      and f.duree_minutes > 0
      and f.agent_id is not null
    group by f.agent_key, f.etape_key, f.action, f.agent_id
),

-- =====================================================
-- SECTION 2: Benchmark par action (référence)
-- =====================================================
benchmark_action as (
    select
        action,
        avg(duree_moyenne_minutes) as benchmark_moyenne,
        percentile_cont(0.5) within group (order by duree_moyenne_minutes) as benchmark_mediane,
        stddev(duree_moyenne_minutes) as benchmark_ecart_type,
        percentile_cont(0.25) within group (order by duree_moyenne_minutes) as benchmark_p25,
        percentile_cont(0.75) within group (order by duree_moyenne_minutes) as benchmark_p75,
        sum(nb_actions) as total_actions_action
    from stats_agent_action
    group by action
),

-- =====================================================
-- SECTION 3: Calcul des indicateurs de performance
-- =====================================================
performance_calc as (
    select
        s.*,
        
        -- Informations benchmark
        b.benchmark_moyenne,
        b.benchmark_mediane,
        b.benchmark_p25,
        b.benchmark_p75,
        b.total_actions_action,
        
        -- Indicateurs de performance
        -- 1. Ratio vs benchmark (< 1 = plus rapide que la moyenne)
        case 
            when b.benchmark_moyenne > 0 
            then s.duree_moyenne_minutes / b.benchmark_moyenne 
            else null 
        end as ratio_vs_benchmark,
        
        -- 2. Écart en minutes par rapport au benchmark
        s.duree_moyenne_minutes - b.benchmark_moyenne as ecart_benchmark_minutes,
        
        -- 3. Coefficient de variation (stabilité)
        case 
            when s.duree_moyenne_minutes > 0 
            then (s.ecart_type_minutes / s.duree_moyenne_minutes) * 100 
            else 0 
        end as coefficient_variation_pct,
        
        -- 4. Productivité (actions par jour actif)
        case 
            when s.nb_jours_actifs > 0 
            then s.nb_actions::numeric / s.nb_jours_actifs 
            else 0 
        end as actions_par_jour,
        
        -- 5. Part de charge sur cette action
        case 
            when b.total_actions_action > 0 
            then (s.nb_actions::numeric / b.total_actions_action) * 100 
            else 0 
        end as pct_charge_action,
        
        -- 6. Score de rapidité (0-100, 100 = le plus rapide)
        case 
            when b.benchmark_p75 > b.benchmark_p25 
            then greatest(0, least(100, 
                100 - ((s.duree_moyenne_minutes - b.benchmark_p25) / 
                       (b.benchmark_p75 - b.benchmark_p25) * 100)
            ))
            else 50 
        end as score_rapidite,
        
        -- 7. Rang par rapidité sur cette action
        row_number() over (
            partition by s.action 
            order by s.duree_moyenne_minutes asc
        ) as rang_rapidite,
        
        -- 8. Rang par volume sur cette action
        row_number() over (
            partition by s.action 
            order by s.nb_actions desc
        ) as rang_volume,
        
        -- Nombre total d'agents sur cette action
        count(*) over (partition by s.action) as nb_agents_action
        
    from stats_agent_action s
    join benchmark_action b on s.action = b.action
),

-- =====================================================
-- SECTION 4: Enrichissement avec dimensions agents et étapes
-- =====================================================
final as (
    select
        -- Identification
        row_number() over (order by p.agent_id, p.action) as perf_id,
        
        -- Clés dimensions
        p.agent_key,
        p.etape_key,
        p.agent_id,
        
        -- Attributs agent (depuis dimension)
        a.nom_agent as agent_nom,
        a.prenom_agent as agent_prenoms,
        coalesce(a.nom_complet, 'Agent #' || p.agent_id::text) as agent_nom_complet,
        a.email as agent_email,
        
        -- Attributs étape (depuis dimension)
        p.action,
        e.action_libelle,
        e.categorie_etape,
        e.responsable_type,
        
        -- Volume de travail
        p.nb_actions,
        p.nb_dossiers_traites,
        p.nb_jours_actifs,
        round(p.actions_par_jour::numeric, 2) as actions_par_jour,
        round(p.pct_charge_action::numeric, 2) as pct_charge_action,
        
        -- Temps de traitement
        round(p.duree_moyenne_minutes::numeric, 2) as duree_moyenne_minutes,
        round((p.duree_moyenne_minutes / 60)::numeric, 2) as duree_moyenne_heures,
        round(p.mediane_minutes::numeric, 2) as mediane_minutes,
        round(p.ecart_type_minutes::numeric, 2) as ecart_type_minutes,
        round(p.min_minutes::numeric, 2) as min_minutes,
        round(p.max_minutes::numeric, 2) as max_minutes,
        round(p.p25_minutes::numeric, 2) as p25_minutes,
        round(p.p75_minutes::numeric, 2) as p75_minutes,
        round(p.p90_minutes::numeric, 2) as p90_minutes,
        round(p.temps_total_minutes::numeric, 2) as temps_total_minutes,
        round((p.temps_total_minutes / 60)::numeric, 2) as temps_total_heures,
        
        -- Benchmark
        round(p.benchmark_moyenne::numeric, 2) as benchmark_moyenne_minutes,
        round(p.benchmark_mediane::numeric, 2) as benchmark_mediane_minutes,
        
        -- Indicateurs de performance
        round(p.ratio_vs_benchmark::numeric, 2) as ratio_vs_benchmark,
        round(p.ecart_benchmark_minutes::numeric, 2) as ecart_benchmark_minutes,
        round(p.coefficient_variation_pct::numeric, 2) as coefficient_variation_pct,
        round(p.score_rapidite::numeric, 2) as score_rapidite,
        
        -- Classifications
        p.rang_rapidite,
        p.rang_volume,
        p.nb_agents_action,
        
        -- Classification performance
        case
            when p.ratio_vs_benchmark < 0.5 then 'EXCELLENT'
            when p.ratio_vs_benchmark < 0.8 then 'BON'
            when p.ratio_vs_benchmark <= 1.2 then 'STANDARD'
            when p.ratio_vs_benchmark <= 1.5 then 'A_AMELIORER'
            else 'CRITIQUE'
        end as niveau_performance,
        
        -- Classification stabilité
        case
            when p.coefficient_variation_pct < 30 then 'TRES_STABLE'
            when p.coefficient_variation_pct < 50 then 'STABLE'
            when p.coefficient_variation_pct < 100 then 'VARIABLE'
            else 'INSTABLE'
        end as niveau_stabilite,
        
        -- Classification volume
        case
            when p.rang_volume = 1 then 'TOP_CONTRIBUTEUR'
            when p.rang_volume <= 3 then 'FORT_CONTRIBUTEUR'
            when p.pct_charge_action > 20 then 'CONTRIBUTEUR'
            else 'OCCASIONNEL'
        end as niveau_contribution,
        
        -- Score global de performance (0-100)
        round(
            (
                -- 40% rapidité
                p.score_rapidite * 0.4 +
                -- 30% stabilité (inversé: faible CV = bon)
                greatest(0, 100 - p.coefficient_variation_pct) * 0.3 +
                -- 30% expérience (basé sur le volume)
                least(100, p.nb_actions * 5) * 0.3
            )::numeric, 2
        ) as score_global_performance,
        
        -- Recommandations
        case
            when p.ratio_vs_benchmark > 1.5 and p.coefficient_variation_pct > 100 
                then 'FORMATION URGENTE: Performance faible et instable'
            when p.ratio_vs_benchmark > 1.5 
                then 'COACHING: Améliorer la rapidité sur cette étape'
            when p.coefficient_variation_pct > 100 
                then 'STANDARDISATION: Besoin de processus plus structuré'
            when p.ratio_vs_benchmark < 0.5 and p.nb_actions >= 5 
                then 'EXPERT: Peut former les autres agents'
            when p.ratio_vs_benchmark < 0.8 
                then 'PERFORMANT: Maintenir les bonnes pratiques'
            else 'NORMAL: Performance conforme aux attentes'
        end as recommandation,
        
        -- Potentiel de gain (si ramené au benchmark)
        case
            when p.ecart_benchmark_minutes > 0 
            then round((p.ecart_benchmark_minutes * p.nb_actions)::numeric, 2)
            else 0
        end as gain_potentiel_minutes,
        
        -- Période d'activité
        p.premiere_action,
        p.derniere_action,
        p.derniere_action - p.premiere_action as periode_activite,
        round(p.heure_moyenne_travail::numeric, 1) as heure_moyenne_travail,
        p.jour_prefere,
        
        -- Métadonnées
        current_timestamp as dbt_updated_at
        
    from performance_calc p
    left join {{ ref('dim_agents') }} a on p.agent_key = a.agent_key
    left join {{ ref('dim_etapes') }} e on p.etape_key = e.etape_key
)

select * from final
order by agent_id, action
