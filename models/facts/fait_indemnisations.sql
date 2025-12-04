{{ config(
    materialized='incremental',
    schema='facts',
    unique_key='indemnisation_id',
    on_schema_change='ignore',
    full_refresh=false,
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
        recevabilite_decision,
        
        -- Montants
        montant_restant,
        
        -- Indicateurs booléens
        est_acceptee,
        est_payee,
        est_evaluee,
        est_rejetee,
        
        -- Délai d'évaluation
        delai_evaluation_jours,
        
        -- Dates
        date_creation,
        date_recevabilite,
        
        -- Lineage
        updated_at,
        dbt_extracted_at,
        current_timestamp as dbt_loaded_at
    
    from stg
)

select * from enriched
