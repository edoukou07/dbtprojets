{{
    config(
        materialized='view'
    )
}}

select
    id,
    libelle,
    description,
    created_at,
    updated_at
from {{ source('sigeti_source', 'zones_industrielles') }}
where id is not null
