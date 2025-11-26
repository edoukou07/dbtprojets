{{ config(
    materialized='table',
    schema='marts_operationnel',
    indexes=[
        {'columns': ['zone_id']},
        {'columns': ['annee']}
    ],
    tags=['socio_eco', 'P2'],
    enabled=false
) }}

-- Data Mart: Emplois Créés
-- KPIs d'emplois créés par zone et catégorie
-- Refresh: Mensuel
-- Utilisateurs: Métier socio-économique, Management

with emplois as (
    select * from {{ ref('fait_emplois_crees') }}
),

zones as (
    select * from {{ ref('dim_zones_industrielles') }}
),

aggregated as (
    select
        z.zone_name,
        e.zone_id,
        e.annee,
        e.emploi_category,
        e.emploi_sector,
        
        -- Volumes totaux
        sum(e.total_emplois) as total_emplois,
        sum(e.total_expatries) as total_expatries,
        sum(e.total_nationaux) as total_nationaux,
        sum(e.total_cadres) as total_cadres,
        
        -- Nombre de demandes
        sum(e.nombre_demandes) as nombre_demandes,
        
        -- Ratios
        round(sum(e.total_expatries)::numeric / nullif(sum(e.total_emplois), 0) * 100, 2) as pct_expatries,
        round(sum(e.total_nationaux)::numeric / nullif(sum(e.total_emplois), 0) * 100, 2) as pct_nationaux,
        round(sum(e.total_cadres)::numeric / nullif(sum(e.total_emplois), 0) * 100, 2) as pct_cadres,
        
        -- Moyennes
        round(avg(e.avg_expatries_par_demande), 2) as avg_expatries_par_demande,
        round(avg(e.avg_nationaux_par_demande), 2) as avg_nationaux_par_demande,
        
        current_timestamp as dbt_updated_at
    
    from emplois e
    left join zones z on e.zone_id = z.zone_id
    group by z.zone_name, e.zone_id, e.annee, e.emploi_category, e.emploi_sector
)

select * from aggregated

