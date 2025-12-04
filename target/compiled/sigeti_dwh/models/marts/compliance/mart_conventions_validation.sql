

-- Data Mart: Convention Validation
-- Track status and progression of conventions
-- Dimensions: Time, Step, Status, Enterprise, Zone, Agent, Amount
-- Refresh: Daily
-- Users: Compliance Business, Management

with conventions as (
    select * from "sigeti_node_db"."dwh_facts"."fait_conventions"
),

agents as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_agents"
),

domaines as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_domaines_activites_conventions"
),

conventions_enrichies as (
    select
        c.convention_id,
        c.numero_convention,
        extract(year from c.date_creation) as annee,
        extract(month from c.date_creation) as mois,
        to_char(c.date_creation, 'YYYY-MM') as annee_mois,
        
        -- Business dimensions
        c.etape_actuelle,
        c.statut,
        
        -- Agent dimensions (CRITICAL)
        c.cree_par as agent_id,
        coalesce(ag.nom_agent, 'SYSTEM') as nom_agent_createur,
        
        -- Enterprise dimensions (PHASE 1 - CRITICAL)
        c.raison_sociale,
        c.forme_juridique,
        c.domaine_activite as libelle_domaine,
        coalesce(d.categorie_domaine, 'AUTRE') as categorie_domaine,
        
        -- Delays
        extract(day from (c.date_modification - c.date_creation)) as jours_depuis_creation,
        
        -- Timestamps
        c.date_creation,
        c.date_modification
    
    from conventions c
    left join agents ag on c.cree_par = ag.agent_id
    left join domaines d on c.domaine_activite = d.libelle_domaine
    
    where c.statut is not null
),

aggregated as (
    select
        annee,
        mois,
        annee_mois,
        
        -- Business dimensions
        etape_actuelle,
        statut,
        
        -- Agent dimensions
        agent_id,
        nom_agent_createur,
        
        -- Enterprise dimensions (PHASE 1)
        raison_sociale,
        forme_juridique,
        libelle_domaine,
        categorie_domaine,
        
        -- Volumes
        count(*) as nombre_conventions,
        count(distinct agent_id) as nombre_createurs_distincts,
        
        -- Status breakdown
        count(case when statut = 'VALIDEE' then 1 end) as conventions_validees,
        count(case when statut = 'REJETEE' then 1 end) as conventions_rejetees,
        count(case when statut = 'EN_COURS' then 1 end) as conventions_en_cours,
        count(case when statut = 'ARCHIVEE' then 1 end) as conventions_archivees,
        
        -- Validation rate
        round(count(case when statut = 'VALIDEE' then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as taux_validation_pct,
        
        -- Rejection rate
        round(count(case when statut = 'REJETEE' then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as taux_rejet_pct,
        
        -- Average delays
        round(avg(jours_depuis_creation)::numeric, 2) as delai_moyen_traitement_jours,
        round(max(jours_depuis_creation)::numeric, 0) as delai_max_traitement_jours,
        round(min(jours_depuis_creation)::numeric, 0) as delai_min_traitement_jours,
        
        current_timestamp as dbt_updated_at
    
    from conventions_enrichies
    group by annee, mois, annee_mois, etape_actuelle, statut, agent_id, nom_agent_createur, raison_sociale, forme_juridique, libelle_domaine, categorie_domaine
)

select 
    md5(cast(coalesce(cast(annee_mois as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(etape_actuelle as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(agent_id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(statut as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as convention_validation_key,
    *
from aggregated
order by annee_mois desc, etape_actuelle