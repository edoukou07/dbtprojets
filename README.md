#  SIGETI DATA WAREHOUSE

Entrepôt de données pour le Système Intégré de Gestion des Terres Industrielles.

![dbt](https://img.shields.io/badge/dbt-1.7-FF694B?logo=dbt)
![Prefect](https://img.shields.io/badge/Prefect-2.14-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791?logo=postgresql)

##  Vue d'ensemble

### Architecture Data Marts

-  **Mart Financier** - Performance financière et recouvrement
-  **Mart Occupation** - Taux d'occupation et disponibilité
-  **Mart Clients** - Portefeuille et segmentation
-  **Mart Opérationnel** - KPIs et efficacité

### Stack Technologique

- **dbt** 1.7+ - Transformations SQL
- **Prefect** 2.14+ - Orchestration ETL
- **PostgreSQL** 13+ - Source + DWH
- **Python** 3.9+ - Runtime

##  Architecture

Source DB  Staging (8 vues)  Dimensions (5 tables SCD Type 2)  Facts (4 tables)  Data Marts (4 vues)  DWH

**Schémas** : staging, dimensions, facts, marts_*

##  Installation

### Prérequis

- PostgreSQL 13+, Python 3.9+, Git
- Accès base source (52.143.186.136)

### Étapes

**1. Cloner**
cd C:\Users\hynco\Desktop
git clone https://github.com/edoukou07/dbtprojets.git DWH_SIG
cd DWH_SIG

**2. Installer**
.\scripts\install.ps1

**3. Configurer**
notepad .env
# Renseigner SOURCE_DB_*, DWH_DB_*, DBT_PASSWORD

##  Utilisation

**Démarrer Prefect**
.\scripts\start_prefect.ps1
# Interface : http://127.0.0.1:4200

**Pipeline complet**
.\scripts\run_flow.ps1 -FlowType full
# Crée la base + construit tout le DWH

**Refresh incrémental**
.\scripts\run_flow.ps1 -FlowType incremental

**Rebuild marts**
.\scripts\run_flow.ps1 -FlowType marts

##  Data Marts

1. **Financier** - Factures, paiements, recouvrement
2. **Occupation** - Taux occupation, lots disponibles
3. **Clients** - Segmentation, risques
4. **Opérationnel** - KPIs, performances

##  Commandes Utiles

**dbt**
.\venv\Scripts\Activate.ps1
dbt debug
dbt run
dbt test
dbt docs generate && dbt docs serve

**PostgreSQL**
psql -U user -h localhost -d sigeti_dwh
\dt dimensions.*

##  Support

- dbt : https://docs.getdbt.com/
- Prefect : https://docs.prefect.io/
- Logs : .\target\dbt.log

**Version** : 1.0.0 | Équipe Data SIGETI | Nov 2025
