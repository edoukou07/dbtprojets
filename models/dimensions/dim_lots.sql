{{
    config(
        materialized='table',
        unique_key='lot_key'
    )
}}

with source as (
    select * from {{ ref('stg_lots') }}
),

lots_enrichis as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['id']) }} as lot_key,
        
        -- Clés naturelles
        id as lot_id,
        numero as numero_lot,
        ilot,
        
        -- Attributs
        superficie,
        unite_mesure,
        prix,
        statut,
        priorite,
        viabilite,
        description,
        coordonnees,
        polygon,
        location,
        
        -- Clés étrangères
        zone_industrielle_id,
        zone_id,
        entreprise_id,
        operateur_id,
        
        -- Dates
        date_acquisition,
        date_reservation,
        delai_option,
        created_at,
        updated_at,
        
        -- Métadonnées
        case when statut = 'disponible' then true else false end as est_disponible,
        case when viabilite = true then true else false end as est_viable,
        case when entreprise_id is not null then true else false end as est_attribue
        
    from source
)

select * from lots_enrichis
