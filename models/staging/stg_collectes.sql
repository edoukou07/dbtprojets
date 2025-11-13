{{
    config(
        materialized='view'
    )
}}

select
    id,
    reference,
    montant_a_recouvrer,
    montant_recouvre,
    date_debut,
    date_fin_prevue,
    status,
    commentaire,
    cree_par,
    modifie_par,
    created_at,
    updated_at,
    statut_cloture,
    date_cloture,
    cloture_par,
    entreprises_selectionnees,
    factures_generees,
    date_generation_factures
from {{ source('sigeti_source', 'collectes') }}
where id is not null
