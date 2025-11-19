-- Vérifier toutes les zones
SELECT 
    nom_zone,
    nombre_total_lots,
    lots_attribues,
    lots_disponibles,
    taux_occupation_pct
FROM "dwh_marts_occupation"."mart_occupation_zones"
ORDER BY nom_zone;
