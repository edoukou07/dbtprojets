{{
    config(
        materialized='table',
        schema='dimensions',
        unique_key='dossier_key',
        tags=['rh', 'workflow']
    )
}}

/*
    Dimension: Dossiers de Demande d'Attribution
    ============================================
    
    Cette dimension contient les informations descriptives
    des dossiers de demande d'attribution.
    
    Source: demandes_attribution
*/

with demandes as (
    select
        id,
        reference,
        entreprise_id,
        lot_id,
        statut,
        etape_courante,
        type_demande,
        created_at,
        updated_at
    from {{ source('sigeti_source', 'demandes_attribution') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['id']) }} as dossier_key,
        id as dossier_id,
        reference as dossier_reference,
        entreprise_id,
        lot_id,
        statut as dossier_statut,
        etape_courante,
        type_demande,
        
        -- Dates clés
        created_at as date_creation,
        updated_at as date_modification,
        
        -- Indicateurs
        case when statut = 'VALIDE' then true else false end as est_valide,
        case when statut = 'EN_COURS' then true else false end as est_en_cours,
        case when statut = 'REJETE' then true else false end as est_rejete,
        
        -- Métadonnées
        current_timestamp as dbt_loaded_at
        
    from demandes
)

select * from final
