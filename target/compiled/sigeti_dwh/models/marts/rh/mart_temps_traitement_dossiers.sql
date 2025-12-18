

/*
    ================================================================
    Mart: Temps de Traitement des Dossiers et Goulots d'Étranglement
    ================================================================
    
    ARCHITECTURE: Star Schema (Kimball)
    -----------------------------------
    Sources:
    - fait_traitements (table de faits)
    - dim_etapes (dimension)
    - dim_temps (dimension)
    
    Objectifs métier:
    - Identifier les étapes les plus longues du workflow
    - Détecter les goulots d'étranglement
    - Calculer les gains potentiels d'optimisation
    - Fournir des recommandations automatisées
    
    Indicateurs clés: 12 indicateurs de goulot d'étranglement
    Classification: CRITIQUE / MAJEUR / MODERE / NORMAL
    
    Refresh: Quotidien
    Utilisateurs: Direction, Managers, Amélioration Continue
*/

-- =====================================================
-- SECTION 1: Agrégation depuis la table de faits
-- =====================================================
with stats_par_etape as (
    select
        -- Clés et attributs de dimension
        f.etape_key,
        f.action,
        e.action_libelle,
        e.categorie_etape,
        e.responsable_type,
        e.etape_source,
        e.etape_destination,
        e.ordre_workflow,
        e.est_etape_critique,
        
        -- Volume
        count(*) as nb_occurrences,
        count(distinct f.dossier_id) as nb_dossiers_distincts,
        count(distinct f.agent_id) as nb_agents_impliques,
        
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
        sum(f.duree_heures) as temps_total_heures
        
    from "sigeti_node_db"."dwh_facts"."fait_traitements" f
    inner join "sigeti_node_db"."dwh_dimensions"."dim_etapes" e on f.etape_key = e.etape_key
    where f.duree_minutes is not null
      and f.duree_minutes > 0
    group by 
        f.etape_key, f.action, e.action_libelle, e.categorie_etape,
        e.responsable_type, e.etape_source, e.etape_destination,
        e.ordre_workflow, e.est_etape_critique
),

-- =====================================================
-- SECTION 2: Statistiques globales du workflow
-- =====================================================

-- =====================================================
-- SECTION 3: Calcul des indicateurs de goulot d'étranglement
-- =====================================================
stats_globales as (
    select
        avg(duree_moyenne_minutes) as moyenne_globale_minutes,
        percentile_cont(0.5) within group (order by duree_moyenne_minutes) as mediane_globale_minutes,
        stddev(duree_moyenne_minutes) as ecart_type_global,
        sum(temps_total_minutes) as temps_total_workflow
    from stats_par_etape
),

goulots as (
    select
        s.*,
        g.moyenne_globale_minutes,
        g.mediane_globale_minutes,
        g.temps_total_workflow,
        
        -- =====================================================
        -- INDICATEURS DE GOULOT D'ÉTRANGLEMENT
        -- =====================================================
        
        -- 1. Ratio vs moyenne globale (>2 = goulot potentiel)
        round((s.duree_moyenne_minutes / nullif(g.moyenne_globale_minutes, 0))::numeric, 2) as ratio_vs_moyenne_globale,
        
        -- 2. Ratio vs médiane globale (plus robuste)
        round((s.duree_moyenne_minutes / nullif(g.mediane_globale_minutes, 0))::numeric, 2) as ratio_vs_mediane_globale,
        
        -- 3. Part du temps total (% du workflow)
        round((s.temps_total_minutes / nullif(g.temps_total_workflow, 0) * 100)::numeric, 2) as pct_temps_total_workflow,
        
        -- 4. Coefficient de variation (variabilité/prévisibilité)
        -- CV > 100% = très variable = problème de process
        round((s.ecart_type_minutes / nullif(s.duree_moyenne_minutes, 0) * 100)::numeric, 2) as coefficient_variation_pct,
        
        -- 5. Indice de dispersion P90/Médiane
        -- >3 = forte dispersion = processus instable
        round((s.p90_minutes / nullif(s.mediane_minutes, 0))::numeric, 2) as indice_dispersion_p90,
        
        -- 6. Score de goulot (composite 0-100)
        round((
            -- Poids: 40% ratio temps, 30% part workflow, 30% variabilité
            (least(s.duree_moyenne_minutes / nullif(g.moyenne_globale_minutes, 0), 10) / 10 * 40) +
            (least(s.temps_total_minutes / nullif(g.temps_total_workflow, 0) * 100, 50) / 50 * 30) +
            (least(s.ecart_type_minutes / nullif(s.duree_moyenne_minutes, 0), 2) / 2 * 30)
        )::numeric, 2) as score_goulot,
        
        -- 7. Classification du goulot
        case
            when s.duree_moyenne_minutes / nullif(g.moyenne_globale_minutes, 0) > 3 
                 and s.temps_total_minutes / nullif(g.temps_total_workflow, 0) > 0.15 then 'CRITIQUE'
            when s.duree_moyenne_minutes / nullif(g.moyenne_globale_minutes, 0) > 2 
                 or s.temps_total_minutes / nullif(g.temps_total_workflow, 0) > 0.10 then 'MAJEUR'
            when s.duree_moyenne_minutes / nullif(g.moyenne_globale_minutes, 0) > 1.5 then 'MODERE'
            else 'NORMAL'
        end as niveau_goulot,
        
        -- 8. Flag binaire goulot
        case
            when s.duree_moyenne_minutes / nullif(g.moyenne_globale_minutes, 0) > 2 
                 or s.temps_total_minutes / nullif(g.temps_total_workflow, 0) > 0.10 then true
            else false
        end as est_goulot_etranglement,
        
        -- 9. Impact estimé si optimisé de 50%
        round((s.temps_total_minutes * 0.5)::numeric, 2) as gain_potentiel_minutes,
        round((s.temps_total_minutes * 0.5 / 60)::numeric, 2) as gain_potentiel_heures,
        
        -- 10. Rang par temps moyen
        row_number() over (order by s.duree_moyenne_minutes desc) as rang_duree_moyenne,
        
        -- 11. Rang par temps total
        row_number() over (order by s.temps_total_minutes desc) as rang_temps_total,
        
        -- 12. Rang par variabilité
        row_number() over (order by s.ecart_type_minutes desc nulls last) as rang_variabilite
        
    from stats_par_etape s
    cross join stats_globales g
),

