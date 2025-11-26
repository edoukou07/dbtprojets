#!/usr/bin/env powershell
# Quick Start - Commandes dBT pour Déploiement
# SIGETI DWH - 12 Nouveaux Indicateurs
# Date: 25 Novembre 2025

# ==============================================================================
# ÉTAPE 1: VALIDATION SYNTAX (< 5 minutes)
# ==============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 1: Validaton Syntax dBT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Vérifier connexion à la base
Write-Host "`n1. Tester connexion à SIGETI database..." -ForegroundColor Yellow
# dbt debug

# Parser tous les models (vérifier syntaxe + dépendances)
Write-Host "`n2. Parser les modèles..." -ForegroundColor Yellow
# dbt parse

Write-Host "`n✅ Si succès: Compilation successful, X nodes parsed" -ForegroundColor Green

# ==============================================================================
# ÉTAPE 2: BUILD PARTIAL (Staging seulement) - 10-15 min
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 2: Build Staging Layer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nConstruction des 8 vues de staging..." -ForegroundColor Yellow
# dbt run --select path:staging
# dbt run --select path:staging --debug  # Pour troubleshoot

Write-Host "`n✅ Attendu:" -ForegroundColor Green
Write-Host "  - 8 vues créées en schema 'staging'" -ForegroundColor Green
Write-Host "  - Pas d'erreur SQL" -ForegroundColor Green

# ==============================================================================
# ÉTAPE 3: BUILD DIMENSIONS - 5 min
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 3: Build Dimensions Layer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nConstruction des 4 dimensions SCD Type 2..." -ForegroundColor Yellow
# dbt run --select path:dimensions

Write-Host "`n✅ Attendu:" -ForegroundColor Green
Write-Host "  - 4 tables créées en schema 'dimensions'" -ForegroundColor Green
Write-Host "  - Avec colonnes dbt_valid_from/to" -ForegroundColor Green

# ==============================================================================
# ÉTAPE 4: BUILD FACTS (Phase 1) - 5-10 min
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 4: Build Fact Tables (Phase 1)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nConstruction des 3 facts pour phase 1..." -ForegroundColor Yellow
# dbt run --select tag:P1 path:facts

Write-Host "`n✅ Attendu:" -ForegroundColor Green
Write-Host "  - fait_infractions (incremental)" -ForegroundColor Green
Write-Host "  - fait_implantations (incremental)" -ForegroundColor Green
Write-Host "  - fait_conventions (incremental)" -ForegroundColor Green

# ==============================================================================
# ÉTAPE 5: BUILD DATA MARTS (Phase 1) - 10-15 min
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 5: Build Data Marts (Phase 1)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nConstruction des 3 marts pour phase 1..." -ForegroundColor Yellow
# dbt run --select tag:P1 path:marts

Write-Host "`n✅ Attendu:" -ForegroundColor Green
Write-Host "  - mart_conformite_infractions" -ForegroundColor Green
Write-Host "  - mart_implantation_suivi" -ForegroundColor Green
Write-Host "  - mart_conventions_validation" -ForegroundColor Green

# ==============================================================================
# ÉTAPE 6: QUALITY TESTS - 5-10 min
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 6: Data Quality Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nTester l'intégrité des données..." -ForegroundColor Yellow
# dbt test --select path:facts

Write-Host "`n✅ Attendu:" -ForegroundColor Green
Write-Host "  - Tous les unique_key tests réussissent" -ForegroundColor Green
Write-Host "  - Tous les not_null tests réussissent" -ForegroundColor Green

# ==============================================================================
# ÉTAPE 7: DOCUMENTATION - 2 min
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 7: Generate Documentation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nGénérer et afficher documentation..." -ForegroundColor Yellow
# dbt docs generate
# dbt docs serve

Write-Host "`n✅ Accéder à: http://localhost:8000" -ForegroundColor Green

# ==============================================================================
# COMMANDES RAPIDES
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "COMMANDES RAPIDES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n# Build complet (tous les modèles):" -ForegroundColor Yellow
Write-Host "dbt run" -ForegroundColor White

Write-Host "`n# Build par phase:" -ForegroundColor Yellow
Write-Host "dbt run --select tag:P1    # Phase 1 (infractions, implantation, DPP)" -ForegroundColor White
Write-Host "dbt run --select tag:P2    # Phase 2 (emplois, créances, indemnisations, RH)" -ForegroundColor White
Write-Host "dbt run --select tag:P3    # Phase 3 (délai appro, API perf, conventions)" -ForegroundColor White

Write-Host "`n# Build par couche:" -ForegroundColor Yellow
Write-Host "dbt run --select path:staging        # 8 vues" -ForegroundColor White
Write-Host "dbt run --select path:dimensions     # 4 dimensions" -ForegroundColor White
Write-Host "dbt run --select path:facts          # 6 facts" -ForegroundColor White
Write-Host "dbt run --select path:marts          # 8 marts" -ForegroundColor White

Write-Host "`n# Build spécifique:" -ForegroundColor Yellow
Write-Host "dbt run --select mart_conformite_infractions   # Un seul mart" -ForegroundColor White
Write-Host "dbt run --select fact_infractions             # Un seul fact" -ForegroundColor White
Write-Host "dbt run --select fait_infractions+            # Model et tout ce qui en dépend" -ForegroundColor White

Write-Host "`n# Tests:" -ForegroundColor Yellow
Write-Host "dbt test                              # Tous les tests" -ForegroundColor White
Write-Host "dbt test --select path:facts          # Tests des facts" -ForegroundColor White
Write-Host "dbt test --select tag:P1              # Tests de Phase 1" -ForegroundColor White

