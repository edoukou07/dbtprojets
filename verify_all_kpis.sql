-- Vérifier tous les KPIs du Dashboard
-- 1. FINANCIER: CA Total, Taux Paiement, Collectes, Top Zone
SELECT 'FINANCIER - CA Total' as kpi, SUM(montant_facture) as value
FROM dwh_facts.fait_factures WHERE EXTRACT(YEAR FROM date_facture) = EXTRACT(YEAR FROM CURRENT_DATE);

SELECT 'FINANCIER - CA Payé' as kpi, SUM(montant_paye) as value
FROM dwh_facts.fait_factures WHERE EXTRACT(YEAR FROM date_facture) = EXTRACT(YEAR FROM CURRENT_DATE);

-- 2. OCCUPATION: Zones occupées, Taux occupation, Retard paiement
SELECT 'OCCUPATION - Total Zones' as kpi, COUNT(DISTINCT zone_id) as value
FROM dwh_facts.fait_occupation WHERE status_active = true;

SELECT 'OCCUPATION - Zones En Retard' as kpi, COUNT(DISTINCT zone_id) as value
FROM dwh_facts.fait_factures 
WHERE status_paiement = 'retard' AND EXTRACT(YEAR FROM date_facture) = EXTRACT(YEAR FROM CURRENT_DATE);

-- 3. OPERATIONNEL: Total Factures, Factures Retard, Lots, Collectes (déjà vérifié = 6)
SELECT 'OPERATIONNEL - Total Factures' as kpi, COUNT(*) as value
FROM dwh_facts.fait_factures WHERE EXTRACT(YEAR FROM date_facture) = EXTRACT(YEAR FROM CURRENT_DATE);

SELECT 'OPERATIONNEL - Factures Retard' as kpi, COUNT(*) as value
FROM dwh_facts.fait_factures 
WHERE status_paiement = 'retard' AND EXTRACT(YEAR FROM date_facture) = EXTRACT(YEAR FROM CURRENT_DATE);

SELECT 'OPERATIONNEL - Lots' as kpi, COUNT(DISTINCT lot_id) as value
FROM dwh_facts.fait_lots WHERE EXTRACT(YEAR FROM date_creation) = EXTRACT(YEAR FROM CURRENT_DATE);
