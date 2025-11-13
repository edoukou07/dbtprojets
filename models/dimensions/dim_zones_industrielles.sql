{{
    config(
        materialized='table',
        unique_key='zone_key'
    )
}}

with source as (
    select * from {{ ref('stg_zones_industrielles') }}
),

zones_enrichies as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['id']) }} as zone_key,
        
        -- Clés naturelles
        id as zone_id,
        
        -- Attributs
        libelle as nom_zone,
        description,
        
        -- Métadonnées
        created_at,
        updated_at
        
    from source
)

select * from zones_enrichies
