{{ config(
    materialized='table',
    schema='marts_compliance',
    indexes=[
        {'columns': ['etape_actuelle']},
        {'columns': ['annee_mois']}
    ],
    tags=['compliance', 'P3']
) }}

-- Data Mart: Délai de Traitement par Étape
-- Analyse des délais de traitement par étape actuelle
-- Refresh: Quotidien
-- Utilisateurs: Process owners, Management

with conventions as (
    select * from {{ ref('fait_conventions') }}
),

étapes_calc as (
    select
        extract(year from date_creation) as annee,
        extract(month from date_creation) as mois,
        to_char(date_creation, 'YYYY-MM') as annee_mois,
        
        -- Étape actuelle
        etape_actuelle,
        
        -- Statut
        statut,
        
        -- Delai depuis création
        extract(day from (date_modification - date_creation)) as jours_depuis_creation,
        
        -- Convention info
        convention_id,
        numero_convention
    
    from conventions
    where etape_actuelle is not null
),

aggregated as (
    select
        annee,
        mois,
        annee_mois,
        etape_actuelle,
        statut,
        
        -- Volume
        count(*) as nombre_conventions,
        count(distinct numero_convention) as nombre_conventions_uniques,
        
        -- Délais
        round(avg(jours_depuis_creation)::numeric, 2) as delai_moyen_traitement_jours,
        round(min(jours_depuis_creation)::numeric, 0) as delai_min_traitement_jours,
        round(max(jours_depuis_creation)::numeric, 0) as delai_max_traitement_jours,
        round(percentile_cont(0.5) within group (order by jours_depuis_creation)::numeric, 0) as delai_median_traitement_jours,
        round(percentile_cont(0.95) within group (order by jours_depuis_creation)::numeric, 0) as delai_p95_traitement_jours,
        
        -- Statut breakdown
        count(case when statut = 'VALIDEE' then 1 end) as conventions_validees,
        count(case when statut = 'REJETEE' then 1 end) as conventions_rejetees,
        count(case when statut = 'EN_COURS' then 1 end) as conventions_en_cours,
        
        current_timestamp as dbt_updated_at
    
    from étapes_calc
    group by annee, mois, annee_mois, etape_actuelle, statut
)

select 
    {{ dbt_utils.generate_surrogate_key(['annee_mois', 'etape_actuelle']) }} as delai_approbation_key,
    *
from aggregated
order by annee desc, mois desc, etape_actuelle

