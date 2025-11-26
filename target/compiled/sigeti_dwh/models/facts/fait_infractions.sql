

-- Fact Table: Infractions
-- Enregistrement des infractions détectées
-- Grain: Une ligne par infraction

with stg as (
    select * from "sigeti_node_db"."dwh_staging"."stg_infractions"
),

enriched as (
    select
        -- Clés
        infraction_id,
        lot_id,
        operateur_id,
        entreprise_id,
        
        -- Attributs
        type_operateur,
        statut,
        etape,
        
        -- Flags
        is_resolved,
        
        -- Dates
        date_detection,
        created_at,
        updated_at,
        
        -- Calculs
        case when is_resolved then (updated_at::date - date_detection) else null end as days_to_resolution,
        (current_date - date_detection)::int as days_since_detection,
        
        -- Métadonnées
        current_timestamp as dbt_loaded_at
    from stg
)

select * from enriched