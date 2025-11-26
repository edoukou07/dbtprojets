# Prefect Deployment - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites

```bash
# Verify Python 3.9+ installed
python --version

# Verify PostgreSQL running
psql -h localhost -U sigeti_node_user -d sigeti_node_db -c "SELECT 1"

# Activate virtual environment
cd C:\Users\hynco\Desktop\DWH_SIG
venv\Scripts\Activate.ps1
```

### 2. Install Prefect

```bash
pip install prefect>=2.0.0 psycopg2-binary click pyyaml python-dotenv
```

### 3. Start Prefect Server

```bash
# In one terminal, start Prefect server
prefect server start

# Takes ~30 seconds to start
# Once running, access dashboard at http://localhost:4200
```

### 4. Deploy Flows

```bash
# In another terminal, from workspace root
cd C:\Users\hynco\Desktop\DWH_SIG

# Run startup script for guided setup
python prefect/deployments/startup.py

# Or manual steps:
python prefect/manage_deployments.py setup
```

### 5. Start Agent

```bash
# In third terminal
prefect agent start --work-queue default

# Agent will execute flows on schedule
```

### 6. Monitor Dashboard

```bash
# In fourth terminal (or browser)
python prefect/manage_deployments.py dashboard

# Or visit: http://localhost:4200
```

---

## 📅 Scheduled Runs

| Schedule | Time | What Runs | Duration |
|----------|------|-----------|----------|
| **Daily Incremental** | 2:00 AM UTC | 6 incremental fact tables | ~3-5 min |
| **Weekly Full** | Sunday 3:00 AM UTC | All 37 models + tests | ~10-15 min |

**⏰ TIP**: Convert UTC to your timezone:
- 2:00 AM UTC = 9:00 PM (EST) / 6:00 PM (PST) previous day
- Adjust schedule in `schedule_config.yaml` if needed
- ✅ Stockage des métadonnées dans **PostgreSQL**
- ✅ Logs détaillés et traçabilité complète
- ✅ Gestion des retries automatiques
- ✅ Support des alertes (en option)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           PREFECT INFRASTRUCTURE                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐    ┌──────────────────┐      │
│  │ Prefect Server   │    │ Prefect Worker   │      │
│  │ (Port 4200)      │◄──►│ (Process Pool)   │      │
│  │ - UI/Dashboard   │    │ - Exécute tasks  │      │
│  │ - API            │    │ - Gère retries   │      │
│  │ - Scheduling     │    │ - Logs           │      │
│  └──────┬───────────┘    └────────┬─────────┘      │
│         │                         │                 │
│    PostgreSQL (prefect_db)        │                 │
│    - Flow runs                    │                 │
│    - Task runs                    │                 │
│    - Deployments                  │                 │
│                          ┌────────▼──────────┐      │
│                          │ DBT Pipeline      │      │
│                          │ - Staging         │      │
│                          │ - Dimensions      │      │
│                          │ - Facts           │      │
│                          │ - Marts           │      │
│                          │ - Tests           │      │
│                          └────────┬──────────┘      │
│                                   │                 │
│                          PostgreSQL (sigeti_node_db)│
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Démarrage rapide

### Prérequis
- Python 3.12+ avec venv activé
- PostgreSQL 13+ en cours d'exécution
- Port 4200 disponible (Dashboard Prefect)

### Étape 1 : Activer l'environnement virtuel

```powershell
cd 'C:\Users\hynco\Desktop\DWH_SIG'
.\venv\Scripts\Activate.ps1
```

### Étape 2 : Démarrer le serveur Prefect

**Dans Terminal 1 :**
```powershell
prefect server start
```

Sortie attendue :
```
 ___ ___ ___ ___ ___ ___ _____
| _ \ _ \ __| __| __/ __|_   _|
|  _/   / _|| _|| _| (__  | |
|_| |_|_\___|_| |___\___| |_|

View the API reference documentation at http://127.0.0.1:4200/docs
Check out the dashboard at http://127.0.0.1:4200
```

### Étape 3 : Démarrer un Worker Prefect

**Dans Terminal 2 :**
```powershell
cd 'C:\Users\hynco\Desktop\DWH_SIG'
.\venv\Scripts\Activate.ps1
prefect worker start --pool default
```

Sortie attendue :
```
Starting worker 'work-pool-default'
Worker ready!
Listening for deployments from work pool 'default'...
```

### Étape 4 : Déployer le pipeline

**Dans Terminal 3 :**
```powershell
cd 'C:\Users\hynco\Desktop\DWH_SIG'
.\venv\Scripts\Activate.ps1
python prefect/deployments/deploy_dbt_pipeline.py
```

