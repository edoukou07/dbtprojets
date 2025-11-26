{{ config(
    materialized='table',
    schema='dimensions',
    unique_key='type_infraction_key',
    on_schema_change='fail',
    tags=['conformite'],
    enabled=false
) }}

-- Dimension: Types d'Infractions
-- Slowly Changing Dimension Type 2
-- Historique des types d'infractions avec versioning

with raw_types as (
    select distinct
        type as type_infraction,
        gravite
    from {{ ref('stg_infractions') }}
    where type is not null
),

with_keys as (
    select
        {{ dbt_utils.generate_surrogate_key(['type', 'gravite']) }} as type_infraction_key,
        type as type_infraction,
        gravite,
        true as est_actif,
        current_timestamp as dbt_valid_from,
        null::timestamp as dbt_valid_to,
        current_timestamp as dbt_created_at,
        current_timestamp as dbt_updated_at
    from raw_types
)

select * from with_keys
