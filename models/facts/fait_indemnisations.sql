{{ config(
    materialized='incremental',
    schema='facts',
    unique_key='indemnisation_id',
    on_schema_change='append_new_columns',
    tags=['compliance', 'P2']
) }}

-- Fact Table: Indemnisations
-- Suivi des indemnisations
-- Grain: Une ligne par indemnisation
-- Update strategy: Incremental par date de création

with stg as (
    select * from {{ ref('stg_indemnisations') }}
    {% if execute %}
        where dbt_extracted_at >= '{{ var("incremental_since", "2020-01-01") }}'
    {% endif %}
),

enriched as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['indemnisation_id']) }} as indemnisation_key,
        
        -- Clés naturelles
        indemnisation_id,
        beneficiaire_id,
        zone_id,
        
        -- Statut et motif
        statut,
        motif_indemnisation,
        
        -- Montants
        montant_restant,
        
        -- Dates
        date_creation,
        
        -- Lineage
        updated_at,
        dbt_extracted_at,
        current_timestamp as dbt_loaded_at
    
    from stg
)

select * from enriched
