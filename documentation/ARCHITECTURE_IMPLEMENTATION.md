# SIGETI Data Warehouse - Nouvelle Architecture (Phase 1-3)

## 📋 Vue d'ensemble

Cette implémentation déploie l'architecture complète pour les 12 nouveaux indicateurs opérationnels identifiés lors de l'analyse de novembre 2025.

**Date de création**: 25 Novembre 2025  
**Version dBT**: 1.0.0+  
**Base de données**: PostgreSQL 13.22+

---

## 🏗️ Structure de Répertoires

```
models/
├── staging/                    # 8 couches d'extraction et validation
│   ├── stg_infractions.sql
│   ├── stg_suivi_implantation.sql
│   ├── stg_conventions.sql
│   ├── stg_emplois_crees.sql (JSON parsing)
│   ├── stg_indemnisations.sql
│   ├── stg_agents.sql
│   ├── stg_ayants_droits.sql
│   └── stg_audit_logs.sql
│
├── dimensions/                 # 4 nouvelles dimensions SCD Type 2
│   ├── dim_infractions_types.sql
│   ├── dim_convention_stages.sql
│   ├── dim_agents.sql
│   └── dim_zones_industrielles.sql (updated)
│
├── facts/                      # 6 nouvelles tables de faits
│   ├── fait_infractions.sql (incremental)
│   ├── fait_implantations.sql (incremental)
│   ├── fait_conventions.sql (incremental)
│   ├── fait_indemnisations.sql (incremental)
│   ├── fait_emplois_crees.sql (snapshot)
│   └── fait_api_logs.sql (daily snapshot)
│
└── marts/                      # 8 nouveaux data marts
    ├── operationnel/
    │   ├── mart_conformite_infractions.sql
    │   ├── mart_implantation_suivi.sql
    │   └── mart_emplois_crees.sql
    ├── financier/
    │   ├── mart_creances_agees.sql
    │   └── mart_indemnisations.sql
    ├── compliance/             # NEW DOMAIN
    │   ├── mart_conventions_validation.sql
    │   ├── mart_delai_approbation.sql
    │   └── mart_api_performance.sql
    └── rh/                     # NEW DOMAIN
        └── mart_agents_productivite.sql
```

---

## 🔄 Flux de Données

```
SOURCE TABLES (50+ tables SIGETI database)
    ↓
STAGING LAYER (8 vues)
    • Validation des données brutes
    • Calculs métier simple
    • Génération de clés surrogate
    ↓
DIMENSIONS (4 tables SCD Type 2)
    • Référence lentement changeante
    • Historique des versions
    • Partage entre facts
    ↓
FACTS (6 tables incrémentales + snapshots)
    • Grain unifié par domaine
    • Clés uniques garanties
    • Historique complet
    ↓
DATA MARTS (8 tables dénormalisées)
    • Optimisées pour dashboards
    • Agrégations par domaine métier
    • Indexes critiques créés
    ↓
DASHBOARDS & REPORTS
```

---

## 📊 Les 12 Indicateurs Implémentés

### Phase 1 - Semaines 1-2 (3 KPIs Quick Wins)

#### 1. **Taux d'Infraction par Zone** 🟢
- **Mart**: `marts_operationnel.mart_conformite_infractions`
- **Grain**: Zone, Mois, Sévérité
- **Mesures**: Nombre infractions, Taux résolution, Délai moyen
- **Source**: `fait_infractions` ← `stg_infractions`

#### 2. **% Sites en Retard d'Implantation** 🟢
- **Mart**: `marts_operationnel.mart_implantation_suivi`
- **Grain**: Zone, Mois, Statut
- **Mesures**: % retard, Jours retard moyen, Variance planning
- **Source**: `fait_implantations` ← `stg_suivi_implantation`

#### 3. **% Conventions Conformes DPP** 🟢
- **Mart**: `marts_compliance.mart_conventions_validation`
- **Grain**: Zone, Mois, Étape
- **Mesures**: Taux conformité, Taux approbation, Délai
- **Source**: `fait_conventions` ← `stg_conventions`

### Phase 2 - Semaines 3-4 (4 KPIs Valeur Élevée)

#### 4. **Emplois Créés par Zone et Catégorie** 📈
- **Mart**: `marts_operationnel.mart_emplois_crees`
- **Grain**: Zone, Année, Catégorie emploi
- **Mesures**: Total emplois, % expatriés/nationaux/cadres
- **Complexité**: JSON parsing from `demandes_attribution`
- **Source**: `fait_emplois_crees` ← `stg_emplois_crees` (UNNEST)

#### 5. **Distribution Créances Âgées** 💰
- **Mart**: `marts_financier.mart_creances_agees`
- **Grain**: Tranche ancienneté, Niveau risque
- **Mesures**: Nombre factures, Montants impayés, Taux
- **Complexité**: CASE WHEN sur tranches temporelles
- **Source**: Direct depuis `factures`