Write-Host "`n# Full refresh (données historiques):" -ForegroundColor Yellow
Write-Host "dbt run --select path:facts --full-refresh       # Reset facts incrementaux" -ForegroundColor White
Write-Host "dbt run --select path:marts --full-refresh       # Reset marts" -ForegroundColor White

Write-Host "`n# Documentation:" -ForegroundColor Yellow
Write-Host "dbt docs generate          # Générer docs" -ForegroundColor White
Write-Host "dbt docs serve             # Serveur à http://localhost:8000" -ForegroundColor White

Write-Host "`n# Debugging:" -ForegroundColor Yellow
Write-Host "dbt run --select stg_infractions --debug              # Verbose logs" -ForegroundColor White
Write-Host "dbt parse                                            # Valider syntax" -ForegroundColor White
Write-Host "dbt run --select path:staging --select-exclude tag:ephemeral   # Sans ephemeral" -ForegroundColor White

# ==============================================================================
# PROCÉDURE DE DÉPLOIEMENT COMPLÈTE
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DÉPLOIEMENT COMPLET (Recommended Order)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host @"

JOUR 1 - Validation & Staging:
  1. dbt parse                          # Vérifier syntax
  2. dbt run --select path:staging      # Build staging
  3. dbt test --select path:staging     # Test staging

JOUR 2 - Dimensions & Facts Phase 1:
  4. dbt run --select path:dimensions   # Build dims
  5. dbt run --select tag:P1 path:facts # Build facts P1
  6. dbt test --select tag:P1 path:facts # Test facts P1

JOUR 3 - Marts Phase 1 & Documentation:
  7. dbt run --select tag:P1 path:marts # Build marts P1
  8. dbt test --select tag:P1           # Test complet P1
  9. dbt docs generate                   # Documentation

JOUR 4+ - Phases 2 & 3 (repeat days 2-3):
  10. dbt run --select tag:P2           # Phase 2
  11. dbt run --select tag:P3           # Phase 3
  12. dbt test                          # Full test

"@ -ForegroundColor Green

# ==============================================================================
# QUERIES DE VALIDATION
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SQL QUERIES DE VALIDATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host @"

# Vérifier création des schemas:
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name LIKE 'staging' OR schema_name LIKE 'facts' 
   OR schema_name LIKE 'marts%' OR schema_name LIKE 'dimensions';

# Compter les vues de staging:
SELECT COUNT(*) as nb_staging_views FROM information_schema.views 
WHERE table_schema = 'staging';
-- Attendu: 8

# Compter les dimensions:
SELECT COUNT(*) as nb_dimensions FROM information_schema.tables 
WHERE table_schema = 'dimensions' AND table_type = 'BASE TABLE';
-- Attendu: 4

# Compter les facts:
SELECT COUNT(*) as nb_facts FROM information_schema.tables 
WHERE table_schema = 'facts' AND table_type = 'BASE TABLE';
-- Attendu: 6

# Compter les marts:
SELECT COUNT(*) as nb_marts FROM information_schema.tables 
WHERE table_schema LIKE 'marts%' AND table_type = 'BASE TABLE';
-- Attendu: 8+

# Vérifier unique keys dans fait_infractions:
SELECT COUNT(*) FROM facts.fait_infractions;
SELECT COUNT(DISTINCT convention_id, infraction_id) FROM facts.fait_infractions;
-- Ces deux nombres doivent être identiques

# Sample data de mart_conformite_infractions:
SELECT * FROM marts_operationnel.mart_conformite_infractions 
ORDER BY annee_mois DESC LIMIT 10;

"@ -ForegroundColor White

# ==============================================================================
# TROUBLESHOOTING
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TROUBLESHOOTING" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host @"

# Erreur: "source 'sigeti' not found"
→ Vérifier sources.yml, s'assurer tables existent dans database

# Erreur: "JSONB parsing error"
→ Vérifier que demandes_attribution.emplois contient valide JSON array

# Erreur: "incremental model... does not have unique_key"
→ dbt run --select path:facts --full-refresh (reset incrementals)

# Erreur: "permission denied for schema"
→ Vérifier user permissions dans PostgreSQL
→ Doit avoir CREATE, INSERT, SELECT sur schemas staging/facts/marts

# Lent pour les tests:
→ dbt test --select path:facts --store-failures  # Debug failures
→ Ajouter WHERE clause pour limiter data

# Vérifier les logs détaillés:
→ cd target/
→ tail -f dbt.log
→ grep ERROR dbt.log

"@ -ForegroundColor Yellow

# ==============================================================================
# MONITORING POST-DÉPLOIEMENT
# ==============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "MONITORING POST-DÉPLOIEMENT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host @"

# Vérifier run times:
dbt run --select path:marts --store-failures | grep "Done in"

# Comparer volume de données:
SELECT 'fait_infractions' as table_name, COUNT(*) as row_count FROM facts.fait_infractions
UNION ALL
SELECT 'mart_conformite_infractions', COUNT(*) FROM marts_operationnel.mart_conformite_infractions;

# Vérifier dernière mise à jour:
SELECT table_name, MAX(dbt_loaded_at) as last_loaded 
FROM (
  SELECT table_name, dbt_loaded_at FROM facts.fait_infractions
  UNION ALL
  SELECT table_name, dbt_updated_at FROM marts_operationnel.mart_conformite_infractions
) t
GROUP BY table_name
ORDER BY last_loaded DESC;

# Monitor refresh times dans la duré:
dbt run --select path:marts --explain  # Montrer plans d'exécution

"@ -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ PRÊT POUR DÉPLOIEMENT!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
