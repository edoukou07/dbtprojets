
  create view "sigeti_node_db"."dwh_staging"."stg_emplois_crees__dbt_tmp"
    
    
  as (
    

-- Staging: Emplois Créés
-- Extract and JSON parsing of jobs created
-- Source: demandes_attribution table (JSONB emplois field)
-- Grain: One row per employment in a demand

with raw_demandes as (
    select
        id,
        zone_id,
        lot_id,
        emplois,
        type_demande,
        statut,
        created_at,
        updated_at
    from "sigeti_node_db"."public"."demandes_attribution"
    where emplois is not null
),

validated as (
    select
        id as demande_id,
        zone_id,
        lot_id,
        type_demande,
        (emplois->>'total')::integer as nombre_emplois_total,
        ((emplois->'nationaux')->>'total')::integer as emplois_nationaux,
        ((emplois->'expatries')->>'total')::integer as emplois_expatries,
        statut,
        created_at,
        updated_at,
        current_timestamp as dbt_extracted_at
    
    from raw_demandes
    where id is not null
)

select * from validated
  );