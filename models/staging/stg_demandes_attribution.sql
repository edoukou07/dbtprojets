{{
    config(
        materialized='view'
    )
}}

select
    id,
    reference,
    statut,
    etape_courante,
    type_demande,
    entreprise_id,
    lot_id,
    zone_id,
    informations_terrain,
    coordonnees_geospatiales,
    financement,
    emplois,
    priorite,
    decisions_commissions,
    historique_etapes,
    retours,
    metadata,
    user_id,
    created_at,
    updated_at
from {{ source('sigeti_source', 'demandes_attribution') }}
where id is not null
