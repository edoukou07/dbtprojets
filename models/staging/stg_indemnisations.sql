{{ config(
    materialized='view',
    schema='staging'
) }}

-- Staging: Indemnisations
-- Extract et validation des données d'indemnisations
-- Source: indemnisations table
-- Grain: Une ligne par indemnisation

with raw_indemnisations as (
    select
        id,
        detenteur_id,
        montant_restant,
        motif_indemnisation,
        statut,
        date_creation,
        zone_id,
        updated_at
    from {{ source('sigeti_source', 'indemnisations') }}
),

validated as (
    select
        -- Natural keys
        id as indemnisation_id,
        detenteur_id as beneficiaire_id,
        zone_id,
        
        -- Attributes
        montant_restant,
        motif_indemnisation,
        statut,
        
        -- Dates
        date_creation,
        updated_at,
        
        -- Audit
        current_timestamp as dbt_extracted_at
    
    from raw_indemnisations
    where id is not null
)

select * from validated
