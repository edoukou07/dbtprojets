{{ config(
    materialized='view',
    schema='staging'
) }}

-- Staging: Ayants-Droits
-- Extract et validation des données d'ayants-droits
-- Source: ayants_droits table
-- Grain: Une ligne par ayant-droit

with raw_ayants_droits as (
    select
        id,
        type_droit_id,
        civilite,
        nom,
        prenom,
        telephone,
        type_piece,
        numero_piece,
        description_droit,
        date_evaluation,
        montant_evalue,
        statut,
        created_at,
        updated_at
    from {{ source('sigeti_source', 'ayants_droits') }}
),

validated as (
    select
        -- Natural keys
        id as ayant_droit_id,
        
        -- Attributes
        civilite,
        trim(nom) as nom_ayant_droit,
        trim(prenom) as prenom_ayant_droit,
        telephone,
        type_droit_id,
        type_piece,
        numero_piece,
        description_droit,
        
        -- Statuses
        statut,
        
        -- Financial
        montant_evalue,
        
        -- Dates
        date_evaluation,
        
        -- Audit
        created_at,
        updated_at,
        current_timestamp as dbt_extracted_at
    
    from raw_ayants_droits
    where id is not null
)

select * from validated
