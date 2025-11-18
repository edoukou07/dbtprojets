SELECT 'Fait Collectes' as source, COUNT(*) as total_rows, COUNT(DISTINCT collecte_id) as distinct_collectes
FROM dwh_facts.fait_collectes;

SELECT 'Staging Collectes' as source, COUNT(*) as total_rows, COUNT(DISTINCT collecte_id) as distinct_collectes
FROM dwh_staging.stg_collectes;
