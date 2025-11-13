

with source as (
    select * from "sigeti_node_db"."dwh_staging"."stg_entreprises"
),

entreprises_enrichies as (
    select
        -- Clé surrogate
        md5(cast(coalesce(cast(id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as entreprise_key,
        
        -- Clés naturelles
        id as entreprise_id,
        
        -- Attributs
        raison_sociale,
        telephone,
        email,
        registre_commerce,
        compte_contribuable,
        forme_juridique,
        adresse,
        date_constitution,
        
        -- Clés étrangères
        domaine_activite_id,
        user_id as representant_user_id,
        
        -- Métadonnées SCD Type 2
        date_creation as valid_from,
        date_modification as valid_to,
        case 
            when date_modification is null then true 
            else false 
        end as is_current
        
    from source
)

select * from entreprises_enrichies