-- =====================================================
-- SECTION 4: Résultat final enrichi
-- =====================================================
final as (
    select
        row_number() over (order by score_goulot desc nulls last) as etape_id,
        
        -- Clés dimensions
        etape_key,
        action,
        action_libelle,
        categorie_etape,
        responsable_type,
        ordre_workflow,
        est_etape_critique,
        
        -- Identification étapes
        etape_source,
        etape_destination,
        
        -- Volume
        nb_occurrences,
        nb_dossiers_distincts,
        nb_agents_impliques,
        
        -- Temps de traitement
        round(duree_moyenne_minutes::numeric, 2) as duree_moyenne_minutes,
        round(duree_moyenne_heures::numeric, 2) as duree_moyenne_heures,
        round(duree_moyenne_jours::numeric, 4) as duree_moyenne_jours,
        round(mediane_minutes::numeric, 2) as mediane_minutes,
        round(ecart_type_minutes::numeric, 2) as ecart_type_minutes,
        
        -- Distribution
        round(min_minutes::numeric, 2) as min_minutes,
        round(p75_minutes::numeric, 2) as p75_minutes,
        round(p90_minutes::numeric, 2) as p90_minutes,
        round(p95_minutes::numeric, 2) as p95_minutes,
        round(max_minutes::numeric, 2) as max_minutes,
        
        -- Totaux
        round(temps_total_minutes::numeric, 2) as temps_total_minutes,
        round(temps_total_heures::numeric, 2) as temps_total_heures,
        
        -- Indicateurs goulot d'étranglement
        ratio_vs_moyenne_globale,
        ratio_vs_mediane_globale,
        pct_temps_total_workflow,
        coefficient_variation_pct,
        indice_dispersion_p90,
        score_goulot,
        niveau_goulot,
        est_goulot_etranglement,
        gain_potentiel_minutes,
        gain_potentiel_heures,
        
        -- Rankings
        rang_duree_moyenne,
        rang_temps_total,
        rang_variabilite,
        
        -- Recommandations automatiques
        case
            when niveau_goulot = 'CRITIQUE' then 'URGENT: Revoir le processus, automatiser ou ajouter des ressources'
            when niveau_goulot = 'MAJEUR' and coefficient_variation_pct > 100 then 'Standardiser le processus - forte variabilité détectée'
            when niveau_goulot = 'MAJEUR' then 'Analyser les causes racines et optimiser'
            when coefficient_variation_pct > 150 then 'Investiguer les cas extrêmes (>P90)'
            when niveau_goulot = 'MODERE' then 'Surveiller et documenter les bonnes pratiques'
            else 'Processus nominal'
        end as recommandation,
        
        -- Métadonnées
        current_timestamp as dbt_updated_at
        
    from goulots
)

select * from final
order by score_goulot desc nulls last