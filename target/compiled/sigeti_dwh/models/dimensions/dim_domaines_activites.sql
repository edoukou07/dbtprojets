

with source as (
    select * from "sigeti_node_db"."dwh_staging"."stg_domaines_activites"
),

domaines_enrichis as (
    select
        -- Clé surrogate
        md5(cast(coalesce(cast(id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as domaine_key,
        
        -- Clés naturelles
        id as domaine_id,
        
        -- Attributs
        libelle as nom_domaine,
        description,
        
        -- Métadonnées
        created_at,
        updated_at
        
    from source
)

select * from domaines_enrichis