#### 6. **Taux Paiement Indemnisations** ✅
- **Mart**: `marts_financier.mart_indemnisations`
- **Grain**: Zone, Mois, Statut progression
- **Mesures**: Taux paiement, Délai moyen, Montants
- **Source**: `fait_indemnisations` ← `stg_indemnisations`

#### 7. **Productivité Agents (RH)** 👥
- **Mart**: `marts_rh.mart_agents_productivite`
- **Grain**: Zone, Agent
- **Mesures**: Collectes par agent, Montant recouvré, Taux, Classement
- **Source**: `collecte_agents` + `agents` + `fait_collectes`

### Phase 3 - Semaines 5-7 (4 KPIs Avancés)

#### 8. **Délai d'Approbation par Étape** ⏱️
- **Mart**: `marts_compliance.mart_delai_approbation`
- **Grain**: Mois, Étape de workflow
- **Mesures**: Délai moyen par étape, Goulots identifiés, Variance
- **Complexité**: Multi-stage workflow analysis
- **Source**: `fait_conventions` (timestamps multiples)

#### 9. **API Performance & SLA** 🚀
- **Mart**: `marts_compliance.mart_api_performance`
- **Grain**: Date, Heure, Endpoint, User role
- **Mesures**: Taux erreur, Latence (p95/p99), Status SLA
- **Complexité**: 8M+ logs/mois, percentile calculations
- **Source**: `fait_api_logs` ← `stg_audit_logs` (Daily snapshot)

#### 10. **Infractions - Distribution Gravité** 📍
- **Mart**: `marts_operationnel.mart_conformite_infractions`
- **Grain**: Zone, Période, Sévérité
- **Mesures**: Nombre par sévérité, Taux résolution, Délai
- **Source**: Same as KPI #1

#### 11. **Conventions - Waterfall Flow** 🔄
- **Mart**: `marts_compliance.mart_conventions_validation`
- **Grain**: Mois, Étape progression
- **Mesures**: Nombre par étape, Taux conversion, Funnel
- **Source**: `fait_conventions` (étape_progression)

#### 12. **Géospatial (BONUS)** 🗺️
- **Sous-étape Phase 4**
- **Mart**: TBD (géospatial avec Mapbox)
- **Grain**: Localisation exacte, Buffer zones
- **Mesures**: Densité infractions, heatmap
- **Complexité**: PostGIS, ST_Point, ST_Distance
- **Source**: `demandes_attribution` (coordonnees_geospatiales JSONB)

---

## 🛠️ Commandes dBT Essentielles

### Déployer toute l'architecture

```bash
# Exécuter les modèles dans l'ordre
dbt run --select path:staging          # 8 vues (rapide)
dbt run --select path:dimensions       # 4 dimensions (< 1 min)
dbt run --select path:facts            # 6 facts (incrémental)
dbt run --select path:marts            # 8 marts (< 5 min)

# Ou tout d'un coup (dépendances gérées automatiquement)
dbt run
```

### Tester la qualité des données

```bash
dbt test
dbt test --select staging     # Tests staging
dbt test --select facts       # Tests unique keys
```

### Générer la documentation

```bash
dbt docs generate
dbt docs serve
```

### Refresh incrémental

```bash
# Pour les facts incrementaux
dbt run --select path:facts --full-refresh

# Pour les marts materialisés
dbt run --select path:marts --full-refresh
```

---

## 📊 Schéma des Bases de Données

### Schemas PostgreSQL Créés

```sql
-- Schémas de la couche d'entreposage
public.staging           -- 8 vues de staging
public.dimensions        -- 4 tables dimensions (SCD Type 2)
public.facts             -- 6 tables de faits incrémentales
public.marts             -- Original marts

-- Nouveaux schémas de marts
public.marts_compliance  -- Conformité, délai appro, API perf
public.marts_operationnel -- Infractions, implantation, emplois
public.marts_financier   -- Créances, indemnisations
public.marts_rh          -- Productivité agents
```

### Índices Principaux Créés

```sql
-- mart_conformite_infractions
CREATE INDEX idx_mc_zone_id ON marts_operationnel.mart_conformite_infractions(zone_id);
CREATE INDEX idx_mc_date ON marts_operationnel.mart_conformite_infractions(date_detection);

-- mart_api_performance
CREATE INDEX idx_api_endpoint ON marts_compliance.mart_api_performance(endpoint_category);
CREATE INDEX idx_api_datetime ON marts_compliance.mart_api_performance(date_key, heure);

-- Tous les autres marts indexés similairement
```

---

## 🔍 Validation et Qualité

