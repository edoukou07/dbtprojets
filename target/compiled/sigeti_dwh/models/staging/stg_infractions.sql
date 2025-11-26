

-- Staging: Infractions
-- Extract and validation of raw infraction data from workflow_infractions
-- Source: workflow_infractions table
-- Grain: One row per infraction detected

with raw_infractions as (
    select
        id,
        lot_id,
        type_operateur,
        operateur_id,
        entreprise_id,
        statut,
        etape,
        date_saisine as date_detection,
        created_at,
        updated_at
    from "sigeti_node_db"."public"."workflow_infractions"
),

validated as (
    select
        -- Clés naturelles
        id as infraction_id,
        lot_id,
        operateur_id,
        entreprise_id,
        
        -- Dimensions
        type_operateur,
        statut,
        etape,
        
        -- Dates
        date_detection,
        created_at,
        updated_at,
        
        -- Flags
        case when statut = 'cloturer' then true else false end as is_resolved
    from raw_infractions
    where id is not null
)

select * from validated