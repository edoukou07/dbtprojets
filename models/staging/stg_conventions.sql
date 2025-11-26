{{ config(
    materialized='view',
    schema='staging'
) }}

-- Staging: Conventions
-- Extract et validation des conventions
-- Source: conventions table
-- Grain: Une ligne par convention

with raw_conventions as (
    select
        id,
        numero_convention,
        nom,
        prenom,
        email,
        telephone,
        profession,
        adresse_personnelle,
        raison_sociale,
        forme_juridique,
        registre_commerce,
        statut,
        etape_actuelle,
        cree_par,
        date_creation,
        date_modification
    from {{ source('sigeti_source', 'conventions') }}
),

validated as (
    select
        -- Natural keys
        id as convention_id,
        numero_convention,
        
        -- Attributes
        trim(nom) as nom_convention,
        trim(prenom) as prenom_convention,
        email,
        telephone,
        profession,
        adresse_personnelle,
        raison_sociale,
        forme_juridique,
        registre_commerce,
        
        -- Status
        statut,
        etape_actuelle,
        cree_par,
        
        -- Audit
        date_creation,
        date_modification,
        current_timestamp as dbt_extracted_at
    
    from raw_conventions
    where id is not null
)

select * from validated
