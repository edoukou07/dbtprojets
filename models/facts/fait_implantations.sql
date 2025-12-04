{{ config(
    materialized='incremental',
    schema='facts',
    unique_key=['implantation_id', 'etape_id'],
    on_schema_change='append_new_columns',
    tags=['operationnel', 'P1'],
    enabled=true
) }}

-- Fact Table: Implantations
-- Suivi des étapes d'implantation par site
-- Grain: Une ligne par étape de suivi
-- Update strategy: Incremental par date de début

with stg as (
    select * from {{ ref('stg_suivi_implantation') }}
    {% if execute %}
        where dbt_extracted_at >= '{{ var("incremental_since", "2020-01-01") }}'
    {% endif %}
),

enriched as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['implantation_id', 'etape_id']) }} as implantation_key,
        
        -- Clés naturelles
        implantation_id,
        etape_id,
        
        -- Attributs
        etape_name,
        etape_description,
        ordre,
        statut,
        progression_pct,
        est_en_retard,
        est_complete,
        
        -- Dates
        date_debut_prevue,
        date_debut_effective,
        date_fin_prevue,
        date_fin_effective,
        
        -- Calculs de durées
        duree_prevue_jours,
        duree_reelle_jours,
        jours_de_retard,
        
        -- Validations
        statut_valide,
        dates_coherentes,
        
        -- Lineage
        created_at,
        updated_at,
        dbt_extracted_at,
        current_timestamp as dbt_loaded_at
    
    from stg
),

final as (
    select 
        distinct on (implantation_id, etape_id)
        *
    from enriched
    order by implantation_id, etape_id, dbt_loaded_at desc
)

select * from final
