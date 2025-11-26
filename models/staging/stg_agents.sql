{{ config(
    materialized='view',
    schema='staging'
) }}

-- Staging: Agents
-- Extract and validation of agents data
-- Source: agents table
-- Grain: One row per agent

with raw_agents as (
    select
        id,
        nom,
        prenoms,
        matricule,
        telephone,
        email,
        type_agent_id,
        actif,
        created_at,
        updated_at,
        deleted_at
    from {{ source('sigeti_source', 'agents') }}
),

validated as (
    select
        -- Natural keys
        id as agent_id,
        matricule,
        email,
        
        -- Attributes
        trim(nom) as nom_agent,
        trim(prenoms) as prenom_agent,
        (trim(nom) || ' ' || trim(prenoms))::text as nom_complet,
        type_agent_id,
        
        -- Contact
        telephone,
        
        -- Indicators
        case when deleted_at is null then 1 else 0 end as est_actif,
        case when actif = true then 1 else 0 end as est_employe_actif,
        
        -- Audit
        created_at,
        updated_at,
        deleted_at,
        current_timestamp as dbt_extracted_at
    
    from raw_agents
    where id is not null
)

select * from validated
