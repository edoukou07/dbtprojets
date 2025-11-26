{{ config(
    materialized='table',
    schema='marts_compliance',
    indexes=[
        {'columns': ['etape_actuelle']},
        {'columns': ['annee_mois']}
    ],
    tags=['compliance', 'P1']
) }}

-- Data Mart: Validation Conventions
-- Suivi de l'état et de la progression des conventions
-- Refresh: Quotidien
-- Utilisateurs: Métier conformité, Management

with conventions as (
    select * from {{ ref('fait_conventions') }}
),

aggregated as (
    select
        extract(year from c.date_creation) as annee,
        extract(month from c.date_creation) as mois,
        to_char(c.date_creation, 'YYYY-MM') as annee_mois,
        
        -- Étape actuelle
        c.etape_actuelle,
        c.statut,
        
        -- Volumes
        count(*) as nombre_conventions,
        count(distinct c.cree_par) as nombre_createurs,
        
        -- Statut breakdown
        count(case when c.statut = 'VALIDEE' then 1 end) as conventions_validees,
        count(case when c.statut = 'REJETEE' then 1 end) as conventions_rejetees,
        count(case when c.statut = 'EN_COURS' then 1 end) as conventions_en_cours,
        count(case when c.statut = 'ARCHIVEE' then 1 end) as conventions_archivees,
        
        -- Taux de validation
        round(count(case when c.statut = 'VALIDEE' then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as taux_validation_pct,
        
        -- Taux de rejet
        round(count(case when c.statut = 'REJETEE' then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as taux_rejet_pct,
        
        -- Délais moyens
        round(avg(extract(day from (c.date_modification - c.date_creation)))::numeric, 2) as delai_moyen_traitement_jours,
        round(max(extract(day from (c.date_modification - c.date_creation)))::numeric, 0) as delai_max_traitement_jours,
        
        current_timestamp as dbt_updated_at
    
    from conventions c
    where c.statut is not null
    group by annee, mois, annee_mois, c.etape_actuelle, c.statut
)

select 
    {{ dbt_utils.generate_surrogate_key(['annee_mois', 'etape_actuelle']) }} as convention_validation_key,
    *
from aggregated
order by annee_mois desc, etape_actuelle

