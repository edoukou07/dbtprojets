# Aide-mémoire - Commandes SIGETI DWH

## 🚀 Démarrage rapide

### Première installation
```powershell
.\scripts\install.ps1
```

### Démarrer Prefect (Terminal 1)
```powershell
.\scripts\start_prefect.ps1
```

### Exécuter le DWH (Terminal 2)

**Full Refresh** (première fois ou reconstruction complète):
```powershell
.\scripts\run_flow.ps1 -FlowType full
```

**Incrémental** (mise à jour quotidienne):
```powershell
.\scripts\run_flow.ps1 -FlowType incremental
```

**Marts uniquement** (rafraîchir dashboards):
```powershell
.\scripts\run_flow.ps1 -FlowType marts
```

## 📊 Commandes dbt

### Construire les modèles
```powershell
# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Tout construire
dbt run

# Staging uniquement
dbt run --select staging.*

# Dimensions uniquement
dbt run --select dimensions.*

# Facts uniquement
dbt run --select facts.*

# Marts uniquement
dbt run --select marts.*

# Un modèle spécifique
dbt run --select dim_entreprises
```

### Tests
```powershell
# Tous les tests
dbt test

# Tests d'un modèle
dbt test --select dim_entreprises
```

### Documentation
```powershell
# Générer
dbt docs generate

# Servir (http://localhost:8080)
dbt docs serve
```

### Debug
```powershell
# Tester la connexion
dbt debug

# Compiler sans exécuter
dbt compile

# Mode verbose
dbt run --debug
```

## 🗄️ Commandes PostgreSQL

### Connexion
```powershell
# Se connecter au DWH
psql -U edou -h localhost -d sigeti_dwh

# Se connecter à la source
psql -U edou -h 52.143.186.136 -d sigeti_node_db
```

### Vérifications
```sql
-- Lister les schémas
\dn

-- Lister les tables d'un schéma
\dt staging.*
\dt dimensions.*
\dt facts.*

-- Compter les lignes
SELECT COUNT(*) FROM dimensions.dim_entreprises;

-- Voir la structure d'une table
\d+ facts.fait_factures
```

### Requêtes utiles
```sql
-- Vérifier les dernières factures
SELECT * FROM facts.fait_factures ORDER BY date_creation DESC LIMIT 10;

-- Vérifier le taux d'occupation
SELECT * FROM marts_occupation.mart_occupation_zones;

-- Top 10 clients par CA
SELECT * FROM marts_clients.mart_portefeuille_clients ORDER BY chiffre_affaires_total DESC LIMIT 10;
```

## 🔧 Maintenance

### Nettoyer le cache dbt
```powershell
Remove-Item -Recurse -Force .\target\
Remove-Item -Recurse -Force .\dbt_packages\
dbt deps
```

### Mettre à jour les dépendances
```powershell
.\venv\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt
dbt deps
```

### Reconstruire complètement
```powershell
# Supprimer tous les schémas DWH
psql -U edou -h localhost -d sigeti_dwh -c "DROP SCHEMA IF EXISTS staging CASCADE;"
psql -U edou -h localhost -d sigeti_dwh -c "DROP SCHEMA IF EXISTS dimensions CASCADE;"
psql -U edou -h localhost -d sigeti_dwh -c "DROP SCHEMA IF EXISTS facts CASCADE;"
psql -U edou -h localhost -d sigeti_dwh -c "DROP SCHEMA IF EXISTS marts_financier CASCADE;"
psql -U edou -h localhost -d sigeti_dwh -c "DROP SCHEMA IF EXISTS marts_occupation CASCADE;"
psql -U edou -h localhost -d sigeti_dwh -c "DROP SCHEMA IF EXISTS marts_clients CASCADE;"
psql -U edou -h localhost -d sigeti_dwh -c "DROP SCHEMA IF EXISTS marts_operationnel CASCADE;"

# Relancer le full refresh
.\scripts\run_flow.ps1 -FlowType full
```

## 📈 Monitoring

### Prefect UI
- URL: http://127.0.0.1:4200
- Voir les exécutions des flows
- Consulter les logs
- Créer des schedules

### Logs dbt
```powershell
# Logs de compilation
cat .\target\dbt.log

# Logs d'exécution
cat .\target\run.log
```

## 🐛 Dépannage

### Erreur de connexion PostgreSQL
```powershell
# Vérifier que PostgreSQL tourne
Get-Process postgres

# Tester la connexion
psql -U edou -h localhost -d postgres -c "SELECT version();"

# Vérifier le fichier .env
cat .env
```

### Erreur dbt
```powershell
# Debug complet
dbt debug

# Nettoyer et reconstruire
Remove-Item -Recurse -Force .\target\
dbt deps
dbt run
```

### Erreur Prefect
```powershell
# Vérifier PREFECT_HOME
echo $env:PREFECT_HOME

# Redémarrer le serveur
# Ctrl+C dans le terminal du serveur
.\scripts\start_prefect.ps1
```

## 📁 Structure du projet

```
DWH_SIG/
├── models/
│   ├── sources.yml              # Définition des sources
│   ├── staging/                 # Couche staging (vues)
│   ├── dimensions/              # Tables de dimensions
│   ├── facts/                   # Tables de faits
│   └── marts/                   # Data marts (vues)
│       ├── financier/
│       ├── occupation/
│       ├── clients/
│       └── operationnel/
├── prefect/
│   └── flows/
│       └── sigeti_dwh_flow.py   # Orchestration
├── scripts/
│   ├── install.ps1              # Installation
│   ├── start_prefect.ps1        # Démarrer Prefect
│   └── run_flow.ps1             # Exécuter flows
├── dbt_project.yml              # Config dbt
├── profiles.yml                 # Connexions DB
├── packages.yml                 # Packages dbt
├── requirements.txt             # Dépendances Python
└── .env                         # Variables d'environnement
```

## 🎯 Workflows typiques

### Quotidien (automatisé)
```powershell
# Mise à jour incrémentale
.\scripts\run_flow.ps1 -FlowType incremental
```

### Hebdomadaire
```powershell
# Full refresh + tests
.\scripts\run_flow.ps1 -FlowType full
dbt test
```

### Ad-hoc (développement)
```powershell
# Modifier un modèle
code .\models\marts\financier\mart_performance_financiere.sql

# Tester
dbt run --select mart_performance_financiere

# Valider les données
psql -U edou -h localhost -d sigeti_dwh
SELECT * FROM marts_financier.mart_performance_financiere LIMIT 10;
```

## 📞 Raccourcis utiles

### Activer l'environnement
```powershell
.\venv\Scripts\Activate.ps1
```

### Voir les modèles dbt
```powershell
dbt ls
dbt ls --select staging.*
```

### Sauvegarde rapide
```powershell
$date = Get-Date -Format "yyyyMMdd_HHmm"
pg_dump -U edou -h localhost sigeti_dwh > "backup_dwh_$date.sql"
```

### Restaurer une sauvegarde
```powershell
psql -U edou -h localhost sigeti_dwh < backup_dwh_20251112_1430.sql
```