Sortie attendue :
```
================================================================================
DEPLOYMENT DBT PIPELINE
================================================================================
Nom: dbt-pipeline-10min
Intervalle: Toutes les 10 minutes
Status: Démarrage du serveur de flow...
================================================================================

Dashboard Prefect: http://127.0.0.1:4200
================================================================================
Your flow 'Pipeline DBT SIGETI' is being served and polling for scheduled runs!
```

### ✅ C'est fait !

Le pipeline DBT s'exécute maintenant **toutes les 10 minutes** automatiquement !

---

## ⚙️ Configuration détaillée

### Structure des fichiers

```
prefect/
├── flows/
│   └── dbt_pipeline.py              # Workflow principal
│       ├── verify_database()        # Vérifier connexion PostgreSQL
│       ├── dbt_debug()              # Valider config DBT
│       ├── dbt_run_staging()        # Exécuter staging
│       ├── dbt_run_dimensions()     # Exécuter dimensions
│       ├── dbt_run_facts()          # Exécuter facts
│       ├── dbt_run_marts()          # Exécuter marts
│       └── dbt_test()               # Exécuter tests
│
└── deployments/
    └── deploy_dbt_pipeline.py       # Configuration du déploiement
        ├── Intervalle: 600 sec (10 min)
        ├── Pool: default
        └── Tags: dbt, sigeti, production
```

### Configuration du .env

Le fichier `.env` contient les variables de connexion :

```dotenv
# Configuration Base de Données Source (SIGETI)
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=5432
SOURCE_DB_NAME=sigeti_node_db
SOURCE_DB_USER=postgres
SOURCE_DB_PASSWORD=postgres

# Configuration Base de Données DWH
DBT_PASSWORD=postgres
DWH_DB_HOST=localhost
DWH_DB_PORT=5432
DWH_DB_NAME=sigeti_node_db
DWH_DB_USER=postgres

# Configuration Prefect
PREFECT_API_URL=http://127.0.0.1:4200/api
PREFECT_API_DATABASE_CONNECTION_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/prefect_db
```

### Modifier la fréquence d'exécution

**Éditer `prefect/deployments/deploy_dbt_pipeline.py` :**

```python
# Modifier la ligne :
dbt_pipeline_flow.serve(
    interval=600,  # Changer ici
    # 60 = 1 minute
    # 300 = 5 minutes
    # 600 = 10 minutes
    # 1800 = 30 minutes
    # 3600 = 1 heure
)
```

Puis redéployer :
```powershell
python prefect/deployments/deploy_dbt_pipeline.py
```

---

## 📚 Commandes utiles

### Gestion des flows

```powershell
# Lister les flows déployés
prefect flow ls

# Voir les détails d'un flow
prefect flow inspect 'Pipeline DBT SIGETI'

# Voir l'historique des exécutions
prefect flow-run ls

# Voir les détails d'une exécution
prefect flow-run inspect <flow_run_id>
```

### Gestion des workers

```powershell
# Lister les workers
prefect worker ls

# Voir les détails d'un worker
prefect worker inspect <worker_id>

# Arrêter tous les workers
prefect worker pause-all
```

### Gestion des work pools

```powershell
# Lister les work pools
prefect work-pool ls

# Créer un work pool (déjà créé par défaut)
prefect work-pool create default --type process

# Voir les détails d'un work pool
prefect work-pool inspect default
```

### Exécution manuelle

```powershell
# Déclencher une exécution manuelle
prefect deployment run 'Pipeline DBT SIGETI/dbt-pipeline-10min'

# Voir les logs en temps réel
prefect flow-run watch <flow_run_id>
```

### Configuration Prefect

```powershell
# Voir la configuration actuelle
prefect config view

# Mettre à jour une variable
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api

# Réinitialiser la configuration par défaut
prefect config unset PREFECT_API_URL
```

---

## 🎨 Dashboard

### Accès

**URL :** http://127.0.0.1:4200

### Fonctionnalités principales

1. **Flows**
   - Voir tous les workflows déployés
   - Consulter le code du flow
   - Voir les exécutions passées

2. **Deployments**
   - Configuration de planification
   - Historique des exécutions
   - Statut du deployment

3. **Flow Runs**
   - Voir tous les exécutions
   - Consulter les logs détaillés
   - Voir le statut (Running, Completed, Failed)
   - Temps d'exécution

4. **Task Runs**
   - Détails de chaque tâche
   - Logs par tâche
   - Durée d'exécution

