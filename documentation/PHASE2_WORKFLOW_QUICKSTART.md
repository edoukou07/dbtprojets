# Phase 2 Workflow - Quick Start Guide

## 🚀 Déployer le workflow Phase 2

### Option 1: Déployer Phase 2 uniquement
```bash
cd c:\Users\hynco\Desktop\DWH_SIG
python prefect/deployments/deploy_dbt_pipeline.py phase2
```

### Option 2: Déployer les deux workflows (DBT + Phase 2)
```bash
python prefect/deployments/deploy_dbt_pipeline.py both
```

### Option 3: Déployer DBT pipeline seul
```bash
python prefect/deployments/deploy_dbt_pipeline.py main
```

---

## 📊 Monitorer les exécutions

### Dashboard Prefect
```
http://127.0.0.1:4200
```

### Logs en base de données
```sql
-- Voir les dernières exécutions
SELECT * FROM dbt_refresh_log 
ORDER BY run_date DESC 
LIMIT 10;

-- Voir les exécutions échouées
SELECT * FROM dbt_refresh_log 
WHERE success = false 
ORDER BY run_date DESC;

-- Statistiques journalières
SELECT 
    DATE(run_date) as date,
    COUNT(*) as executions,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed
FROM dbt_refresh_log
GROUP BY DATE(run_date)
ORDER BY date DESC;
```

---

## 🔄 Phase 2 Scheduling

**Fréquence**: Toutes les 3 heures UTC
- 02:30 UTC
- 05:30 UTC
- 08:30 UTC
- 11:30 UTC
- 14:30 UTC
- 17:30 UTC
- 20:30 UTC
- 23:30 UTC

**Durée estimée**: 3-4 minutes par exécution

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `PREFECT_PHASE2_CONFIG.md` | Configuration détaillée |
| `PHASE2_PREFECT_IMPLEMENTATION.md` | Résumé de l'implémentation |
| `test_phase2_workflow.py` | Script de validation |

---

## 🎯 Nouveaux marts intégrés

```
✓ mart_implantation_suivi      - Suivi des implantations
✓ mart_indemnisations          - Gestion des indemnisations
✓ mart_emplois_crees           - Emplois créés par type
✓ mart_creances_agees          - Analyse des créances âgées
```

---

## 🔗 API Endpoints

Après chaque refresh, le cache est invalidé via:

- `GET /api/implantation-suivi/summary`
- `GET /api/indemnisations/summary`
- `GET /api/emplois-crees/summary`
- `GET /api/creances-agees/summary`

---

## 📝 Fichiers clés

| Fichier | Lignes | Rôle |
|---------|--------|------|
| `prefect/flows/phase2_dashboards_refresh.py` | 447 | Main flow |
| `prefect/deployments/deploy_dbt_pipeline.py` | 87 | Deployment CLI |
| `prefect/deployments/schedule_config.yaml` | 192 | Scheduling config |
| `models/marts/operationnel/mart_implantation_suivi.sql` | 115 | Mart operationnel |
| `models/marts/financier/mart_indemnisations.sql` | 55 | Mart financier |
| `models/marts/operationnel/mart_emplois_crees.sql` | 56 | Mart operationnel |
| `models/marts/financier/mart_creances_agees.sql` | 72 | Mart financier |

---

## ✅ Validation locale

```bash
# Vérifier que le workflow Phase 2 est valide
python test_phase2_workflow.py

# Exécuter les tests DBT Phase 2
dbt test --select "tag:P2"

# Vérifier les données
dbt test --select "tag:P2" -vv
```

---

## 🐛 Troubleshooting

### Le flow ne démarre pas
```bash
# Vérifier les imports
python -c "from prefect.flows.phase2_dashboards_refresh import phase2_dashboards_refresh_flow"

# Vérifier la configuration
python prefect/deployments/deploy_dbt_pipeline.py phase2
```

### Les données ne s'actualisent pas
```sql
-- Vérifier les dernières exécutions
SELECT * FROM dbt_refresh_log ORDER BY run_date DESC LIMIT 1;

-- Vérifier les données dans les marts
SELECT COUNT(*) as count FROM dwh_marts_operationnel.mart_implantation_suivi;
```

### Cache API non invalidé
```bash
# Tester manuellement
curl -X GET http://localhost:8000/api/implantation-suivi/summary

# Vérifier que le serveur Django est en cours d'exécution
python bi_app/backend/manage.py runserver
```

---

## 📞 Support

Pour des questions sur:
- **Prefect workflow**: Voir `PREFECT_PHASE2_CONFIG.md`
- **DBT models**: Voir `models/marts/`
- **API endpoints**: Voir `bi_app/backend/api/`
- **Implémentation**: Voir `PHASE2_PREFECT_IMPLEMENTATION.md`

---

## 🔄 Cycle de rafraîchissement

```
14:30 UTC: Refresh Phase 2
├─ [1/6] Staging (30-40s)
├─ [2/6] Facts (40-50s)
├─ [3/6] Marts (40-50s)
├─ [4/6] Tests (20-30s)
├─ [5/6] Validation (10-15s)
├─ [6/6] Cache Invalidation (5-10s)
└─ Logging
Total: ~3-4 minutes

14:33 UTC: Refresh complete, waiting for next schedule...
```

---

**Last Updated**: 2025-12-04
**Version**: 1.0.0
**Status**: ✅ Production Ready
