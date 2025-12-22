

/*
    ================================================================
    Mart: Temps de Traitement des Impenses et Goulots d'Étranglement
    ================================================================
    
    ARCHITECTURE: Star Schema (Kimball)
    -----------------------------------
    Sources:
    - fait_workflow_impenses (table de faits)
    - dim_phases_impenses (dimension)
    - dim_impenses (dimension)
    
    Objectifs métier:
    - Identifier les phases les plus longues du workflow impenses
    - Détecter les goulots d'étranglement par phase
    - Analyser les temps de traitement par type de demande
    - Fournir des recommandations automatisées
    
    Indicateurs clés: 12 indicateurs de goulot d'étranglement
    Classification: CRITIQUE / MAJEUR / MODERE / NORMAL
    
    Refresh: Quotidien
    Utilisateurs: Direction DI, Direction DG, Amélioration Continue
*/

-- =====================================================
-- SECTION 1: Agrégation depuis la table de faits
-- =====================================================
with stats_par_phase as (
    select
        -- Clés et attributs de dimension
        f.action,
        p.phase_impense_key,
        p.phase_id,
        p.phase_libelle,
        p.action_libelle,
        p.categorie_phase,
        p.responsable_type,
        p.ordre_workflow,
        p.est_etape_principale,
        p.est_etape_validation,
        p.est_etape_rejet,
        
        -- Volume
        count(*) as nb_occurrences,
        count(distinct f.impense_id) as nb_dossiers_distincts,
        count(distinct f.agent_id) as nb_agents_impliques,
        
        -- Rôles impliqués
        count(distinct f.user_role) as nb_roles_distincts,
        
        -- Temps de traitement (mesures de fait)
        avg(f.duree_minutes) as duree_moyenne_minutes,
        avg(f.duree_heures) as duree_moyenne_heures,
        avg(f.duree_jours) as duree_moyenne_jours,
        percentile_cont(0.5) within group (order by f.duree_minutes) as mediane_minutes,
        stddev(f.duree_minutes) as ecart_type_minutes,
        min(f.duree_minutes) as min_minutes,
        max(f.duree_minutes) as max_minutes,
        percentile_cont(0.75) within group (order by f.duree_minutes) as p75_minutes,
        percentile_cont(0.90) within group (order by f.duree_minutes) as p90_minutes,
        percentile_cont(0.95) within group (order by f.duree_minutes) as p95_minutes,
        sum(f.duree_minutes) as temps_total_minutes,
        sum(f.duree_heures) as temps_total_heures,
        
        -- Indicateurs spécifiques impenses
        sum(f.est_validation) as nb_validations,
        sum(f.est_rejet) as nb_rejets,
        sum(f.est_correction) as nb_corrections,
        sum(f.est_cloture) as nb_clotures
        
    from "sigeti_node_db"."dwh_facts"."fait_workflow_impenses" f
    inner join "sigeti_node_db"."dwh_dimensions"."dim_phases_impenses" p on f.phase_impense_key = p.phase_impense_key
    where f.duree_minutes is not null
      and f.duree_minutes > 0
    group by 
        f.action, p.phase_impense_key, p.phase_id, p.phase_libelle,
        p.action_libelle, p.categorie_phase, p.responsable_type,
        p.ordre_workflow, p.est_etape_principale, p.est_etape_validation,
        p.est_etape_rejet
),

-- =====================================================
-- SECTION 2: Statistiques globales du workflow
-- =====================================================
stats_globales as (
    select
        avg(duree_moyenne_minutes) as moyenne_globale_minutes,
        percentile_cont(0.5) within group (order by duree_moyenne_minutes) as mediane_globale_minutes,
        stddev(duree_moyenne_minutes) as ecart_type_global,
        sum(temps_total_minutes) as temps_total_workflow
    from stats_par_phase
),

-- =====================================================
-- SECTION 3: Agrégation par phase (niveau supérieur)
-- =====================================================
stats_par_phase_agregee as (
    select
        phase_id,
        phase_libelle,
        categorie_phase,
        
        sum(nb_occurrences) as nb_actions_phase,
        sum(nb_dossiers_distincts) as nb_dossiers_phase,
        avg(duree_moyenne_minutes) as duree_moyenne_phase_minutes,
        sum(temps_total_minutes) as temps_total_phase_minutes
        
    from stats_par_phase
    group by phase_id, phase_libelle, categorie_phase
),

