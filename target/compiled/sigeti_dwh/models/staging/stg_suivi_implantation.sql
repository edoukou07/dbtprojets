

-- Staging: Suivi Implantation
-- Extract et validation des étapes de suivi d'implantation
-- Source: etapes_suivi_implantation table
-- Grain: Une ligne par étape de suivi

with raw_etapes as (
    select
        id,
        suivi_implantation_id,
        nom,
        description,
        statut,
        progression,
        date_debut_prevue,
        date_debut_effective,
        date_fin_prevue,
        date_fin_effective,
        created_at,
        updated_at
    from "sigeti_node_db"."public"."etapes_suivi_implantation"
),

validated as (
    select
        -- Natural keys
        id as etape_id,
        suivi_implantation_id as implantation_id,
        
        -- Attributes
        nom as etape_name,
        description as etape_description,
        statut,
        progression as progression_pct,
        
        -- Dates
        date_debut_prevue,
        date_debut_effective,
        date_fin_prevue,
        nullif(date_fin_effective, null) as date_fin_effective,
        
        -- Audit
        created_at,
        updated_at,
        current_timestamp as dbt_extracted_at
    
    from raw_etapes
    where id is not null
)

select * from validated