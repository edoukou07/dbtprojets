{{ config(
    materialized='table',
    schema='dimensions',
    unique_key='agent_key',
    on_schema_change='fail',
    tags=['rh']
) }}

-- Dimension: Agents
-- Agents information dimension
-- Source: stg_agents

with raw_agents as (
    select * from {{ ref('stg_agents') }}
),

with_keys as (
    select
        {{ dbt_utils.generate_surrogate_key(['agent_id']) }} as agent_key,
        agent_id,
        matricule,
        trim(nom_agent) as nom_agent,
        trim(prenom_agent) as prenom_agent,
        nom_complet,
        email,
        telephone,
        type_agent_id,
        est_actif,
        est_employe_actif,
        created_at,
        updated_at,
        deleted_at,
        current_timestamp as dbt_extracted_at
    from raw_agents
)

select * from with_keys
