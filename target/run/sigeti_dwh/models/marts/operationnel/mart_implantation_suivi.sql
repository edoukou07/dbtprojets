
  
    

  create  table "sigeti_node_db"."dwh_marts_operationnel"."mart_implantation_suivi__dbt_tmp"
  
  
    as
  
  (
    

-- Data Mart: Suivi Implantation
-- KPIs de suivi d'implantation par zone
-- Refresh: Temps réel
-- Utilisateurs: Project managers, Opérationnels

with implantations as (
    select * from "sigeti_node_db"."dwh_facts"."fait_implantations"
),

suivis as (
    select 
        id as suivi_id,
        demande_attribution_id,
        statut as statut_suivi,
        date_debut_suivi,
        date_limite_implantation,
        date_implantation_effective,
        progression as progression_suivi
    from "sigeti_node_db"."public"."suivis_implantation"
),

demandes as (
    select 
        da.id as demande_id,
        dal.lot_id
    from "sigeti_node_db"."public"."demandes_attribution" da
    left join "sigeti_node_db"."public"."demande_attribution_lots" dal 
        on da.id = dal.demande_attribution_id
),

lots as (
    select 
        id as lot_id,
        zone_id
    from "sigeti_node_db"."public"."lots"
),

zones as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_zones_industrielles"
),

enriched_implantations as (
    select
        i.*,
        s.statut_suivi,
        s.date_debut_suivi,
        d.lot_id,
        l.zone_id
    from implantations i
    left join suivis s on i.implantation_id = s.suivi_id
    left join demandes d on s.demande_attribution_id = d.demande_id
    left join lots l on d.lot_id = l.lot_id
),

aggregated as (
    select
        coalesce(z.nom_zone, 'Zone Inconnue') as zone_name,
        coalesce(ei.zone_id, 0) as zone_id,
        extract(year from coalesce(ei.date_debut_effective, ei.date_debut_prevue)) as annee,
        extract(month from coalesce(ei.date_debut_effective, ei.date_debut_prevue)) as mois,
        to_char(coalesce(ei.date_debut_effective, ei.date_debut_prevue), 'YYYY-MM') as annee_mois,
        
        -- Volumes
        count(*) as nombre_etapes,
        count(distinct ei.implantation_id) as nombre_suivis_distincts,
        
        -- Statuts
        count(case when ei.statut = 'TERMINE' then 1 end) as nombre_etapes_terminees,
        count(case when ei.statut = 'EN_COURS' then 1 end) as nombre_etapes_en_cours,
        count(case when ei.est_en_retard = 1 then 1 end) as nombre_etapes_en_retard,
        count(case when ei.statut = 'BLOQUE' then 1 end) as nombre_etapes_bloquees,
        
        -- Taux
        round(count(case when ei.statut = 'TERMINE' then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as pct_etapes_terminees,
        
        round(count(case when ei.est_en_retard = 1 then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as pct_etapes_en_retard,
        
        round(count(case when ei.est_complete = 1 then 1 end)::numeric / 
              nullif(count(*), 0) * 100, 2) as pct_etapes_completes,
        
        -- Délais
        round(avg(ei.duree_reelle_jours)::numeric, 2) as duree_moyenne_reelle_jours,
        round(avg(ei.duree_prevue_jours)::numeric, 2) as duree_moyenne_prevue_jours,
        round(avg(ei.jours_de_retard)::numeric, 2) as retard_moyen_jours,
        round(max(ei.jours_de_retard)::numeric, 2) as retard_max_jours,
        
        -- Variance planning
        round(avg(coalesce(ei.duree_reelle_jours, 0) - coalesce(ei.duree_prevue_jours, 0))::numeric, 2) as variance_planning_jours,
        
        -- Progression moyenne
        round(avg(ei.progression_pct)::numeric, 2) as progression_moyenne_pct,
        
        current_timestamp as dbt_updated_at
    
    from enriched_implantations ei
    left join zones z on ei.zone_id = z.zone_id
    group by z.nom_zone, ei.zone_id, annee, mois, annee_mois
)

select * from aggregated
  );
  