

with source as (
    select * from "sigeti_node_db"."dwh_staging"."stg_zones_industrielles"
),

zones_enrichies as (
    select
        -- Clé surrogate
        md5(cast(coalesce(cast(id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as zone_key,
        
        -- Clés naturelles
        id as zone_id,
        
        -- Attributs
        libelle as nom_zone,
        description,
        
        -- Métadonnées
        created_at,
        updated_at
        
    from source
)

select * from zones_enrichies