-- Vérifier les nouvelles valeurs de Demandes et Attributions
SELECT 'Demandes Uniques' as metric, nombre_demandes as value
FROM dwh_marts_operationnel.mart_kpi_operationnels
ORDER BY annee DESC, trimestre DESC
LIMIT 1;

SELECT 'Demandes Approuvées' as metric, demandes_approuvees as value
FROM dwh_marts_operationnel.mart_kpi_operationnels
ORDER BY annee DESC, trimestre DESC
LIMIT 1;

SELECT 'Demandes Rejetées' as metric, demandes_rejetees as value
FROM dwh_marts_operationnel.mart_kpi_operationnels
ORDER BY annee DESC, trimestre DESC
LIMIT 1;

SELECT 'Demandes En Attente' as metric, demandes_en_attente as value
FROM dwh_marts_operationnel.mart_kpi_operationnels
ORDER BY annee DESC, trimestre DESC
LIMIT 1;

-- Total devrait être 16 + 6 + 1 = 23
SELECT 'Total Check' as metric, 
       (demandes_approuvees + demandes_rejetees + demandes_en_attente) as calcul,
       nombre_demandes as stored
FROM dwh_marts_operationnel.mart_kpi_operationnels
ORDER BY annee DESC, trimestre DESC
LIMIT 1;
