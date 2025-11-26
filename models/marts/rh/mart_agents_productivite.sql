{{ config(
    materialized='table',
    schema='marts_rh',
    indexes=[
        {'columns': ['zone_id']},
        {'columns': ['agent_id']}
    ],
    tags=['rh', 'P2'],
    enabled=false
) }}

-- Data Mart: Productivité Agents
-- KPIs de productivité des agents
-- Refresh: Hebdomadaire
-- Utilisateurs: RH, Managers de zone

with agents as (
    select * from {{ ref('dim_agents') }}
),

collectes_agents as (
    select * from {{ source('sigeti_source', 'collecte_agents') }}
),

collectes as (
    select * from {{ ref('fait_collectes') }}
),

zones as (
    select * from {{ ref('dim_zones_industrielles') }}
),

joined as (
    select
        z.zone_name,
        z.zone_id,
        a.agent_id,
        a.nom_complet,
        a.poste,
        a.anciennete_annees,
        
        extract(year from current_date) as annee_actuelle,
        extract(month from current_date) as mois_actuel,
        
        -- Collectes
        count(distinct ca.collecte_id) as nombre_collectes,
        count(case when c.est_cloturee then 1 end) as collectes_cloturees,
        
        -- Montants
        sum(c.montant_a_recouvrer) as montant_total_a_recouvrer,
        sum(c.montant_recouvre) as montant_total_recouvre,
        
        -- Taux
        round(avg(c.taux_recouvrement), 2) as taux_recouvrement_moyen_pct,
        round(count(case when c.est_cloturee then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as taux_cloture_pct,
        
        -- Délais
        round(avg(c.duree_reelle_jours), 2) as delai_moyen_traitement_jours,
        
        -- Productivité
        round(count(distinct ca.collecte_id)::numeric / 
              nullif(a.anciennete_annees, 0), 2) as collectes_par_annee_experience,
        
        round(sum(c.montant_recouvre)::numeric / 
              nullif(count(distinct ca.collecte_id), 0), 2) as montant_moyen_par_collecte,
        
        -- Ranking par zone
        row_number() over (partition by z.zone_id order by sum(c.montant_recouvre) desc) as rang_productivite_zone,
        
        current_timestamp as dbt_updated_at
    
    from agents a
    left join zones z on a.zone_id = z.zone_id
    left join collectes_agents ca on a.agent_id = ca.agent_id
    left join collectes c on ca.collecte_id = c.collecte_id
    where a.est_actif = 1
    group by z.zone_name, z.zone_id, a.agent_id, a.nom_complet, a.poste, a.anciennete_annees
)

select * from joined
order by zone_id, montant_total_recouvre desc nulls last