5. **Work Pools & Workers**
   - État des workers
   - Capacité disponible
   - Utilisation des ressources

---

## 🔧 Dépannage

### Problème : Worker ne démarre pas

**Symptôme :** `Connection refused`

**Solution :**
```powershell
# Vérifier que le serveur Prefect est lancé
# Terminal 1 doit avoir : prefect server start

# Vérifier le port 4200
netstat -ano | findstr :4200

# Relancer le worker
prefect worker start --pool default
```

### Problème : Flow runs bloqués en "Late"

**Symptôme :** Les tâches affichent "Late" mais ne s'exécutent pas

**Solution :**
1. Vérifier que le worker est lancé (Terminal 2)
2. Relancer le worker : `prefect worker start --pool default`
3. Redéployer le pipeline : `python prefect/deployments/deploy_dbt_pipeline.py`

### Problème : Erreur de connexion PostgreSQL

**Symptôme :** `Impossible de se connecter à PostgreSQL`

**Solution :**
```powershell
# Vérifier les variables .env
cat .env | findstr DB_

# Tester la connexion
psql -h localhost -U postgres -d sigeti_node_db -c "SELECT 1;"

# Vérifier que PostgreSQL s'exécute
tasklist | findstr postgres
```

### Problème : Base de données Prefect verrouillée

**Symptôme :** `database is locked` dans les logs

**Solution :**
```powershell
# Arrêter tous les processus Prefect
Get-Process python | Stop-Process -Force

# Nettoyer la base SQLite (si utilisé)
$prefectHome = "$env:USERPROFILE\.prefect"
Remove-Item "$prefectHome\prefect.db" -Force

# Redémarrer
prefect server start
```

### Problème : DBT ne trouve pas les profiles

**Symptôme :** `ERROR not found` lors de `dbt debug`

**Solution :**
- Vérifier que `profiles.yml` est à la racine du projet
- Vérifier que `dbt_project.yml` existe
- Exécuter : `dbt debug --project-dir . --profiles-dir .`

---

## 📊 Métriques et monitoring

### Logs disponibles

Les logs sont stockés à plusieurs endroits :

1. **Dashboard Prefect** → http://127.0.0.1:4200
   - Flow runs → Task runs → Logs

2. **Terminal Worker**
   - Affichage en temps réel des exécutions

3. **Base PostgreSQL (prefect_db)**
   - Historique complet des exécutions
   - Durées d'exécution
   - Statuts des tâches

### Requêtes SQL utiles

```sql
-- Voir les dernières exécutions
SELECT * FROM flow_runs 
ORDER BY start_time DESC 
LIMIT 10;

-- Voir les tâches échouées
SELECT * FROM task_runs 
WHERE state_type = 'FAILED' 
ORDER BY end_time DESC;

-- Temps d'exécution moyen
SELECT 
    AVG(EXTRACT(EPOCH FROM (end_time - start_time))) as avg_duration_sec
FROM flow_runs
WHERE state_type = 'COMPLETED';
```

---

## 🔄 Maintenance

### Arrêter le pipeline

```powershell
# Appuyer sur Ctrl+C dans Terminal 3 (deployment)
# Puis dans Terminal 2 (worker)
# Puis dans Terminal 1 (server)

# Ou directement :
Get-Process python | Stop-Process -Force
```

### Redémarrer le pipeline

```powershell
# Redémarrer avec une nouvelle fréquence ou configuration
python prefect/deployments/deploy_dbt_pipeline.py
```

### Nettoyer les anciennes exécutions

```sql
-- Supprimer les exécutions plus vieilles que 30 jours
DELETE FROM flow_runs 
WHERE created < NOW() - INTERVAL '30 days';
```

---

## 📖 Ressources

- [Documentation Prefect 3.x](https://docs.prefect.io/)
- [Prefect Cloud](https://app.prefect.cloud/)
- [GitHub Prefect](https://github.com/PrefectHQ/prefect)

---

## ✅ Checklist de démarrage

- [ ] Environnement virtuel activé
- [ ] PostgreSQL en cours d'exécution
- [ ] Variables .env configurées
- [ ] Terminal 1 : `prefect server start` ✅
- [ ] Terminal 2 : `prefect worker start --pool default` ✅
- [ ] Terminal 3 : `python prefect/deployments/deploy_dbt_pipeline.py` ✅
- [ ] Dashboard Prefect accessible à http://127.0.0.1:4200
- [ ] Première exécution lancée (voir "Flow Runs")

---

**Créé le :** 17 novembre 2025  
**Version :** 1.0.0  
**Statut :** ✅ Production
