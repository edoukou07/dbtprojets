-- Compter Demandes (par type_demande ou statut)
SELECT 'Total Attributions/Demandes' as metric, COUNT(DISTINCT demande_id) as value
FROM dwh_facts.fait_attributions
WHERE EXTRACT(YEAR FROM date_demande) = EXTRACT(YEAR FROM CURRENT_DATE);

SELECT 'Total Demandes par type' as metric, type_demande, COUNT(DISTINCT demande_id) as count
FROM dwh_facts.fait_attributions
WHERE EXTRACT(YEAR FROM date_demande) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY type_demande;

SELECT 'Attributions par statut' as metric, statut, COUNT(*) as count
FROM dwh_facts.fait_attributions
WHERE EXTRACT(YEAR FROM date_demande) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY statut;

SELECT 'Résumé' as metric, 
       'Demandes Uniques' as detail, 
       COUNT(DISTINCT demande_id) as value
FROM dwh_facts.fait_attributions
WHERE EXTRACT(YEAR FROM date_demande) = EXTRACT(YEAR FROM CURRENT_DATE);

SELECT 'Résumé' as metric, 
       'Attributions Totales' as detail, 
       COUNT(*) as value
FROM dwh_facts.fait_attributions
WHERE EXTRACT(YEAR FROM date_demande) = EXTRACT(YEAR FROM CURRENT_DATE);
