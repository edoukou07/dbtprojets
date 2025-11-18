-- Vérifier Demandes et Attributions
SELECT 'Demandes' as metric, COUNT(*) as value
FROM dwh_facts.fait_demandes
WHERE EXTRACT(YEAR FROM date_demande) = EXTRACT(YEAR FROM CURRENT_DATE);

SELECT 'Attributions' as metric, COUNT(*) as value
FROM dwh_facts.fait_attributions
WHERE EXTRACT(YEAR FROM date_attribution) = EXTRACT(YEAR FROM CURRENT_DATE);

-- Détails par mois (Demandes)
SELECT 'Demandes par mois' as detail, 
       TO_CHAR(date_demande, 'YYYY-MM') as period, 
       COUNT(*) as count
FROM dwh_facts.fait_demandes
WHERE EXTRACT(YEAR FROM date_demande) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY TO_CHAR(date_demande, 'YYYY-MM')
ORDER BY period DESC;

-- Détails par mois (Attributions)
SELECT 'Attributions par mois' as detail, 
       TO_CHAR(date_attribution, 'YYYY-MM') as period, 
       COUNT(*) as count
FROM dwh_facts.fait_attributions
WHERE EXTRACT(YEAR FROM date_attribution) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY TO_CHAR(date_attribution, 'YYYY-MM')
ORDER BY period DESC;
