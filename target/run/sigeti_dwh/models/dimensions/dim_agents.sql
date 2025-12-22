
  
    

  create  table "sigeti_node_db"."dwh_dimensions"."dim_agents__dbt_tmp"
  
  
    as
  
  (
    

-- Dimension: Agents
-- Agents information dimension
-- Source: stg_agents

with raw_agents as (
    select * from "sigeti_node_db"."dwh_staging"."stg_agents"
),

with_keys as (
    select
        md5(cast(coalesce(cast(agent_id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as agent_key,
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
  );
  