-- Vérifier Taux Recouvrement et Efficacité collecte
SELECT 'Taux Recouvrement Global' as metric, 
       taux_recouvrement_global_pct as value
FROM dwh_marts_operationnel.mart_kpi_operationnels
WHERE annee = 2025 AND trimestre = 4
LIMIT 1;

SELECT 'Taux Cloture (Efficacité)' as metric,
       taux_cloture_pct as value
FROM dwh_marts_operationnel.mart_kpi_operationnels
WHERE annee = 2025 AND trimestre = 4
LIMIT 1;

-- Détails collectes
SELECT 'Collectes Details' as metric,
       nombre_collectes,
       collectes_cloturees,
       collectes_ouvertes,
       taux_recouvrement_global_pct,
       taux_cloture_pct
FROM dwh_marts_operationnel.mart_kpi_operationnels
WHERE annee = 2025 AND trimestre = 4;

-- Vérification brute depuis fait_collectes
SELECT 'Collectes Brutes' as source,
       COUNT(*) as total_collectes,
       COUNT(CASE WHEN est_cloturee = true THEN 1 END) as cloturees,
       ROUND((SUM(montant_recouvre)::numeric / NULLIF(SUM(montant_a_recouvrer), 0)::numeric * 100), 2) as taux_recouvrement_calc
FROM dwh_facts.fait_collectes;
