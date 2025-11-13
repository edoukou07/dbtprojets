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
from {{ source('sigeti_source', 'domaines_activites') }}
where id is not null
