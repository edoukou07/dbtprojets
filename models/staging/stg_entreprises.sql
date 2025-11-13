{{
    config(
        materialized='view'
    )
}}

select
    id,
    raison_sociale,
    telephone,
    email,
    registre_commerce,
    compte_contribuable,
    forme_juridique,
    adresse,
    date_constitution,
    domaine_activite_id,
    entreprise_id,
    user_id,
    date_creation,
    date_modification
from {{ source('sigeti_source', 'entreprises') }}
where id is not null
