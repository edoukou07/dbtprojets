# Guide de Déploiement - Entrepôt de Données SIGETI

## 📋 Table des Matières
1. [État du Projet](#état-du-projet)
2. [Options de Déploiement](#options-de-déploiement)
3. [Installation des Dépendances](#installation-des-dépendances)
4. [Configuration](#configuration)
5. [Utilisation](#utilisation)
6. [Monitoring](#monitoring)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

---

## ✅ État du Projet

**Statut**: ✅ **PRODUCTION READY**

### Résultats de la dernière exécution:
- **Staging**: 8/8 modèles ✅ (1.44s)
- **Dimensions**: 5/5 tables ✅ (1.27s) - 4,145 lignes
- **Facts**: 4/4 tables ✅ (1.22s)
- **Marts**: 4/4 vues ✅ (1.26s)
- **Tests**: 8/8 validations ✅ (1.06s)
- **Documentation**: Générée ✅ (3.28s)

**Temps total**: ~9 secondes  
**Taux de succès**: 100%

---

## 🚀 Options de Déploiement

### Option 1: Exécution Manuelle (Recommandé pour débuter)

**Avantages**:
- Simple et rapide
- Pas de configuration supplémentaire
- Contrôle total sur l'exécution

**Utilisation**:
```powershell
# Exécuter le pipeline
.\run_pipeline.ps1
```

### Option 2: Planification avec Prefect Server (Recommandé pour production)

**Avantages**:
- Interface web pour monitoring
- Historique des exécutions
- Alertes en cas d'échec
- Logs centralisés

**Configuration**:
```powershell
# 1. Démarrer Prefect Server
prefect server start

# 2. Dans un autre terminal, déployer le flow
.\venv\Scripts\Activate.ps1
python prefect\deployments\deploy_scheduled.py

# 3. Démarrer un agent Prefect
prefect agent start -q default
```

**Accès**: http://localhost:4200 (interface web Prefect)

### Option 3: Planification Windows Task Scheduler (Simple, sans dépendances)

**Avantages**:
- Intégré à Windows
- Pas de serveur à maintenir
- Démarrage automatique

**Configuration**:
```powershell
# Exécuter le script de configuration
.\setup_scheduled_task.ps1

# Vérifier que la tâche est créée
Get-ScheduledTask -TaskName "SIGETI_DWH_Daily_Refresh"
```

**Gestion**:
- Ouvrir: `taskschd.msc` (Planificateur de tâches Windows)
- Rechercher: "SIGETI_DWH_Daily_Refresh"
- Historique visible dans l'onglet "Historique"

---

## 📦 Installation des Dépendances

### Prérequis
- Python 3.12+
- PostgreSQL 13+
- PowerShell 5.1+

### Installation
```powershell
# 1. Créer l'environnement virtuel (déjà fait)
python -m venv venv

# 2. Activer l'environnement
.\venv\Scripts\Activate.ps1

# 3. Installer les packages (déjà fait)
pip install dbt-core==1.10.15 dbt-postgres==1.9.1 prefect==3.6.1 prefect-dbt==0.7.8

# 4. Installer tabulate pour le monitoring
pip install tabulate python-dotenv
```

---

## ⚙️ Configuration

### 1. Variables d'Environnement (.env)

Fichier `.env` à la racine du projet:
```env
# Database Configuration
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=5432
SOURCE_DB_NAME=sigeti_node_db
SOURCE_DB_USER=postgres
SOURCE_DB_PASSWORD=postgres

DWH_DB_HOST=localhost
DWH_DB_PORT=5432
DWH_DB_NAME=sigeti_node_db
DWH_DB_USER=postgres
DBT_PASSWORD=postgres
```

### 2. Configuration dbt (profiles.yml)

Fichier `C:\Users\hynco\.dbt\profiles.yml`:
```yaml
sigeti_dwh:
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: postgres
      password: postgres
      dbname: sigeti_node_db
      schema: dwh
      threads: 4
      client_encoding: utf8
  target: dev
```

### 3. Configuration Critique

**⚠️ IMPORTANT**: L'encodage UTF-8 est **obligatoire** pour gérer les caractères français.

```powershell
# Le script run_pipeline.ps1 configure automatiquement:
$env:PGCLIENTENCODING = "UTF8"
```

---

## 💻 Utilisation

### Exécution Manuelle

```powershell
# Option 1: Script simplifié (RECOMMANDÉ)
.\run_pipeline.ps1

# Option 2: Commande complète
$env:PGCLIENTENCODING="UTF8"
.\venv\Scripts\Activate.ps1
python prefect\flows\sigeti_dwh_flow.py
```

### Exécution avec dbt uniquement

```powershell
# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Exécuter toutes les transformations
dbt run

# Exécuter une couche spécifique
dbt run --select staging
dbt run --select dimensions
dbt run --select facts
dbt run --select marts

# Exécuter les tests
dbt test

# Générer la documentation
dbt docs generate
dbt docs serve  # Ouvre la doc dans le navigateur
```

### Monitoring en Temps Réel

```powershell
# Afficher le tableau de bord
.\venv\Scripts\Activate.ps1
python monitor_dwh.py
```

---

## 📊 Monitoring

### 1. Tableau de Bord Python (monitor_dwh.py)

**Affiche**:
- Nombre de lignes par table/vue
- Taille des objets
- Dernières mises à jour
- Statistiques par couche

**Utilisation**:
```powershell
python monitor_dwh.py
```

### 2. Monitoring via PostgreSQL

```sql
-- Connexion
psql -U postgres -d sigeti_node_db

-- Voir tous les objets du DWH
SELECT 
    schemaname, 
    tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname LIKE 'dwh%'
ORDER BY schemaname, tablename;

-- Compter les lignes dans les faits
SELECT 'fait_attributions' as table, COUNT(*) FROM dwh_facts.fait_attributions
UNION ALL
SELECT 'fait_collectes', COUNT(*) FROM dwh_facts.fait_collectes
UNION ALL
SELECT 'fait_factures', COUNT(*) FROM dwh_facts.fait_factures
UNION ALL
SELECT 'fait_paiements', COUNT(*) FROM dwh_facts.fait_paiements;

-- Vérifier la fraîcheur des données
SELECT 
    'fait_attributions' as table,
    MAX(created_at) as derniere_maj
FROM dwh_facts.fait_attributions;
```

### 3. Monitoring via Prefect UI

Si vous utilisez Prefect Server:
1. Ouvrir http://localhost:4200
2. Onglet "Flow Runs" → voir l'historique
3. Cliquer sur un run → voir les logs détaillés
4. Onglet "Deployments" → voir les planifications

---

## 🔧 Maintenance

### Rafraîchissement des Données

**Fréquence recommandée**: Quotidienne (2:00 AM)

**Mode incrémental**: Les tables de faits (`fait_*`) utilisent une stratégie incrémentale:
- Première exécution: charge toutes les données
- Exécutions suivantes: charge uniquement les nouvelles/modifiées

**Rafraîchissement complet** (si nécessaire):
```powershell
# Option 1: Via dbt
dbt run --full-refresh

# Option 2: Supprimer et recréer
psql -U postgres -d sigeti_node_db -c "DROP SCHEMA dwh CASCADE; CREATE SCHEMA dwh;"
.\run_pipeline.ps1
```

### Nettoyage

```powershell
# Supprimer les fichiers compilés dbt
Remove-Item -Recurse -Force target, dbt_packages, logs

# Reconstruire les packages dbt
dbt deps
```

### Mise à Jour des Modèles

1. Modifier les fichiers `.sql` dans `models/`
2. Tester localement:
   ```powershell
   dbt run --select <nom_du_modele>
   dbt test --select <nom_du_modele>
   ```
3. Exécuter le pipeline complet pour validation

---

## 🐛 Troubleshooting

### Problème: Erreur UTF-8 / Caractères français

**Symptôme**: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9`

**Solution**:
```powershell
# Utiliser le script run_pipeline.ps1 qui configure automatiquement UTF-8
.\run_pipeline.ps1

# Ou définir manuellement
$env:PGCLIENTENCODING="UTF8"
```

### Problème: Connexion PostgreSQL refusée

**Symptôme**: `could not connect to server: Connection refused`

**Solution**:
```powershell
# Vérifier que PostgreSQL est démarré
Get-Service -Name postgresql*

# Démarrer si nécessaire
Start-Service postgresql-x64-13  # Adapter selon votre version

# Tester la connexion
psql -U postgres -d sigeti_node_db -c "SELECT 1;"
```

### Problème: Colonne n'existe pas

**Symptôme**: `ERROR: column "xxx" does not exist`

**Solution**:
1. Vérifier le schéma source:
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'nom_table' AND table_schema = 'public';
   ```
2. Mettre à jour le modèle dbt correspondant
3. Re-exécuter le pipeline

### Problème: Tests dbt échouent

**Symptôme**: `FAIL` dans les tests

**Solution**:
```powershell
# Voir les détails des échecs
dbt test --select <test_name> --store-failures

# Vérifier les données problématiques
psql -U postgres -d sigeti_node_db
SELECT * FROM dwh.dbt_test__audit LIMIT 10;
```

### Problème: Prefect ne trouve pas le flow

**Symptôme**: `Flow not found`

**Solution**:
```powershell
# Re-déployer le flow
python prefect\deployments\deploy_scheduled.py

# Vérifier les déploiements
prefect deployment ls
```

---

## 📚 Ressources

### Documentation
- **dbt**: https://docs.getdbt.com/
- **Prefect**: https://docs.prefect.io/
- **PostgreSQL**: https://www.postgresql.org/docs/

### Fichiers Clés
```
DWH_SIG/
├── run_pipeline.ps1           # Script d'exécution principal
├── monitor_dwh.py             # Tableau de bord monitoring
├── setup_scheduled_task.ps1   # Configuration Windows Task
├── prefect/
│   ├── flows/
│   │   └── sigeti_dwh_flow.py    # Orchestration Prefect
│   └── deployments/
│       └── deploy_scheduled.py   # Déploiement avec schedule
├── models/
│   ├── staging/               # 8 vues de staging
│   ├── dimensions/            # 5 tables de dimensions
│   ├── facts/                 # 4 tables de faits
│   └── marts/                 # 4 vues analytiques
├── .env                       # Configuration
└── profiles.yml              # Configuration dbt (dans ~/.dbt/)
```

### Support
- Pour les questions: Consulter les logs dans `logs/dbt.log`
- Pour les erreurs Prefect: Voir l'UI Prefect ou les logs terminal
- Pour PostgreSQL: Consulter les logs dans le répertoire `pg_log/`

---

## 🎯 Prochaines Étapes Recommandées

1. **Court terme**:
   - ✅ Choisir une option de planification (Prefect ou Task Scheduler)
   - ✅ Configurer le monitoring automatique
   - ✅ Tester le rafraîchissement incrémental

2. **Moyen terme**:
   - 📊 Connecter un outil de BI (Power BI, Tableau, Metabase)
   - 📧 Configurer des alertes email en cas d'échec
   - 🔄 Ajouter des snapshots dbt pour l'historisation

3. **Long terme**:
   - ☁️ Migrer vers Azure/AWS pour la production
   - 🔐 Implémenter la sécurité au niveau des lignes
   - 📈 Optimiser les performances (index, partitionnement)

---

**Version**: 1.0  
**Date**: 2025-01-13  
**Statut**: Production Ready ✅
