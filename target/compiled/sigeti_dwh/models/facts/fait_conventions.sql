

-- Fact Table: Conventions
-- État et progression des conventions
-- Grain: Une ligne par convention
-- Update strategy: Incremental par date de création

with stg as (
    select * from "sigeti_node_db"."dwh_staging"."stg_conventions"
    
        where dbt_extracted_at >= '2020-01-01'
    
),

enriched as (
    select
        -- Clé surrogate
        md5(cast(coalesce(cast(convention_id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as convention_key,
        
        -- Clés naturelles
        convention_id,
        numero_convention,
        
        -- Contact Info
        nom_convention,
        prenom_convention,
        email,
        telephone,
        profession,
        
        -- Business Info
        raison_sociale,
        forme_juridique,
        registre_commerce,
        domaine_activite,
        
        -- Address
        adresse_personnelle,
        
        -- Statuts
        statut,
        etape_actuelle,
        cree_par,
        
        -- Dates
        date_creation,
        date_modification,
        
        -- Lineage
        dbt_extracted_at,
        current_timestamp as dbt_loaded_at
    
    from stg
)

select * from enriched