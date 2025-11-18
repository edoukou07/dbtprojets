DROP TABLE IF EXISTS dwh.mart_portefeuille_clients CASCADE;

CREATE TABLE dwh.mart_portefeuille_clients AS
WITH entreprises AS (
    SELECT * FROM dwh.dim_entreprises
),
domaines AS (
    SELECT * FROM dwh.dim_domaines_activites
),
factures_stats AS (
    SELECT
        f.entreprise_id,
        COUNT(DISTINCT f.facture_id) as nombre_factures,
        SUM(f.montant_total) as chiffre_affaires_total,
        SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) as ca_paye
    FROM dwh.fait_factures f
    GROUP BY f.entreprise_id
),
attributions_stats AS (
    SELECT
        a.entreprise_id,
        COUNT(DISTINCT a.demande_id) as nombre_demandes
    FROM dwh.fait_attributions a
    GROUP BY a.entreprise_id
),
lots_stats AS (
    SELECT
        l.entreprise_id,
        COUNT(DISTINCT l.lot_id) as nombre_lots_attribues
    FROM dwh.dim_lots l
    WHERE l.est_attribue
    GROUP BY l.entreprise_id
)
SELECT
    e.entreprise_id,
    e.raison_sociale,
    COALESCE(f.nombre_factures, 0) as nombre_factures,
    COALESCE(f.chiffre_affaires_total, 0) as chiffre_affaires_total,
    COALESCE(f.ca_paye, 0) as ca_paye,
    COALESCE(a.nombre_demandes, 0) as nombre_demandes,
    COALESCE(l.nombre_lots_attribues, 0) as nombre_lots_attribues
FROM entreprises e
LEFT JOIN domaines d ON e.domaine_activite_id = d.domaine_id
LEFT JOIN factures_stats f ON e.entreprise_id = f.entreprise_id
LEFT JOIN attributions_stats a ON e.entreprise_id = a.entreprise_id
LEFT JOIN lots_stats l ON e.entreprise_id = l.entreprise_id;

SELECT COUNT(*) as total_clients, COALESCE(SUM(chiffre_affaires_total), 0) as ca_total FROM dwh.mart_portefeuille_clients;
