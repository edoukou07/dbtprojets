{{
    config(
        materialized='table',
        unique_key='entreprise_key'
    )
}}

with source as (
    select * from {{ ref('stg_entreprises') }}
),

entreprises_enrichies as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['id']) }} as entreprise_key,
        
        -- Clés naturelles
        id as entreprise_id,
        
        -- Attributs
        raison_sociale,
        telephone,
        email,
        registre_commerce,
        compte_contribuable,
        forme_juridique,
        adresse,
        date_constitution,
        
        -- Clés étrangères
        domaine_activite_id,
        user_id as representant_user_id,
        
        -- Métadonnées SCD Type 2
        date_creation as valid_from,
        date_modification as valid_to,
        case 
            when date_modification is null then true 
            else false 
        end as is_current
        
    from source
)

select * from entreprises_enrichies
