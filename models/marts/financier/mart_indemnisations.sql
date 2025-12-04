{{ config(
    materialized='table',
    schema='marts_financier',
    indexes=[
        {'columns': ['zone_id']},
        {'columns': ['annee_mois']}
    ],
    tags=['compliance', 'P2'],
    enabled=true
) }}

-- Data Mart: Indemnisations
-- KPIs de suivi des indemnisations par zone et statut
-- Refresh: Quotidien
-- Utilisateurs: Compliance, Métier indemnisations

with indemnisations as (
    select * from {{ ref('fait_indemnisations') }}
),

zones as (
    select 
        zone_id,
        nom_zone
    from {{ ref('dim_zones_industrielles') }}
),

aggregated as (
    select
        coalesce(z.nom_zone, 'Zone Inconnue') as zone_name,
        coalesce(i.zone_id, 0) as zone_id,
        extract(year from i.date_creation) as annee,
        extract(month from i.date_creation) as mois,
        to_char(i.date_creation, 'YYYY-MM') as annee_mois,
        
        i.statut,
        
        -- Volumes
        count(*) as nombre_indemnisations,
        count(distinct i.beneficiaire_id) as nombre_beneficiaires,
        
        -- Montants
        round(sum(i.montant_restant)::numeric, 2) as montant_total_restant,
        round(avg(i.montant_restant)::numeric, 2) as montant_moyen,
        
        current_timestamp as dbt_updated_at
    
    from indemnisations i
    left join zones z on i.zone_id = z.zone_id
    group by z.nom_zone, i.zone_id, annee, mois, annee_mois, i.statut
)

select * from aggregated

