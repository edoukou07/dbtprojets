

-- Mart Occupation - Analyse de l'occupation des lots et zones

with lots as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_lots"
),

zones as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_zones_industrielles"
),

entreprises as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
),

attributions as (
    select * from "sigeti_node_db"."dwh_facts"."fait_attributions"
),

occupation_lots as (
    select
        z.zone_id,
        z.nom_zone,
        
        -- Comptage des lots
        count(*) as nombre_total_lots,
        count(case when l.est_disponible then 1 end) as lots_disponibles,
        count(case when l.est_attribue then 1 end) as lots_attribues,
        count(case when not l.est_attribue and not l.est_disponible then 1 end) as lots_reserves,
        
        -- Surfaces
        sum(l.superficie) as superficie_totale,
        sum(case when l.est_disponible then l.superficie else 0 end) as superficie_disponible,
        sum(case when l.est_attribue then l.superficie else 0 end) as superficie_attribuee,
        
        -- Taux d'occupation
        round(
            (count(case when l.est_attribue then 1 end)::numeric / 
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