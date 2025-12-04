{{ config(
    materialized='view',
    schema='staging'
) }}

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
        ordre,
        statut,
        progression,
        date_debut_prevue,
        date_debut_effective,
        date_fin_prevue,
        date_fin_effective,
        created_at,
        updated_at
    from {{ source('sigeti_source', 'etapes_suivi_implantation') }}
),

validated as (
    select
        -- Natural keys
        id as etape_id,
        suivi_implantation_id as implantation_id,
        
        -- Attributes
        nom as etape_name,
        description as etape_description,
        ordre,
        statut,
        progression as progression_pct,
        
        -- Dates
        date_debut_prevue,
        date_debut_effective,
        date_fin_prevue,
        date_fin_effective,
        
        -- Calculs de durées (en jours)
        case 
            when date_debut_prevue is not null and date_fin_prevue is not null
            then extract(epoch from (date_fin_prevue - date_debut_prevue))/86400
            else null
        end as duree_prevue_jours,
        
        case 
            when date_debut_effective is not null and date_fin_effective is not null
            then extract(epoch from (date_fin_effective - date_debut_effective))/86400
            else null
        end as duree_reelle_jours,
        
        -- Calcul du retard
        case 
            when date_fin_effective is not null and date_fin_prevue is not null
            then extract(epoch from (date_fin_effective - date_fin_prevue))/86400
            when date_fin_effective is null and date_fin_prevue is not null and current_date > date_fin_prevue::date
            then extract(epoch from (current_timestamp - date_fin_prevue))/86400
            else 0
        end as jours_de_retard,
        
        -- Indicateurs booléens
        case 
            when date_fin_prevue is not null and current_timestamp > date_fin_prevue and date_fin_effective is null
            then 1
            when date_fin_effective is not null and date_fin_effective > date_fin_prevue
            then 1
            else 0
        end as est_en_retard,
        
        case 
            when date_fin_effective is not null and progression = 100
            then 1
            else 0
        end as est_complete,
        
        -- Validations
        case 
            when statut in ('EN_ATTENTE', 'EN_COURS', 'TERMINE', 'RETARD', 'BLOQUE')
            then 1
            else 0
        end as statut_valide,
        
        case 
            when date_debut_prevue is not null and date_fin_prevue is not null 
                 and date_fin_prevue >= date_debut_prevue
            then 1
            else 0
        end as dates_coherentes,
        
        -- Audit
        created_at,
        updated_at,
        current_timestamp as dbt_extracted_at
    
    from raw_etapes
    where id is not null
)

select * from validated
