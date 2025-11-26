
  
    

  create  table "sigeti_node_db"."dwh_dimensions"."dim_convention_stages__dbt_tmp"
  
  
    as
  
  (
    

-- Dimension: Étapes de Conventions
-- Slowly Changing Dimension Type 2
-- Historique des étapes de validation des conventions

with stages as (
    select 
        1 as stage_order,
        'DPP_ANALYSIS' as stage_code,
        'Analyse DPP' as stage_name,
        'En attente analyse DPP' as stage_description,
        true as est_actif
    union all
    select 2, 'RECEVABILITY_CHECK', 'Vérification Recevabilité', 'En attente vérification recevabilité', true
    union all
    select 3, 'MARKETING_REVIEW', 'Analyse Marketing', 'En attente analyse marketing', true
    union all
    select 4, 'DG_VALIDATION', 'Validation DG', 'En attente validation direction générale', true
    union all
    select 5, 'APPROVED', 'Approuvée', 'Convention approuvée', true
),

with_keys as (
    select
        md5(cast(coalesce(cast(stage_code as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as stage_key,
        stage_order,
        stage_code,
        stage_name,
        stage_description,
        est_actif,
        current_timestamp as dbt_valid_from,
        null::timestamp as dbt_valid_to,
        current_timestamp as dbt_created_at,
        current_timestamp as dbt_updated_at
    from stages
)

select * from with_keys
  );
  