-- =====================================================
-- SECTION 4: Calcul des indicateurs de goulot
-- =====================================================
goulots as (
    select
        s.*,
        g.moyenne_globale_minutes,
        g.mediane_globale_minutes,
        g.temps_total_workflow,
        
        -- Ratio vs moyenne globale
        case 
            when g.moyenne_globale_minutes > 0 
            then s.duree_moyenne_minutes / g.moyenne_globale_minutes 
            else 0 
        end as ratio_vs_moyenne_globale,
        
        -- Ratio vs médiane globale
        case 
            when g.mediane_globale_minutes > 0 
            then s.duree_moyenne_minutes / g.mediane_globale_minutes 
            else 0 
        end as ratio_vs_mediane_globale,
        
        -- Pourcentage du temps total
        case 
            when g.temps_total_workflow > 0 
            then (s.temps_total_minutes / g.temps_total_workflow) * 100 
            else 0 
        end as pct_temps_total_workflow,
        
        -- Coefficient de variation (variabilité)
        case 
            when s.duree_moyenne_minutes > 0 
            then (s.ecart_type_minutes / s.duree_moyenne_minutes) * 100 
            else 0 
        end as coefficient_variation_pct,
        
        -- Indice de dispersion P90
        case 
            when s.mediane_minutes > 0 
            then s.p90_minutes / s.mediane_minutes 
            else 0 
        end as indice_dispersion_p90,
        
        -- Taux de rejet
        case 
            when s.nb_occurrences > 0 
            then (s.nb_rejets::float / s.nb_occurrences) * 100 
            else 0 
        end as taux_rejet_pct,
        
        -- Taux de correction
        case 
            when s.nb_occurrences > 0 
            then (s.nb_corrections::float / s.nb_occurrences) * 100 
            else 0 
        end as taux_correction_pct
        
    from stats_par_phase s
    cross join stats_globales g
),

