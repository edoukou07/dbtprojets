
  
    

  create  table "sigeti_node_db"."dwh_marts_occupation"."mart_occupation_zones__dbt_tmp"
  
  
    as
  
  (
    

-- Mart Occupation - Analyse de l'occupation des lots et zones
-- Matérialisé en table pour performance optimale des dashboards

with lots as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_lots"
),

zones as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_zones_industrielles"
),

attributions as (
    select * from "sigeti_node_db"."dwh_facts"."fait_attributions"
),

-- Vérifier les attributions approuvées directement depuis la source
demandes_attribution_source as (
    select distinct lot_id
    from "sigeti_node_db"."public"."demandes_attribution"
    where statut = 'VALIDE'
),

occupation_lots as (
    select
        z.zone_id,
        z.nom_zone,
        
        -- Comptage des lots
        count(*) as nombre_total_lots,
        count(case when l.est_disponible then 1 end) as lots_disponibles,
        count(case when da.lot_id is not null then 1 end) as lots_attribues,
        count(case when not l.est_disponible and da.lot_id is null then 1 end) as lots_reserves,
        
        -- Surfaces
        sum(l.superficie) as superficie_totale,
        sum(case when l.est_disponible then l.superficie else 0 end) as superficie_disponible,
        sum(case when da.lot_id is not null then l.superficie else 0 end) as superficie_attribuee,
        
        -- Taux d'occupation
        round(
            (count(case when da.lot_id is not null then 1 end)::numeric / 
             nullif(count(*), 0)::numeric * 100), 
            2
        ) as taux_occupation_pct,
        
        -- Valeur
        sum(l.prix) as valeur_totale_lots,
        sum(case when l.est_disponible then l.prix else 0 end) as valeur_lots_disponibles,
        
        -- Viabilité
        count(case when l.est_viable then 1 end) as lots_viabilises,
        round(
            (count(case when l.est_viable then 1 end)::numeric / 
             nullif(count(*), 0)::numeric * 100), 
            2
        ) as taux_viabilisation_pct
        
    from lots l
    left join zones z on l.zone_industrielle_id = z.zone_id
    left join demandes_attribution_source da on l.lot_id = da.lot_id
    
    group by 
        z.zone_id,
        z.nom_zone
),

attributions_stats as (
    select
        a.zone_id,
        
        count(*) as nombre_demandes_attribution,
        count(case when a.est_approuve then 1 end) as demandes_approuvees,
        count(case when a.est_rejete then 1 end) as demandes_rejetees,
        count(case when a.est_en_attente then 1 end) as demandes_en_attente,
        
        avg(a.delai_traitement_jours) as delai_moyen_traitement,
        
        round(
            (count(case when a.est_approuve then 1 end)::numeric / 
             nullif(count(*), 0)::numeric * 100), 
            2
        ) as taux_approbation_pct
        
    from attributions a
    
    group by a.zone_id
)

select
    o.*,
    a.nombre_demandes_attribution,
    a.demandes_approuvees,
    a.demandes_rejetees,
    a.demandes_en_attente,
    a.delai_moyen_traitement,
    a.taux_approbation_pct
    
from occupation_lots o
left join attributions_stats a on o.zone_id = a.zone_id
  );
  