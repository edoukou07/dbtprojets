{{ config(
    materialized='table',
    schema='marts_operationnel',
    indexes=[
        {'columns': ['zone_id']},
        {'columns': ['annee_mois']}
    ],
    tags=['operationnel', 'P1'],
    enabled=false
) }}

-- Data Mart: Suivi Implantation
-- KPIs de suivi d'implantation par zone
-- Refresh: Temps réel
-- Utilisateurs: Project managers, Opérationnels

with implantations as (
    select * from {{ ref('fait_implantations') }}
),

zones as (
    select * from {{ ref('dim_zones_industrielles') }}
),

aggregated as (
    select
        z.zone_name,
        z.zone_id,
        extract(year from i.date_debut) as annee,
        extract(month from i.date_debut) as mois,
        to_char(i.date_debut, 'YYYY-MM') as annee_mois,
        
        -- Volumes
        count(*) as nombre_sites,
        count(distinct i.implantation_id) as nombre_sites_distincts,
        
        -- Statuts
        count(case when i.statut = 'TERMINE' then 1 end) as nombre_sites_termines,
        count(case when i.statut = 'EN_COURS' then 1 end) as nombre_sites_en_cours,
        count(case when i.statut = 'RETARD' then 1 end) as nombre_sites_en_retard,
        count(case when i.statut = 'BLOQUE' then 1 end) as nombre_sites_bloques,
        
        -- Taux
        round(count(case when i.statut = 'TERMINE' then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as pct_sites_termines,
        
        round(count(case when i.statut = 'RETARD' then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as pct_sites_en_retard,
        
        round(count(case when i.est_complete = 1 then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as pct_sites_complets,
        
        -- Délais
        avg(i.duree_reelle_jours) as duree_moyenne_reelle_jours,
        avg(i.duree_prevue_jours) as duree_moyenne_prevue_jours,
        avg(i.jours_de_retard) as retard_moyen_jours,
        max(i.jours_de_retard) as retard_max_jours,
        
        -- Variance planning
        round(avg(i.duree_reelle_jours - i.duree_prevue_jours), 2) as variance_planning_jours,
        
        current_timestamp as dbt_updated_at
    
    from implantations i
    left join zones z on i.implantation_id = z.zone_id
    group by z.zone_name, z.zone_id, annee, mois, annee_mois
)

select * from aggregated

