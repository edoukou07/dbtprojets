{{
    config(
        materialized='table',
        unique_key='domaine_key'
    )
}}

-- Dimension: Domaines d'Activités (depuis conventions)
-- Extrait des domaines d'activité uniques des conventions
-- Source: fait_conventions.domaine_activite
-- Grain: Un domaine d'activité unique par ligne

with conventions_domaines as (
    select distinct
        domaine_activite
    from {{ ref('fait_conventions') }}
    where domaine_activite is not null
    and trim(domaine_activite) != ''
),

domaines_categorises as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['domaine_activite']) }} as domaine_key,
        
        -- Attributs
        domaine_activite as libelle_domaine,
        
        -- Catégorisation (peut être enrichie plus tard)
        case 
            when lower(domaine_activite) like '%industrie%' or lower(domaine_activite) like '%fabrication%' 
                or lower(domaine_activite) like '%production%' then 'INDUSTRIE'
            when lower(domaine_activite) like '%service%' or lower(domaine_activite) like '%commerce%' 
                or lower(domaine_activite) like '%vente%' then 'SERVICES'
            when lower(domaine_activite) like '%technologie%' or lower(domaine_activite) like '%informatique%' 
                or lower(domaine_activite) like '%tech%' then 'TECH'
            when lower(domaine_activite) like '%agriculture%' or lower(domaine_activite) like '%agro%' then 'AGRICULTURE'
            when lower(domaine_activite) like '%construction%' or lower(domaine_activite) like '%btp%' then 'BTP'
            else 'AUTRE'
        end as categorie_domaine,
        
        -- Métadonnées
        current_timestamp as created_at
        
    from conventions_domaines
)

select * from domaines_categorises
order by libelle_domaine
