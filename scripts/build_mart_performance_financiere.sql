
DROP TABLE IF EXISTS dwh_marts_financier.mart_performance_financiere CASCADE;
CREATE TABLE dwh_marts_financier.mart_performance_financiere AS
WITH factures as (
    SELECT
        f.facture_id,
        f.montant_total,
        f.est_paye,
        f.delai_paiement_jours,
        f.date_creation,
        EXTRACT(YEAR FROM f.date_creation)::INT as annee,
        EXTRACT(MONTH FROM f.date_creation)::INT as mois,
        EXTRACT(QUARTER FROM f.date_creation)::INT as trimestre
    FROM dwh_facts.fait_factures f
),
collectes as (
    SELECT
        c.collecte_id,
        c.montant_a_recouvrer,
        c.montant_recouvre,
        c.taux_recouvrement,
        c.duree_reelle_jours,
        EXTRACT(YEAR FROM c.date_debut)::INT as annee,
        EXTRACT(QUARTER FROM c.date_debut)::INT as trimestre
    FROM dwh_facts.fait_collectes c
),
factures_aggregees as (
    SELECT
        f.annee,
        f.mois,
        f.trimestre,
        COUNT(DISTINCT f.facture_id) as nombre_factures,
        SUM(f.montant_total) as montant_total_facture,
        SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) as montant_paye,
        SUM(CASE WHEN NOT f.est_paye THEN f.montant_total ELSE 0 END) as montant_impaye,
        ROUND(AVG(COALESCE(EXTRACT(DAY FROM f.delai_paiement_jours), 0))::NUMERIC, 2) as delai_moyen_paiement,
        ROUND(100.0 * SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) / NULLIF(SUM(f.montant_total), 0), 2) as taux_paiement_pct
    FROM factures f
    GROUP BY f.annee, f.mois, f.trimestre
),
collectes_aggregees as (
    SELECT
        c.annee,
        c.trimestre,
        COUNT(DISTINCT c.collecte_id) as nombre_collectes,
        SUM(c.montant_a_recouvrer) as montant_total_a_recouvrer,
        SUM(c.montant_recouvre) as montant_total_recouvre,
        ROUND(100.0 * AVG(COALESCE(c.taux_recouvrement, 0)), 2) as taux_recouvrement_moyen,
        ROUND(AVG(ABS(COALESCE(c.duree_reelle_jours, 0)))::NUMERIC, 1) as duree_moyenne_collecte
    FROM collectes c
    GROUP BY c.annee, c.trimestre
)
SELECT
    COALESCE(f.annee, c.annee) as annee,
    f.mois,
    COALESCE(f.trimestre, c.trimestre) as trimestre,
    COALESCE(f.nombre_factures, 0) as nombre_factures,
    COALESCE(f.montant_total_facture, 0) as montant_total_facture,
    COALESCE(f.montant_paye, 0) as montant_paye,
    COALESCE(f.montant_impaye, 0) as montant_impaye,
    COALESCE(f.delai_moyen_paiement, 0) as delai_moyen_paiement,
    COALESCE(f.taux_paiement_pct, 0) as taux_paiement_pct,
    COALESCE(c.nombre_collectes, 0) as nombre_collectes,
    COALESCE(c.montant_total_a_recouvrer, 0) as montant_total_a_recouvrer,
    COALESCE(c.montant_total_recouvre, 0) as montant_total_recouvre,
    COALESCE(c.taux_recouvrement_moyen, 0) as taux_recouvrement_moyen,
    COALESCE(c.duree_moyenne_collecte, 0) as duree_moyenne_collecte
FROM factures_aggregees f
FULL OUTER JOIN collectes_aggregees c 
    ON f.annee = c.annee AND f.trimestre = c.trimestre
ORDER BY annee, mois, trimestre;
CREATE INDEX idx_mart_performance_annee 
    ON dwh_marts_financier.mart_performance_financiere(annee);
CREATE INDEX idx_mart_performance_annee_mois 
    ON dwh_marts_financier.mart_performance_financiere(annee, mois);
CREATE INDEX idx_mart_performance_annee_trimestre 
    ON dwh_marts_financier.mart_performance_financiere(annee, trimestre);
SELECT 
    'Verification' as check_type,
    COUNT(*) as total_rows,
    COUNT(DISTINCT annee) as annees,
    MIN(duree_moyenne_collecte) as min_duree,
    MAX(duree_moyenne_collecte) as max_duree,
    ROUND(AVG(duree_moyenne_collecte)::NUMERIC, 1) as avg_duree,
    SUM(montant_total_recouvre) / 1000000000.0 as total_creances_mds
FROM dwh_marts_financier.mart_performance_financiere;
