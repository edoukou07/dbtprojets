

-- Fact Table: Indemnisations
-- Suivi des indemnisations
-- Grain: Une ligne par indemnisation
-- Update strategy: Incremental par date de création

with stg as (
    select * from "sigeti_node_db"."dwh_staging"."stg_indemnisations"
    
        where dbt_extracted_at >= '2020-01-01'
    
),

enriched as (
    select
        -- Clé surrogate
        md5(cast(coalesce(cast(indemnisation_id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as indemnisation_key,
        
        -- Clés naturelles
        indemnisation_id,
        beneficiaire_id,
        zone_id,
        
        -- Statut et motif
        statut,
        motif_indemnisation,
        
        -- Montants
        montant_restant,
        
        -- Dates
        date_creation,
        
        -- Lineage
        updated_at,
        dbt_extracted_at,
        current_timestamp as dbt_loaded_at
    
    from stg
)

select * from enriched