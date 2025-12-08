# Configuration Prefect - Phase 2 Marts Integration

## Overview

Le workflow Prefect a été mis à jour pour intégrer les 4 nouveaux marts Phase 2:
- **mart_implantation_suivi**: Suivi des implantations par zone
- **mart_indemnisations**: Indemnisations par zone et statut  
- **mart_emplois_crees**: Emplois créés par type et statut
- **mart_creances_agees**: Créances âgées par tranche d'ancienneté

## Architecture

### Flows

#### 1. DBT Pipeline (dbt_pipeline_flow)
- **Fréquence**: Toutes les 10 minutes
- **Tags**: `dbt`, `sigeti`, `production`, `full-pipeline`
- **Étapes**:
  1. Vérification de connexion DB
  2. DBT Debug
  3. Staging
  4. Dimensions
  5. Facts
  6. Marts
  7. Tests de qualité

#### 2. Phase 2 Refresh (phase2_dashboards_refresh_flow) [NEW]
- **Fréquence**: Toutes les 3 heures (02:30, 05:30, 08:30, etc. UTC)
- **Tags**: `phase2`, `dashboards`, `nouveaux-marts`, `production`
- **Étapes**:
  1. Exécution des modèles Staging Phase 2
  2. Construction des Facts Phase 2
  3. Exécution des Marts Phase 2
  4. Tests de qualité (tag:P2)
  5. Validation des données
  6. Invalidation du cache API
  7. Logging des métadonnées

### Tasks Phase 2

#### run_phase2_staging()
- Exécute: `stg_implantations`, `stg_indemnisations`, `stg_emplois_crees`
- Timeout: 120 secondes
- Retries: 1

#### run_phase2_facts()
- Exécute: `fait_implantations`, `fait_indemnisations`, `fait_emplois_crees`, `fait_factures`
- Timeout: 120 secondes
- Retries: 1

#### run_phase2_marts()
- Exécute: `mart_implantation_suivi`, `mart_indemnisations`, `mart_emplois_crees`, `mart_creances_agees`
- Timeout: 120 secondes
- Retries: 1

#### validate_phase2_data()
- Valide les données de chaque mart:
  - Compte de lignes
  - Colonnes NULL
  - Cohérence des données
- Retourne un dictionnaire de résultats (mart -> bool)

#### run_phase2_tests()
- Exécute tous les tests DBT avec le tag `P2`
- Timeout: 120 secondes
- Retries: 1

#### invalidate_api_cache()
- Appelle les endpoints API pour forcer la création du cache
- Endpoints: `/api/implantation-suivi/summary`, `/api/indemnisations/summary`, etc.
- Base URL: `http://localhost:8000` (configurable via `API_BASE_URL`)

#### log_phase2_refresh()
- Enregistre les métadonnées du refresh dans `dbt_refresh_log`
- Captures: succès, marts mis à jour, notes de validation

## Scheduling

### Configuration YAML

**Fichier**: `prefect/deployments/schedule_config.yaml`

```yaml
# Phase 2 - Nouveaux Marts Refresh
- name: phase2-dashboards-refresh
  flow: phase2_dashboards_refresh_flow
  schedule:
    cron: "30 2,5,8,11,14,17,20,23 * * *"  # Toutes les 3 heures
  tags:
    - production
    - phase2
    - dashboards
  notifications:
    - type: email (on FAILED)
    - type: slack (on FAILED)
```

**Intervalles de rafraîchissement**:
- 02:30 UTC
- 05:30 UTC
- 08:30 UTC
- 11:30 UTC
- 14:30 UTC
- 17:30 UTC
- 20:30 UTC
- 23:30 UTC

## Déploiement

### Option 1: Déployer Phase 2 seul

```bash
python prefect/deployments/deploy_dbt_pipeline.py phase2
```

**Output**:
```
DEPLOYMENT PHASE 2 DASHBOARDS
========================================
Nom: phase2-refresh-2h30
Intervalle: Toutes les 2 heures 30 minutes
Marts: implantation_suivi, indemnisations, emplois_crees, creances_agees
Status: Démarrage du serveur de flow...

Dashboard Prefect: http://127.0.0.1:4200
```

### Option 2: Déployer le pipeline DBT principal

```bash
python prefect/deployments/deploy_dbt_pipeline.py main
```

### Option 3: Déployer les deux

```bash
python prefect/deployments/deploy_dbt_pipeline.py both
```

## Validation des Données

### Checks Phase 2

Chaque mart est validé sur:

**mart_implantation_suivi**:
- Clés: `zone_id`, `annee`, `mois`
- Min rows: 0
- Max rows: 50,000
- Expected lag: 3 heures

