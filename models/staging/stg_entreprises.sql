{{
    config(
        materialized='view'
    )
}}

select
    id,
    raison_sociale,
    segment_client,
    niveau_risque,
    secteur_activite
from {{ source('sigeti_source', 'entreprises') }}
where id is not null
