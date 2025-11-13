-- =====================================================================
-- CRÉATION D'INDEX POUR OPTIMISATION DES PERFORMANCES
-- Projet: SIGETI DWH
-- Date: 2025-11-13
-- =====================================================================

\echo '🚀 Création des index pour optimisation des performances...'
\echo ''

-- ===== INDEX SUR LES TABLES DE FAITS =====

\echo '📊 Index sur fait_attributions...'

-- Index sur les clés étrangères (améliore les jointures)
CREATE INDEX IF NOT EXISTS idx_fait_attr_entreprise 
    ON dwh_facts.fait_attributions(entreprise_key);

CREATE INDEX IF NOT EXISTS idx_fait_attr_lot 
    ON dwh_facts.fait_attributions(lot_key);

CREATE INDEX IF NOT EXISTS idx_fait_attr_zone 
    ON dwh_facts.fait_attributions(zone_key);

CREATE INDEX IF NOT EXISTS idx_fait_attr_domaine 
    ON dwh_facts.fait_attributions(domaine_key);

-- Index sur la date (filtres fréquents)
CREATE INDEX IF NOT EXISTS idx_fait_attr_date_demande 
    ON dwh_facts.fait_attributions(date_demande_key);

CREATE INDEX IF NOT EXISTS idx_fait_attr_created_at 
    ON dwh_facts.fait_attributions(created_at);

-- Index composite pour requêtes d'agrégation
CREATE INDEX IF NOT EXISTS idx_fait_attr_entreprise_date 
    ON dwh_facts.fait_attributions(entreprise_key, date_demande_key);

\echo '✅ Index fait_attributions créés'
\echo ''

-- ===== INDEX SUR fait_factures =====

\echo '💰 Index sur fait_factures...'

CREATE INDEX IF NOT EXISTS idx_fait_fact_entreprise 
    ON dwh_facts.fait_factures(entreprise_key);

CREATE INDEX IF NOT EXISTS idx_fait_fact_lot 
    ON dwh_facts.fait_factures(lot_key);

CREATE INDEX IF NOT EXISTS idx_fait_fact_date_creation 
    ON dwh_facts.fait_factures(date_creation_key);

CREATE INDEX IF NOT EXISTS idx_fait_fact_date_emission 
    ON dwh_facts.fait_factures(date_emission_key);

-- Index pour les requêtes de paiement
CREATE INDEX IF NOT EXISTS idx_fait_fact_statut_paiement 
    ON dwh_facts.fait_factures(statut_paiement) 
    WHERE statut_paiement IN ('impaye', 'partiellement_paye');

CREATE INDEX IF NOT EXISTS idx_fait_fact_montant 
    ON dwh_facts.fait_factures(montant_facture) 
    WHERE montant_facture > 0;

\echo '✅ Index fait_factures créés'
\echo ''

-- ===== INDEX SUR fait_paiements =====

\echo '💳 Index sur fait_paiements...'

CREATE INDEX IF NOT EXISTS idx_fait_paie_entreprise 
    ON dwh_facts.fait_paiements(entreprise_key);

CREATE INDEX IF NOT EXISTS idx_fait_paie_facture 
    ON dwh_facts.fait_paiements(facture_key);

CREATE INDEX IF NOT EXISTS idx_fait_paie_date 
    ON dwh_facts.fait_paiements(date_paiement_key);

-- Index pour suivi des paiements
CREATE INDEX IF NOT EXISTS idx_fait_paie_mode 
    ON dwh_facts.fait_paiements(mode_paiement);

\echo '✅ Index fait_paiements créés'
\echo ''

-- ===== INDEX SUR fait_collectes =====

\echo '🏭 Index sur fait_collectes...'

CREATE INDEX IF NOT EXISTS idx_fait_coll_zone 
    ON dwh_facts.fait_collectes(zone_key);

CREATE INDEX IF NOT EXISTS idx_fait_coll_date_debut 
    ON dwh_facts.fait_collectes(date_debut_key);

CREATE INDEX IF NOT EXISTS idx_fait_coll_date_fin 
    ON dwh_facts.fait_collectes(date_fin_prevue_key);

\echo '✅ Index fait_collectes créés'
\echo ''

-- ===== INDEX SUR LES DIMENSIONS =====

\echo '📁 Index sur dim_temps...'

-- Index sur la date complète (requêtes par date exacte)
CREATE INDEX IF NOT EXISTS idx_dim_temps_date 
    ON dwh_dimensions.dim_temps(date);

-- Index sur année/mois (agrégations mensuelles)
CREATE INDEX IF NOT EXISTS idx_dim_temps_annee_mois 
    ON dwh_dimensions.dim_temps(annee, mois);

-- Index sur trimestre (reporting trimestriel)
CREATE INDEX IF NOT EXISTS idx_dim_temps_annee_trimestre 
    ON dwh_dimensions.dim_temps(annee, trimestre);

\echo '✅ Index dim_temps créés'
\echo ''

\echo '📁 Index sur dim_entreprises...'

-- Index sur le nom (recherches fréquentes)
CREATE INDEX IF NOT EXISTS idx_dim_entr_nom 
    ON dwh_dimensions.dim_entreprises(nom_entreprise);

-- Index sur l'email (lookups)
CREATE INDEX IF NOT EXISTS idx_dim_entr_email 
    ON dwh_dimensions.dim_entreprises(email);

-- Index texte pour recherche full-text
CREATE INDEX IF NOT EXISTS idx_dim_entr_nom_trgm 
    ON dwh_dimensions.dim_entreprises 
    USING gin (nom_entreprise gin_trgm_ops);

\echo '✅ Index dim_entreprises créés'
\echo ''

\echo '📁 Index sur dim_lots...'

-- Index sur la zone (filtres par zone)
CREATE INDEX IF NOT EXISTS idx_dim_lots_zone 
    ON dwh_dimensions.dim_lots(zone_id);

-- Index sur le statut (lots disponibles/occupés)
CREATE INDEX IF NOT EXISTS idx_dim_lots_statut 
    ON dwh_dimensions.dim_lots(statut);

-- Index sur la superficie (recherches par taille)
CREATE INDEX IF NOT EXISTS idx_dim_lots_superficie 
    ON dwh_dimensions.dim_lots(superficie) 
    WHERE superficie > 0;

\echo '✅ Index dim_lots créés'
\echo ''

-- ===== STATISTIQUES =====

\echo '📊 Mise à jour des statistiques PostgreSQL...'

ANALYZE dwh_facts.fait_attributions;
ANALYZE dwh_facts.fait_factures;
ANALYZE dwh_facts.fait_paiements;
ANALYZE dwh_facts.fait_collectes;
ANALYZE dwh_dimensions.dim_temps;
ANALYZE dwh_dimensions.dim_entreprises;
ANALYZE dwh_dimensions.dim_lots;
ANALYZE dwh_dimensions.dim_zones_industrielles;
ANALYZE dwh_dimensions.dim_domaines_activites;

\echo '✅ Statistiques mises à jour'
\echo ''

-- ===== RÉSUMÉ =====

\echo '================================================'
\echo ' ✅ Création des index terminée avec succès!'
\echo '================================================'
\echo ''
\echo '📈 Impact attendu:'
\echo '   - Jointures: 50-80% plus rapides'
\echo '   - Filtres par date: 70-90% plus rapides'
\echo '   - Agrégations: 40-60% plus rapides'
\echo ''
\echo '💡 Prochaine étape: Analyser les requêtes avec EXPLAIN ANALYZE'
\echo ''
