-- Fix: Inclure les lots avec statut 'occupé' dans les reserves
DROP TABLE IF EXISTS "dwh_marts_occupation"."mart_occupation_zones_new";

CREATE TABLE "dwh_marts_occupation"."mart_occupation_zones_new" AS
with lots as (
    select 
        l.id as lot_id,
        l.numero,
        l.superficie,
        l.prix,
        l.statut,
        l.viabilite,
        l.zone_industrielle_id,
        l.entreprise_id
    from lots l
),

zones as (
    select 
        z.id as zone_id,
        z.libelle as nom_zone
    from zones_industrielles z
),

demandes_valides as (
    select distinct lot_id
    from demandes_attribution
    where statut = 'VALIDE'
),

occupation_data as (
    select
        z.zone_id,
        z.nom_zone,
        count(*) as nombre_total_lots,
        count(case when l.statut = 'disponible' then 1 end) as lots_disponibles,
        count(case when dv.lot_id is not null then 1 end) as lots_attribues,
        count(case when l.statut = 'occupé' and dv.lot_id is null then 1 end) as lots_reserves,
        sum(l.superficie) as superficie_totale,
        sum(case when l.statut = 'disponible' then l.superficie else 0 end) as superficie_disponible,
        sum(case when dv.lot_id is not null then l.superficie else 0 end) as superficie_attribuee,
        round(
            (count(case when dv.lot_id is not null then 1 end)::numeric / nullif(count(*), 0)::numeric * 100), 
            2
        ) as taux_occupation_pct,
        sum(l.prix) as valeur_totale_lots,
        sum(case when l.statut = 'disponible' then l.prix else 0 end) as valeur_lots_disponibles,
        count(case when l.viabilite = true then 1 end) as lots_viabilises,
        round(
            (count(case when l.viabilite = true then 1 end)::numeric / nullif(count(*), 0)::numeric * 100), 
            2
        ) as taux_viabilisation_pct
    from lots l
    left join zones z on l.zone_industrielle_id = z.zone_id
    left join demandes_valides dv on l.lot_id = dv.lot_id
    group by z.zone_id, z.nom_zone
)

select 
    zone_id,
    nom_zone,
    nombre_total_lots,
    lots_disponibles,
    lots_attribues,
    lots_reserves,
    superficie_totale,
    superficie_disponible,
    superficie_attribuee,
    taux_occupation_pct,
    valeur_totale_lots,
    valeur_lots_disponibles,
    lots_viabilises,
    taux_viabilisation_pct,
    null::integer as nombre_demandes_attribution,
    null::integer as demandes_approuvees,
    null::integer as demandes_rejetees,
    null::integer as demandes_en_attente,
    null::numeric as delai_moyen_traitement,
    null::numeric as taux_approbation_pct
from occupation_data;

-- Copier les données dans la vraie table
DELETE FROM "dwh_marts_occupation"."mart_occupation_zones";
INSERT INTO "dwh_marts_occupation"."mart_occupation_zones"
SELECT * FROM "dwh_marts_occupation"."mart_occupation_zones_new";

DROP TABLE "dwh_marts_occupation"."mart_occupation_zones_new";

-- Vérifier les résultats pour Yopougon
SELECT 
    nom_zone,
    nombre_total_lots,
    lots_attribues,
    lots_disponibles,
    lots_reserves,
    (lots_attribues + lots_disponibles + lots_reserves) as total_check,
    taux_occupation_pct
FROM "dwh_marts_occupation"."mart_occupation_zones"
WHERE nom_zone LIKE '%Yopougon%';