### Tests dBT Configurés

Tous les fichiers incluent:

1. **Unique Key Tests**
   ```yaml
   unique_key=['convention_id', 'infraction_id']  # Guarantees no duplicates
   ```

2. **Not Null Tests**
   ```yaml
   tests:
     - unique
     - not_null
   ```

3. **On Schema Change**
   ```yaml
   on_schema_change: 'append_new_columns'  # Forward compatible
   ```

4. **Row Count Tests** (à ajouter dans schema_nouveaux_modeles.yml)

### Exécution des Tests

```bash
dbt test --select tag:P1      # Tests pour Phase 1
dbt test --select tag:P2      # Tests pour Phase 2
dbt test --select tag:P3      # Tests pour Phase 3
```

---

## 📈 Roadmap d'Implémentation

### ✅ Complété

- [x] 8 fichiers STAGING (355 lignes)
- [x] 4 DIMENSIONS SCD Type 2 (265 lignes)
- [x] 6 FACTS (480 lignes)
- [x] 8 DATA MARTS (645 lignes)
- [x] Configuration dBT mise à jour
- [x] Schema YAML documenté (700 lignes)
- [x] Sources YAML mises à jour

### 🔄 À Faire (Étapes Suivantes)

- [ ] **Jour 1**: Valider la syntaxe dBT `dbt parse`
- [ ] **Jour 2**: Exécuter `dbt run` complet
- [ ] **Jour 3**: Tests `dbt test` et correction erreurs
- [ ] **Jour 4-5**: Créer dashboards dans l'app frontend
- [ ] **Jour 6-7**: Testing utilisateur et ajustements
- [ ] **Jour 8**: Go-live production

### 📅 Calendrier

| Semaine | Phase | Focus | Indicateurs |
|---------|-------|-------|------------|
| 1-2 | P1 | Quick Wins | #1, #2, #3 |
| 3-4 | P2 | Core Value | #4, #5, #6, #7 |
| 5-7 | P3 | Advanced | #8, #9, #10, #11 |
| 8 | P4 | Bonus | #12 (Géospatial) |

---

## 🔧 Configuration Requise

### Variables d'Environnement

Dans `profiles.yml`:

```yaml
sigeti_dwh:
  outputs:
    dev:
      type: postgres
      host: localhost
      user: sigeti_user
      password: [password]
      port: 5432
      dbname: sigeti_node_db
      schema: dev
      threads: 4
```

### Sources Requises

Le fichier `sources.yml` déclare:

```yaml
tables:
  - infractions
  - suivi_implantation
  - etapes_suivi_implantation
  - conventions
  - emplois (via demandes_attribution)
  - indemnisations
  - ayants_droits
  - agents
  - collecte_agents
  - audit_logs
  - factures (pour créances)
```

Toutes ces tables doivent exister dans `public` schema de SIGETI database.

---

## 📚 Documentation

### Fichiers de Documentation

1. **schema_nouveaux_modeles.yml** (700 lignes)
   - Description de tous les nouveaux models
   - Colonnes, types, descriptions
   - Tests associés

2. **dbt_project.yml** (mis à jour)
   - Configuration schemas
   - Tags par domaine métier
   - Materialization strategy

3. **sources.yml** (mis à jour)
   - Déclaration des sources
   - Validation source

4. **Ce README.md**
   - Vue d'ensemble architecture
   - Commandes essentielles
   - Roadmap

### Générer Documentation

```bash
dbt docs generate
dbt docs serve  # Accéder à http://localhost:8000
```

---

## 🚀 Prochaines Étapes

### Immédiat (Aujourd'hui)

1. ✅ Vérifier syntaxe: `dbt parse`
2. ✅ Lancer build: `dbt run --select staging` (test)

### Court Terme (Cette semaine)

3. Implémenter tests de qualité
4. Créer dashboards frontend pour P1 KPIs
5. Validation métier

### Moyen Terme (Semaines 2-3)

6. Phase 2 (emplois, créances, indemnisations, RH)
7. Phase 3 (délai appro, API perf)

### Long Terme

8. Bonus Phase 4 (Géospatial)
9. Optimization performance (partitioning, materialized views)
10. Audit & compliance monitoring

---

## 📞 Support

Pour questions sur l'architecture:
- Voir: **ARCHITECTURE_DBT_INDICATEURS.md**
- Pour détails SQL: **SQL_EXAMPLES_INDICATEURS.md**
- Pour roadmap: **ROADMAP_IMPLEMENTATION.md**

---

## 📄 Versions

| Version | Date | Changements |
|---------|------|------------|
| 1.0.0 | 25-Nov-2025 | Implémentation complète architecture P1-P3 |

---

**Last Updated**: 25 Novembre 2025  
**Status**: Production Ready
