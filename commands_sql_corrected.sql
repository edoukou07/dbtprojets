
SELECT COUNT(*) as durees_negatives FROM dwh_facts.fait_collectes WHERE duree_reelle_jours < 0;
UPDATE dwh_facts.fait_collectes
SET duree_reelle_jours = ABS(duree_reelle_jours)
WHERE duree_reelle_jours < 0;
SELECT COUNT(*) as durees_negatives_apres FROM dwh_facts.fait_collectes WHERE duree_reelle_jours < 0;
SELECT 
    COUNT(*) as nombre_collectes,
    ROUND(AVG(duree_reelle_jours)::numeric, 1) as duree_moyenne,
    MIN(duree_reelle_jours) as duree_min,
    MAX(duree_reelle_jours) as duree_max
FROM dwh_facts.fait_collectes
WHERE duree_reelle_jours IS NOT NULL;
DROP TABLE IF EXISTS dwh_marts_financier.mart_performance_financiere CASCADE;
CREATE TABLE dwh_marts_financier.mart_performance_financiere AS
WITH factures AS (
    SELECT 
        f.facture_id,
        f.montant_total,
        f.est_paye,
        f.delai_paiement_jours,
        f.zone_id,
        f.date_creation,
        EXTRACT(YEAR FROM f.date_creation)::int as annee,
        EXTRACT(MONTH FROM f.date_creation)::int as mois,
        EXTRACT(QUARTER FROM f.date_creation)::int as trimestre
    FROM dwh_facts.fait_factures f
),
collectes AS (
    SELECT 
        c.collecte_id,
        c.montant_a_recouvrer,
        c.montant_total_recouvre,
        c.taux_recouvrement,
        c.duree_reelle_jours,
        EXTRACT(YEAR FROM c.date_debut)::int as annee,
        EXTRACT(QUARTER FROM c.date_debut)::int as trimestre
    FROM dwh_facts.fait_collectes c
),
factures_aggregees AS (
    SELECT
        f.annee,
        f.mois,
        f.trimestre,
        COUNT(DISTINCT f.facture_id) as nombre_factures,
        SUM(f.montant_total) as montant_total_facture,
        SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) as montant_paye,
        SUM(CASE WHEN NOT f.est_paye THEN f.montant_total ELSE 0 END) as montant_impaye,
        ROUND(AVG(COALESCE(f.delai_paiement_jours, 0))::numeric, 2) as delai_moyen_paiement,
        ROUND(
            (SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END)::NUMERIC / 
             NULLIF(SUM(f.montant_total), 0)::NUMERIC * 100), 
            2
        ) as taux_paiement_pct
    FROM factures f
    GROUP BY f.annee, f.mois, f.trimestre
),
collectes_aggregees AS (
    SELECT
        c.annee,
        c.trimestre,
        COUNT(DISTINCT c.collecte_id) as nombre_collectes,
        SUM(c.montant_a_recouvrer) as montant_total_a_recouvrer,
        SUM(CASE WHEN c.montant_total_recouvre > 0 THEN c.montant_total_recouvre ELSE 0 END) as montant_total_recouvre,
        ROUND(AVG(COALESCE(c.taux_recouvrement, 0))::numeric, 2) as taux_recouvrement_moyen,
        ROUND(AVG(ABS(COALESCE(c.duree_reelle_jours, 0)))::numeric, 1) as duree_moyenne_collecte
    FROM collectes c
    GROUP BY c.annee, c.trimestre
)
SELECT
    f.annee,
    f.mois,
    f.trimestre,
    f.nombre_factures,
    f.montant_total_facture,
    f.montant_paye,
    f.montant_impaye,
    f.delai_moyen_paiement,
    f.taux_paiement_pct,
    COALESCE(c.nombre_collectes, 0)::int as nombre_collectes,
    COALESCE(c.montant_total_a_recouvrer, 0) as montant_total_a_recouvrer,
    COALESCE(c.montant_total_recouvre, 0) as montant_total_recouvre,
    COALESCE(c.taux_recouvrement_moyen, 0) as taux_recouvrement_moyen,
    COALESCE(c.duree_moyenne_collecte, 0) as duree_moyenne_collecte
FROM factures_aggregees f
LEFT JOIN collectes_aggregees c 
    ON f.annee = c.annee 
    AND f.trimestre = c.trimestre
ORDER BY f.annee DESC, f.mois DESC;
CREATE INDEX idx_mart_perf_annee ON dwh_marts_financier.mart_performance_financiere(annee);
CREATE INDEX idx_mart_perf_annee_mois ON dwh_marts_financier.mart_performance_financiere(annee, mois);
CREATE INDEX idx_mart_perf_annee_trimestre ON dwh_marts_financier.mart_performance_financiere(annee, trimestre);
SELECT COUNT(*) as nombre_lignes FROM dwh_marts_financier.mart_performance_financiere;
SELECT 
    ROUND(SUM(montant_paye)/1000000000.0, 2) as creances_mds_fcfa,
    SUM(montant_paye)::bigint as creances_fcfa
FROM dwh_marts_financier.mart_performance_financiere;
SELECT 
    ROUND(AVG(duree_moyenne_collecte)::numeric, 1) as duree_moy_jours,
    MIN(duree_moyenne_collecte) as duree_min,
    MAX(duree_moyenne_collecte) as duree_max
FROM dwh_marts_financier.mart_performance_financiere
WHERE duree_moyenne_collecte > 0;
SELECT 
    annee, trimestre,
    ROUND(montant_total_facture/1000000000.0, 2) as factures_mds,
    ROUND(montant_paye/1000000000.0, 2) as recouvre_mds,
    duree_moyenne_collecte as duree_jours,
    ROUND(taux_recouvrement_moyen, 1) as taux_recouvrement_pct
FROM dwh_marts_financier.mart_performance_financiere
WHERE montant_total_facture > 0
ORDER BY annee DESC, trimestre DESC
LIMIT 8;
SELECT '✅ CORRECTIONS APPLIQUEES AVEC SUCCES!' as status;
