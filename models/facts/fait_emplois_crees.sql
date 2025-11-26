{{ config(
    materialized='table',
    schema='facts',
    tags=['socio_eco', 'P2']
) }}

-- Fact Table: Emplois Créés
-- Snapshot des emplois créés par zone
-- Grain: Ligne par zone, demande, année
-- Update strategy: Full refresh

with stg as (
    select * from {{ ref('stg_emplois_crees') }}
),

aggregated as (
    select
        -- Clés naturelles
        demande_id,
        zone_id,
        type_demande,
        statut,
        
        -- Agrégations
        count(*) as nombre_demandes,
        sum(nombre_emplois_total) as total_emplois,
        sum(emplois_nationaux) as total_emplois_nationaux,
        sum(emplois_expatries) as total_emplois_expatries,
        
        -- Statistiques
        avg(nombre_emplois_total)::numeric as avg_emplois_par_demande,
        
        -- Dates
        min(created_at) as date_premiere_creation,
        max(updated_at) as date_derniere_maj,
        current_timestamp as dbt_processed_at
    
    from stg
    group by demande_id, zone_id, type_demande, statut
),

with_keys as (
    select
        {{ dbt_utils.generate_surrogate_key(['zone_id', 'demande_id']) }} as emplois_key,
        *
    from aggregated
)

select * from with_keys