**mart_indemnisations**:
- Clés: `zone_id`, `annea`, `mois`
- Min rows: 0 (peut être vide si source vide)
- Max rows: 50,000
- Expected lag: 3 heures

**mart_emplois_crees**:
- Clés: `zone_id`, `annea`, `mois`
- Min rows: 0
- Max rows: 100,000
- Expected lag: 3 heures

**mart_creances_agees**:
- Clés: `tranche_anciennete`, `niveau_risque`
- Min rows: 0
- Max rows: 50,000
- Expected lag: 3 heures

### Validation Queries

```sql
-- Exemple pour mart_implantation_suivi
SELECT 
    COUNT(*) as row_count,
    COUNT(CASE WHEN zone_id IS NULL THEN 1 END) as null_zones
FROM dwh_marts_operationnel.mart_implantation_suivi
```

**Critères d'acceptation**:
- NULL count < 10% du total (sauf cas spéciaux)
- Status VALID ou WARNING
- Alerte EMAIL/SLACK si INVALID

## Monitoring & Alertes

### Notifications

**Email** (on FAILED):
- Recipient: admin@sigeti.local
- Event: Flow execution failure

**Slack** (on FAILED):
- Channel: #phase2-alerts
- Event: Flow execution failure

### Logging

- **Logs**: `./logs/prefect_phase2.log`
- **Database**: Table `dbt_refresh_log`
- **Retention**: 90 jours
- **Level**: INFO

### Metadata Table

```sql
CREATE TABLE dbt_refresh_log (
    refresh_id SERIAL PRIMARY KEY,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    models_updated INTEGER,
    rows_inserted INTEGER,
    execution_time_seconds NUMERIC,
    notes TEXT
);
```

**Exemple d'enregistrement**:
```
refresh_id: 42
run_date: 2025-12-04 14:30:00
success: true
models_updated: 4
notes: "Phase 2 refresh - 4/4 marts validated"
```

## API Integration

### Cache Invalidation

Le flow invalide le cache API après chaque refresh:

```python
endpoints = [
    '/api/implantation-suivi/summary',
    '/api/indemnisations/summary',
    '/api/emplois-crees/summary',
    '/api/creances-agees/summary'
]
```

**Comportement**:
- Appelle chaque endpoint pour forcer la création du cache
- Status 200 = cache invalidé
- Log WARNING si endpoint inaccessible
- Continue même si un endpoint échoue

## Fichiers Modifiés

### Nouveaux fichiers
- `prefect/flows/phase2_dashboards_refresh.py` - Nouveau flow complet

### Fichiers mis à jour
- `prefect/deployments/deploy_dbt_pipeline.py` - Ajout de `deploy_phase2_dashboards()`
- `prefect/deployments/schedule_config.yaml` - Ajout de la section Phase 2

## Performance

### Durée estimée par étape
- Staging Phase 2: ~30-40 secondes
- Facts Phase 2: ~40-50 secondes
- Marts Phase 2: ~40-50 secondes
- Tests Phase 2: ~20-30 secondes
- Validation: ~10-15 secondes
- Cache Invalidation: ~5-10 secondes

**Total estimé**: ~3-4 minutes par flow

### Ressources
- CPU: 2 cores (configurable)
- Memory: 4 GB (configurable)
- Disk: 10 GB (configurable)
- Threads DBT: 8 (configurable dans env)

## Troubleshooting

### Flow ne démarre pas
```bash
# Vérifier les imports
python -c "from flows.phase2_dashboards_refresh import phase2_dashboards_refresh_flow"

# Vérifier la configuration
python prefect/deployments/deploy_dbt_pipeline.py phase2
```

### Validation échoue
```bash
# Vérifier les données
SELECT * FROM dwh_marts_operationnel.mart_implantation_suivi;
SELECT COUNT(*) FROM dwh_marts_financier.mart_indemnisations;
```

### Cache API non invalidé
```bash
# Tester manuellement
curl -X GET http://localhost:8000/api/implantation-suivi/summary
```

### Logs non générés
```bash
# Vérifier la table
SELECT * FROM dbt_refresh_log ORDER BY run_date DESC LIMIT 10;
```

## Prochaines étapes

1. ✓ Créer le flow Phase 2
2. ✓ Configurer le scheduling YAML
3. ✓ Mettre à jour les scripts de déploiement
4. ⏳ Pousser vers GitHub
5. ⏳ Créer les composants React pour les dashboards
6. ⏳ Tester end-to-end (Prefect → DBT → API → Frontend)

## Références

- **Prefect Documentation**: https://docs.prefect.io
- **DBT Tags**: Tous les marts Phase 2 sont taggés avec `tag:P2`
- **API Base**: `http://localhost:8000`
- **Dashboard Prefect**: `http://127.0.0.1:4200`
