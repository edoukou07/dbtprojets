
CREATE TABLE dwh_marts_financier.mart_performance_financiere AS
WITH factures AS (
    SELECT 
        f.facture_id,
        f.montant_total,
        f.est_paye,
        f.delai_paiement_jours,
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
        c.montant_recouvre,
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
        ROUND(AVG(COALESCE(EXTRACT(DAY FROM f.delai_paiement_jours), 0))::numeric, 2) as delai_moyen_paiement,
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
        SUM(CASE WHEN c.montant_recouvre > 0 THEN c.montant_recouvre ELSE 0 END) as montant_total_recouvre,
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
