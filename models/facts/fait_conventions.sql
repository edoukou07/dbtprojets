{{ config(
    materialized='incremental',
    schema='facts',
    unique_key='convention_id',
    on_schema_change='append_new_columns',
    tags=['compliance', 'P1']
) }}

-- Fact Table: Conventions
-- État et progression des conventions
-- Grain: Une ligne par convention
-- Update strategy: Incremental par date de création

with stg as (
    select * from {{ ref('stg_conventions') }}
    {% if execute %}
        where dbt_extracted_at >= '{{ var("incremental_since", "2020-01-01") }}'
    {% endif %}
),

enriched as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['convention_id']) }} as convention_key,
        
        -- Clés naturelles
        convention_id,
        numero_convention,
        
        -- Contact Info
        nom_convention,
        prenom_convention,
        email,
        telephone,
        profession,
        
        -- Business Info
        raison_sociale,
        forme_juridique,
        registre_commerce,
        
        -- Address
        adresse_personnelle,
        
        -- Statuts
        statut,
        etape_actuelle,
        cree_par,
        
        -- Dates
        date_creation,
        date_modification,
        
        -- Lineage
        dbt_extracted_at,
        current_timestamp as dbt_loaded_at
    
    from stg
)

select * from enriched
