-- Script pour trouver les données qui déclenchent des alertes
-- Exécutez ces requêtes pour voir quelles zones génèreront des alertes

-- ===================================
-- 1. ALERTES FINANCIÈRES
-- ===================================

-- Zones avec impayés critiques (>= 40%)
SELECT 
    nom_zone,
    taux_paiement_pct,
    (100 - taux_paiement_pct) as taux_impaye_pct,
    ca_impaye,
    '🔴 CRITIQUE - Impayés > 40%' as alerte
FROM dwh_marts_financier.mart_performance_financiere
WHERE annee = EXTRACT(YEAR FROM CURRENT_DATE)
  AND (100 - taux_paiement_pct) >= 40
ORDER BY taux_impaye_pct DESC;

-- Zones avec impayés warning (25-39%)
SELECT 
    nom_zone,
    taux_paiement_pct,
    (100 - taux_paiement_pct) as taux_impaye_pct,
    ca_impaye,
    '🟠 WARNING - Impayés 25-39%' as alerte
FROM dwh_marts_financier.mart_performance_financiere
WHERE annee = EXTRACT(YEAR FROM CURRENT_DATE)
  AND (100 - taux_paiement_pct) >= 25
  AND (100 - taux_paiement_pct) < 40
ORDER BY taux_impaye_pct DESC;

-- Zones avec délais de paiement critiques (>= 90 jours)
SELECT 
    nom_zone,
    delai_moyen_paiement_jours,
    '🔴 CRITIQUE - Délai > 90 jours' as alerte
FROM dwh_marts_financier.mart_performance_financiere
WHERE annee = EXTRACT(YEAR FROM CURRENT_DATE)
  AND delai_moyen_paiement_jours >= 90
ORDER BY delai_moyen_paiement_jours DESC;

-- Zones avec délais de paiement warning (60-89 jours)
SELECT 
    nom_zone,
    delai_moyen_paiement_jours,
    '🟠 WARNING - Délai 60-89 jours' as alerte
FROM dwh_marts_financier.mart_performance_financiere
WHERE annee = EXTRACT(YEAR FROM CURRENT_DATE)
  AND delai_moyen_paiement_jours >= 60
  AND delai_moyen_paiement_jours < 90
ORDER BY delai_moyen_paiement_jours DESC;

-- ===================================
-- 2. ALERTES D'OCCUPATION
-- ===================================

-- Zones avec occupation critique basse (< 30%)
SELECT 
    nom_zone,
    taux_occupation_pct,
    lots_disponibles,
    nombre_total_lots,
    '🔴 CRITIQUE - Occupation < 30%' as alerte
FROM dwh_marts_occupation.mart_occupation_zones
WHERE taux_occupation_pct < 30
ORDER BY taux_occupation_pct ASC;

-- Zones avec occupation warning basse (30-49%)
SELECT 
    nom_zone,
    taux_occupation_pct,
    lots_disponibles,
    nombre_total_lots,
    '🟠 WARNING - Occupation 30-49%' as alerte
FROM dwh_marts_occupation.mart_occupation_zones
WHERE taux_occupation_pct >= 30 
  AND taux_occupation_pct < 50
ORDER BY taux_occupation_pct ASC;

-- Zones saturées (>= 95%)
SELECT 
    nom_zone,
    taux_occupation_pct,
    lots_disponibles,
    nombre_total_lots,
    '🔴 CRITIQUE - Saturation >= 95%' as alerte
FROM dwh_marts_occupation.mart_occupation_zones
WHERE taux_occupation_pct >= 95
ORDER BY taux_occupation_pct DESC;

-- ===================================
-- 3. ALERTES CLIENTS À RISQUE
-- ===================================

-- Clients avec niveau de risque Élevé ou Critique
SELECT 
    raison_sociale,
    niveau_risque,
    taux_paiement_pct,
    ca_impaye,
    nombre_factures_retard,
    '🚨 Client à Risque' as alerte
FROM dwh_marts_clients.mart_portefeuille_clients
WHERE niveau_risque IN ('Élevé', 'Critique')
   OR taux_paiement_pct < 60
ORDER BY ca_impaye DESC NULLS LAST
LIMIT 20;

-- ===================================
-- 4. RÉSUMÉ DES ALERTES POTENTIELLES
-- ===================================

-- Comptage par type d'alerte
SELECT 
    'Impayés critiques (>40%)' as type_alerte,
    COUNT(*) as nombre
FROM dwh_marts_financier.mart_performance_financiere
WHERE annee = EXTRACT(YEAR FROM CURRENT_DATE)
  AND (100 - taux_paiement_pct) >= 40

UNION ALL

SELECT 
    'Impayés warning (25-39%)',
    COUNT(*)
FROM dwh_marts_financier.mart_performance_financiere
WHERE annee = EXTRACT(YEAR FROM CURRENT_DATE)
  AND (100 - taux_paiement_pct) >= 25
  AND (100 - taux_paiement_pct) < 40

UNION ALL

SELECT 
    'Délais paiement critiques (>90j)',
    COUNT(*)
FROM dwh_marts_financier.mart_performance_financiere
WHERE annee = EXTRACT(YEAR FROM CURRENT_DATE)
  AND delai_moyen_paiement_jours >= 90

UNION ALL

SELECT 
    'Occupation critique (<30%)',
    COUNT(*)
FROM dwh_marts_occupation.mart_occupation_zones
WHERE taux_occupation_pct < 30

UNION ALL

SELECT 
    'Occupation warning (30-49%)',
    COUNT(*)
FROM dwh_marts_occupation.mart_occupation_zones
WHERE taux_occupation_pct >= 30 
  AND taux_occupation_pct < 50

UNION ALL

SELECT 
    'Zones saturées (>=95%)',
    COUNT(*)
FROM dwh_marts_occupation.mart_occupation_zones
WHERE taux_occupation_pct >= 95

UNION ALL

SELECT 
    'Clients à risque',
    COUNT(*)
FROM dwh_marts_clients.mart_portefeuille_clients
WHERE niveau_risque IN ('Élevé', 'Critique')
   OR taux_paiement_pct < 60;
