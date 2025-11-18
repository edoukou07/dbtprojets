
DROP TABLE IF EXISTS dwh_marts_financier.mart_performance_financiere CASCADE;
CREATE TABLE dwh_marts_financier.mart_performance_financiere AS
WITH factures AS (
    SELECT * FROM dwh_facts.fait_factures
),
paiements AS (
    SELECT * FROM dwh_facts.fait_paiements
),
collectes AS (
    SELECT * FROM dwh_facts.fait_collectes
),
entreprises AS (
    SELECT * FROM dwh_dimensions.dim_entreprises
),
zones AS (
    SELECT * FROM dwh_dimensions.dim_zones_industrielles
),
temps AS (
    SELECT * FROM dwh_dimensions.dim_temps
),
factures_aggregees AS (
    SELECT
        t.annee,
        t.mois,
        t.trimestre,
        e.raison_sociale,
        e.domaine_activite_id,
        z.nom_zone,
        COUNT(DISTINCT f.facture_id) as nombre_factures,
        SUM(f.montant_total) as montant_total_facture,
        SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) as montant_paye,
        SUM(CASE WHEN NOT f.est_paye THEN f.montant_total ELSE 0 END) as montant_impaye,
        AVG(f.delai_paiement_jours) as delai_moyen_paiement,
        ROUND(
            (SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END)::NUMERIC / 
             NULLIF(SUM(f.montant_total), 0)::NUMERIC * 100), 
            2
        ) as taux_paiement_pct
    FROM factures f
    JOIN temps t ON f.date_creation_key = t.date_key
    LEFT JOIN entreprises e ON f.entreprise_id = e.entreprise_id
    LEFT JOIN zones z ON z.zone_id = f.zone_id
    GROUP BY 
        t.annee,
        t.mois,
        t.trimestre,
        e.raison_sociale,
        e.domaine_activite_id,
        z.nom_zone
),
paiements_par_collecte AS (
    SELECT
        f.collecte_id,
        t.annee,
        t.trimestre,
        SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) as montant_paye_collecte,
        COUNT(DISTINCT f.facture_id) as nombre_factures_payees
    FROM factures f
    JOIN temps t ON f.date_creation_key = t.date_key
    WHERE f.collecte_id IS NOT NULL
    GROUP BY f.collecte_id, t.annee, t.trimestre
),
collectes_aggregees AS (
    SELECT
        t.annee,
        t.trimestre,
        COUNT(DISTINCT c.collecte_id) as nombre_collectes,
        SUM(c.montant_a_recouvrer) as montant_total_a_recouvrer,
        COALESCE(SUM(pc.montant_paye_collecte), 0) as montant_total_recouvre,
        AVG(c.taux_recouvrement) as taux_recouvrement_moyen,
        AVG(c.duree_reelle_jours) as duree_moyenne_collecte
    FROM collectes c
    JOIN temps t ON c.date_debut_key = t.date_key
    LEFT JOIN paiements_par_collecte pc ON c.collecte_id = pc.collecte_id
        AND t.annee = pc.annee
        AND t.trimestre = pc.trimestre
    GROUP BY 
        t.annee,
        t.trimestre
)
SELECT
    f.*,
    c.nombre_collectes,
    c.montant_total_a_recouvrer,
    c.montant_total_recouvre,
    c.taux_recouvrement_moyen
FROM factures_aggregees f
LEFT JOIN collectes_aggregees c 
    ON f.annee = c.annee 
    AND f.trimestre = c.trimestre;
CREATE INDEX idx_mart_performance_annee ON dwh_marts_financier.mart_performance_financiere(annee);
CREATE INDEX idx_mart_performance_annee_mois ON dwh_marts_financier.mart_performance_financiere(annee, mois);
CREATE INDEX idx_mart_performance_nom_zone ON dwh_marts_financier.mart_performance_financiere(nom_zone);
SELECT 'Mart materialised successfully' AS status;
