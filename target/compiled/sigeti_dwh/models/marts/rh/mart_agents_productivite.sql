

-- Data Mart: Productivité Agents
-- KPIs de productivité des agents
-- Refresh: Hebdomadaire
-- Utilisateurs: RH, Managers

with agents as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_agents"
),

collectes_agents as (
    select * from "sigeti_node_db"."public"."collecte_agents"
),

collectes as (
    select * from "sigeti_node_db"."dwh_facts"."fait_collectes"
),

joined as (
    select
        a.agent_id,
        a.nom_complet,
        a.matricule,
        a.email,
        a.type_agent_id,
        
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
        round(sum(c.montant_recouvre)::numeric / 
              nullif(count(distinct ca.collecte_id), 0), 2) as montant_moyen_par_collecte,
        
        -- Ranking global
        row_number() over (order by sum(c.montant_recouvre) desc) as rang_productivite_global,
        
        current_timestamp as dbt_updated_at
    
    from agents a
    left join collectes_agents ca on a.agent_id = ca.agent_id
    left join collectes c on ca.collecte_id = c.collecte_id
    where a.est_actif = 1
    group by a.agent_id, a.nom_complet, a.matricule, a.email, a.type_agent_id
)

select * from joined
order by montant_total_recouvre desc nulls last