-- =====================================================
-- SECTION 5: Classification et recommandations
-- =====================================================
final as (
    select
        -- Identification
        row_number() over (order by g.ordre_workflow, g.action) as phase_etape_id,
        g.action,
        g.phase_id,
        g.phase_libelle,
        g.action_libelle,
        g.categorie_phase,
        g.responsable_type,
        g.ordre_workflow,
        
        -- Caractéristiques
        g.est_etape_principale,
        g.est_etape_validation,
        g.est_etape_rejet,
        
        -- Volume
        g.nb_occurrences,
        g.nb_dossiers_distincts,
        g.nb_agents_impliques,
        g.nb_roles_distincts,
        
        -- Temps de traitement
        round(g.duree_moyenne_minutes::numeric, 2) as duree_moyenne_minutes,
        round(g.duree_moyenne_heures::numeric, 2) as duree_moyenne_heures,
        round(g.duree_moyenne_jours::numeric, 4) as duree_moyenne_jours,
        round(g.mediane_minutes::numeric, 2) as mediane_minutes,
        round(g.ecart_type_minutes::numeric, 2) as ecart_type_minutes,
        round(g.min_minutes::numeric, 2) as min_minutes,
        round(g.max_minutes::numeric, 2) as max_minutes,
        round(g.p75_minutes::numeric, 2) as p75_minutes,
        round(g.p90_minutes::numeric, 2) as p90_minutes,
        round(g.p95_minutes::numeric, 2) as p95_minutes,
        round(g.temps_total_minutes::numeric, 2) as temps_total_minutes,
        round(g.temps_total_heures::numeric, 2) as temps_total_heures,
        
        -- Indicateurs spécifiques
        g.nb_validations,
        g.nb_rejets,
        g.nb_corrections,
        g.nb_clotures,
        round(g.taux_rejet_pct::numeric, 2) as taux_rejet_pct,
        round(g.taux_correction_pct::numeric, 2) as taux_correction_pct,
        
        -- Indicateurs de goulot
        round(g.ratio_vs_moyenne_globale::numeric, 2) as ratio_vs_moyenne_globale,
        round(g.ratio_vs_mediane_globale::numeric, 2) as ratio_vs_mediane_globale,
        round(g.pct_temps_total_workflow::numeric, 2) as pct_temps_total_workflow,
        round(g.coefficient_variation_pct::numeric, 2) as coefficient_variation_pct,
        round(g.indice_dispersion_p90::numeric, 2) as indice_dispersion_p90,
        
        -- Score composite de goulot (0-100)
        round((
            (case when g.ratio_vs_moyenne_globale > 2 then 30 
                  when g.ratio_vs_moyenne_globale > 1.5 then 20 
                  when g.ratio_vs_moyenne_globale > 1 then 10 
                  else 0 end) +
            (case when g.pct_temps_total_workflow > 30 then 30 
                  when g.pct_temps_total_workflow > 20 then 20 
                  when g.pct_temps_total_workflow > 10 then 10 
                  else 0 end) +
            (case when g.coefficient_variation_pct > 100 then 20 
                  when g.coefficient_variation_pct > 50 then 10 
                  else 0 end) +
            (case when g.indice_dispersion_p90 > 3 then 20 
                  when g.indice_dispersion_p90 > 2 then 10 
                  else 0 end)
        )::numeric, 2) as score_goulot,
        
        -- Classification du niveau de goulot
        case 
            when (
                (case when g.ratio_vs_moyenne_globale > 2 then 30 else 0 end) +
                (case when g.pct_temps_total_workflow > 30 then 30 else 0 end) +
                (case when g.coefficient_variation_pct > 100 then 20 else 0 end) +
                (case when g.indice_dispersion_p90 > 3 then 20 else 0 end)
            ) >= 60 then 'CRITIQUE'
            when (
                (case when g.ratio_vs_moyenne_globale > 1.5 then 20 else 0 end) +
                (case when g.pct_temps_total_workflow > 20 then 20 else 0 end) +
                (case when g.coefficient_variation_pct > 50 then 10 else 0 end) +
                (case when g.indice_dispersion_p90 > 2 then 10 else 0 end)
            ) >= 40 then 'MAJEUR'
            when g.ratio_vs_moyenne_globale > 1 or g.pct_temps_total_workflow > 10 then 'MODERE'
            else 'NORMAL'
        end as niveau_goulot,
        
        -- Est un goulot d'étranglement
        case 
            when g.ratio_vs_moyenne_globale > 1.5 or g.pct_temps_total_workflow > 20 then true
            else false
        end as est_goulot_etranglement,
        
        -- Recommandation automatique
        case 
            when (
                (case when g.ratio_vs_moyenne_globale > 2 then 30 else 0 end) +
                (case when g.pct_temps_total_workflow > 30 then 30 else 0 end)
            ) >= 50 then 'URGENT: Revoir le processus - Phase ' || g.phase_libelle || ' monopolise ' || round(g.pct_temps_total_workflow::numeric, 1) || '% du temps'
            when g.coefficient_variation_pct > 100 then 'Forte variabilité: Standardiser le traitement pour ' || g.action_libelle
            when g.taux_rejet_pct > 20 then 'Taux de rejet élevé (' || round(g.taux_rejet_pct::numeric, 1) || '%): Améliorer la qualité amont'
            when g.taux_correction_pct > 30 then 'Nombreuses corrections (' || round(g.taux_correction_pct::numeric, 1) || '%): Former les opérateurs'
            when g.indice_dispersion_p90 > 3 then 'Investiguer les cas extrêmes (P90 = ' || round(g.p90_minutes::numeric, 0) || ' min)'
            when g.ratio_vs_moyenne_globale > 1 then 'Surveiller cette étape - légèrement au-dessus de la moyenne'
            else 'Performance normale - maintenir le niveau actuel'
        end as recommandation,
        
        -- Priorité d'action
        case 
            when g.ratio_vs_moyenne_globale > 2 and g.pct_temps_total_workflow > 20 then 1
            when g.ratio_vs_moyenne_globale > 1.5 or g.pct_temps_total_workflow > 15 then 2
            when g.coefficient_variation_pct > 100 or g.taux_rejet_pct > 20 then 3
            else 4
        end as priorite_action,
        
        -- Gain potentiel (si ramené à la moyenne)
        round(greatest(0, g.temps_total_minutes - (g.nb_occurrences * g.moyenne_globale_minutes))::numeric, 0) as gain_potentiel_minutes,
        round(greatest(0, g.temps_total_minutes - (g.nb_occurrences * g.moyenne_globale_minutes))::numeric / 60, 1) as gain_potentiel_heures,
        
        -- Metadata
        current_timestamp as dbt_created_at
        
    from goulots g
)

select * from final
order by priorite_action, score_goulot desc