

-- Data Mart: Emplois Créés
-- KPIs d'emplois créés par zone et catégorie
-- Refresh: Mensuel
-- Utilisateurs: Métier socio-économique, Management

with emplois as (
    select * from "sigeti_node_db"."dwh_facts"."fait_emplois_crees"
),

zones as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_zones_industrielles"
),

aggregated as (
    select
        z.nom_zone as zone_name,
        e.zone_id,
        extract(year from e.date_premiere_creation) as annee,
        extract(month from e.date_premiere_creation) as mois,
        e.type_demande,
        e.statut,
        
        -- Volumes totaux
        count(*) as nombre_demandes,
        sum(e.total_emplois) as total_emplois,
        sum(e.total_emplois_expatries) as total_emplois_expatries,
        sum(e.total_emplois_nationaux) as total_emplois_nationaux,
        
        -- Moyennes
        round(avg(e.avg_emplois_par_demande)::numeric, 2) as avg_emplois_par_demande,
        
        -- Ratios
        round(sum(e.total_emplois_expatries)::numeric / nullif(sum(e.total_emplois), 0) * 100, 2) as pct_expatries,
        round(sum(e.total_emplois_nationaux)::numeric / nullif(sum(e.total_emplois), 0) * 100, 2) as pct_nationaux,
        
        current_timestamp as dbt_updated_at
    
    from emplois e
    left join zones z on e.zone_id = z.zone_id
    group by z.nom_zone, e.zone_id, annee, mois, e.type_demande, e.statut
)

select * from aggregated