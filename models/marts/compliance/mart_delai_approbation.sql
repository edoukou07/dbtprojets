{{ config(
    materialized='table',
    schema='marts_compliance',
    indexes=[
        {'columns': ['etape_actuelle']},
        {'columns': ['annee_mois']},
        {'columns': ['agent_approbateur_id']}
    ],
    tags=['compliance', 'P3']
) }}

-- Data Mart: Processing Delay by Step
-- Analysis of processing delays by current step
-- Dimensions: Time, Step, Status, Enterprise, Zone, Approver Agent, Rejection Reason
-- Refresh: Daily
-- Users: Process owners, Management

with conventions as (
    select * from {{ ref('fait_conventions') }}
),

agents as (
    select * from {{ ref('dim_agents') }}
),

domaines as (
    select * from {{ ref('dim_domaines_activites_conventions') }}
),

conventions_enrichies as (
    select
        c.convention_id,
        c.numero_convention,
        extract(year from c.date_creation) as annee,
        extract(month from c.date_creation) as mois,
        to_char(c.date_creation, 'YYYY-MM') as annee_mois,
        
        -- Current step
        c.etape_actuelle,
        
        -- Status
        c.statut,
        
        -- Approver agent (IMPORTANT - using cree_par as proxy)
        c.cree_par as agent_approbateur_id,
        coalesce(ag.nom_agent, 'SYSTEM') as nom_approbateur,
        
        -- Enterprise dimensions (PHASE 1 - CRITICAL)
        c.raison_sociale,
        c.forme_juridique,
        c.domaine_activite as libelle_domaine,
        coalesce(d.categorie_domaine, 'AUTRE') as categorie_domaine,
        
        -- Delay since creation
        extract(day from (c.date_modification - c.date_creation)) as jours_depuis_creation,
        
        -- Waiting for action delay (IMPORTANT)
        case 
            when c.statut = 'EN_COURS' then extract(day from (current_timestamp - c.date_modification))
            else 0
        end as jours_en_attente_action,
        
        -- Timestamps
        c.date_creation,
        c.date_modification
    
    from conventions c
    left join agents ag on c.cree_par = ag.agent_id
    left join domaines d on c.domaine_activite = d.libelle_domaine
    
    where c.etape_actuelle is not null
),

aggregated as (
    select
        annee,
        mois,
        annee_mois,
        etape_actuelle,
        statut,
        
        -- Approver agent dimensions
        agent_approbateur_id,
        nom_approbateur,
        
        -- Enterprise dimensions (PHASE 1)
        raison_sociale,
        forme_juridique,
        libelle_domaine,
        categorie_domaine,
        
        -- Volume
        count(*) as nombre_conventions,
        count(distinct numero_convention) as nombre_conventions_uniques,
        
        -- Status breakdown
        count(case when statut = 'VALIDEE' then 1 end) as conventions_validees,
        count(case when statut = 'REJETEE' then 1 end) as conventions_rejetees,
        count(case when statut = 'EN_COURS' then 1 end) as conventions_en_cours,
        
        -- Delays - percentiles
        round(avg(jours_depuis_creation)::numeric, 2) as delai_moyen_traitement_jours,
        round(min(jours_depuis_creation)::numeric, 0) as delai_min_traitement_jours,
        round(max(jours_depuis_creation)::numeric, 0) as delai_max_traitement_jours,
        round(percentile_cont(0.5) within group (order by jours_depuis_creation)::numeric, 0) as delai_median_traitement_jours,
        round(percentile_cont(0.95) within group (order by jours_depuis_creation)::numeric, 0) as delai_p95_traitement_jours,
        
        -- Waiting for action delay (IMPORTANT)
        round(avg(jours_en_attente_action)::numeric, 2) as jours_attente_moyen,
        round(max(jours_en_attente_action)::numeric, 0) as jours_attente_max,
        
        current_timestamp as dbt_updated_at
    
    from conventions_enrichies
    group by annee, mois, annee_mois, etape_actuelle, statut, agent_approbateur_id, nom_approbateur, raison_sociale, forme_juridique, libelle_domaine, categorie_domaine
)

select 
    {{ dbt_utils.generate_surrogate_key(['annee_mois', 'etape_actuelle', 'agent_approbateur_id', 'statut']) }} as delai_approbation_key,
    *
from aggregated
order by annee desc, mois desc, etape_actuelle

