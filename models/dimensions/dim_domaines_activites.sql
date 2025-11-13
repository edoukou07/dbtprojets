{{
    config(
        materialized='table',
        unique_key='domaine_key'
    )
}}

with source as (
    select * from {{ ref('stg_domaines_activites') }}
),

domaines_enrichis as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['id']) }} as domaine_key,
        
        -- Clés naturelles
        id as domaine_id,
        
        -- Attributs
        libelle as nom_domaine,
        description,
        
        -- Métadonnées
        created_at,
        updated_at
        
    from source
)

select * from domaines_enrichis
