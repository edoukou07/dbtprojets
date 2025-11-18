
UPDATE dwh_facts.fait_collectes
SET duree_reelle_jours = ABS(duree_reelle_jours)
WHERE duree_reelle_jours < 0;
SELECT 
    COUNT(*) as total_collectes,
    COUNT(CASE WHEN duree_reelle_jours < 0 THEN 1 END) as negative_durees,
    AVG(duree_reelle_jours) as duree_moyenne,
    MIN(duree_reelle_jours) as duree_min,
    MAX(duree_reelle_jours) as duree_max
FROM dwh_facts.fait_collectes;
