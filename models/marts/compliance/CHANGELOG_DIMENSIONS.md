# 📋 Changelog - Ajout des Dimensions Critiques et Importantes

**Date**: 26 Novembre 2025  
**Status**: ✅ IMPLÉMENTÉ

---

## 1. MART_CONVENTIONS_VALIDATION - Améliorations

### ✅ Dimensions CRITIQUES AJOUTÉES

#### 1.1 Dimension Entreprise (CRITIQUE)
```
Colonne: entreprise_id
Référence: dim_entreprises
Attributs joinés:
  - raison_sociale: Nom commercial
  - forme_juridique: Type juridique (SARL, SA, etc.)
  - domaine_activite: Secteur d'activité
  
Impact: Permet segmentation par secteur, analyse risque par domaine
```

#### 1.2 Dimension Zone Industrielle (IMPORTANTE)
```
Colonnes: zone_industrielle_id, nom_zone, localisation_zone
Référence: dim_zones_industrielles
Traçage: convention → entreprise → zone

Impact: Heatmap délai de traitement par zone
```

#### 1.3 Dimension Agent Créateur (CRITIQUE)
```
Colonnes: agent_id, nom_agent_createur, prenom_agent_createur
Référence: dim_agents
Source: fait_conventions.cree_par

Impact: Productivité par agent, traçabilité complète
```

#### 1.4 Montant Convention (CRITIQUE)
```
Colonnes: 
  - montant_convention: Montant brut
  - tranche_montant: Catégorie (Moins de 10M, 10M-50M, 50M-100M, Plus de 100M)

Impact: Corrélation montant vs taux validation, segmentation montant
```

#### 1.5 Respect SLA (CRITIQUE)
```
Colonnes:
  - date_limite_reponse: Date limite de traitement
  - respect_delai: ENUM (A_TEMPS, EN_RETARD, N/A)
  - jours_delai_imparti: Jours alloués pour traitement

Agrégations:
  - conventions_a_temps: Comptage
  - conventions_en_retard: Comptage
  - pourcentage_respect_sla: Taux %

Impact: KPI compliance, SLA tracking
```

### 📊 Nouvelles Métriques

| Métrique | Calcul | Dimension |
|----------|--------|-----------|
| `montant_total` | SUM(montant_convention) | tranche_montant |
| `montant_moyen` | AVG(montant_convention) | domaine_activite |
| `montant_max/min` | MAX/MIN(montant_convention) | - |
| `conventions_a_temps` | COUNT si respect_delai='A_TEMPS' | zone |
| `pourcentage_respect_sla` | % conventions à temps vs total | agent_id |

### 🔄 Index Ajoutés
```sql
CREATE INDEX ON mart_conventions_validation(entreprise_id);
CREATE INDEX ON mart_conventions_validation(zone_industrielle_id);
CREATE INDEX ON mart_conventions_validation(agent_id);
```

### 🔗 Nouveau Grain
**Avant**: (annee_mois, etape_actuelle, statut)  
**Après**: (annee_mois, etape_actuelle, statut, entreprise_id, domaine_activite, tranche_montant)

---

## 2. MART_DELAI_APPROBATION - Améliorations

### ✅ Dimensions CRITIQUES AJOUTÉES

#### 2.1 Dimension Entreprise (CRITIQUE)
```
Colonnes: entreprise_id, raison_sociale, domaine_activite
Référence: dim_entreprises (via fact_conventions)

Impact: Analyser délai d'approbation par secteur d'activité
```

#### 2.2 Dimension Zone Industrielle (IMPORTANTE)
```
Colonnes: zone_industrielle_id, nom_zone
Référence: dim_zones_industrielles

Impact: Performance approbation par zone géographique
```

#### 2.3 Agent Approbateur (IMPORTANTE)
```
Colonnes: agent_approbateur_id, nom_approbateur, prenom_approbateur
Référence: dim_agents
Source: fait_conventions.approuve_par (ou cree_par si null)

Impact: Productivité approbateur, délai par approbateur
```

#### 2.4 Raison Rejet (IMPORTANTE)
```
Colonne: raison_rejet
Type: ENUM / TEXT
Valeurs possibles: "Docs manquants", "Non conforme", "Secteur interdit", etc.

Impact: Root cause analysis pour rejets
Nouvelles visualisations: Sankey rejet → cause → secteur
```

#### 2.5 Délai en Attente Action (IMPORTANTE)
```
Colonnes: 
  - jours_en_attente_action: Jours depuis dernière action (si EN_COURS)
  - jours_attente_moyen: Moyenne
  - jours_attente_max: Maximum

Impact: Identifier goulets d'étranglement et stagnation
```

#### 2.6 Respect SLA (CRITIQUE)
```
Colonnes:
  - respect_sla: A_TEMPS / EN_RETARD / N/A
  - conventions_a_temps: Comptage
  - conventions_en_retard: Comptage
  - pourcentage_respect_sla: Taux %

Impact: Tracking SLA approbation
```

### 📊 Nouvelles Métriques

| Métrique | Calcul | Dimension |
|----------|--------|-----------|
| `jours_attente_moyen` | AVG(jours_en_attente_action) | agent_approbateur_id |
| `jours_attente_max` | MAX(jours_en_attente_action) | raison_rejet |
| `pourcentage_respect_sla` | % conventions à temps | zone |
| `montant_total` | SUM(montant_convention) | domaine_activite |
| `delai_median_traitement` | PERCENTILE(0.5) | - |

### 🔄 Index Ajoutés
```sql
CREATE INDEX ON mart_delai_approbation(entreprise_id);
CREATE INDEX ON mart_delai_approbation(zone_industrielle_id);
CREATE INDEX ON mart_delai_approbation(agent_approbateur_id);
```

### 🔗 Nouveau Grain
**Avant**: (annee_mois, etape_actuelle, statut)  
**Après**: (annee_mois, etape_actuelle, statut, entreprise_id, agent_approbateur_id, raison_rejet, zone)

---

## 3. MART_API_PERFORMANCE - Améliorations

### ✅ Dimensions IMPORTANTES AJOUTÉES

#### 3.1 Environment (IMPORTANTE)
```
Colonne: environment
Type: ENUM
Valeurs: PRODUCTION, STAGING, DEVELOPMENT, UNKNOWN

Logique: Extraite du request_path
  - '/prod/' → PRODUCTION
  - '/staging/' → STAGING
  - '/dev/' → DEVELOPMENT

Impact: SLA par environment (ex: prod vs staging)
```

#### 3.2 Endpoint Category (IMPORTANTE)
```
Colonne: endpoint_category
Type: ENUM
Valeurs: 
  - Conventions
  - Attributions
  - Paiements
  - Collectes
  - Agents
  - Infractions
  - Zones & Lots
  - Autre

Logique: Classification basée sur request_path pattern

Impact: Performance par domaine métier
```

### 📊 Nouvelles Métriques

| Métrique | Calcul | Dimension |
|----------|--------|-----------|
| `taux_requetes_lentes_pct` | % requêtes > seuil | endpoint_category |
| `duration_min_ms_global` | MIN(duration_avg_ms) | environment |
| `endpoints_ok` | COUNT sla_status='OK' | endpoint_category |
| `endpoints_warning` | COUNT sla_status='WARNING' | - |
| `endpoints_critical` | COUNT sla_status='CRITICAL' | - |

### 🔄 Index Ajoutés
```sql
CREATE INDEX ON mart_api_performance(environment);
CREATE INDEX ON mart_api_performance(endpoint_category);
CREATE INDEX ON mart_api_performance(user_role);
```

### 🔗 Nouveau Grain
**Avant**: (request_path, request_method, status_code, user_role)  
**Après**: (request_path, request_method, status_code, user_role, environment, endpoint_category)

---

## 4. NOUVELLES VISUALISATIONS POSSIBLES

### Pour Conventions Validation

```
1. Heatmap: Taux validation par Domaine × Zone
   Dimensions: domaine_activite, nom_zone
   Métrique: taux_validation_pct

2. Scatter: Montant vs Délai de traitement
   X: montant_convention
   Y: delai_moyen_traitement_jours
   Color: domaine_activite
   Size: nombre_conventions

3. Waterfall: Respect SLA par Zone
   Catégories: nom_zone
   Valeurs: pourcentage_respect_sla

4. Table: Top 10 Agents par Productivité
   Colonnes: nom_agent_createur, nombre_conventions, taux_validation_pct, delai_moyen
   Filtre: mois = current_month
```

### Pour Délai Approbation

```
1. Sankey: Rejet → Raison → Secteur
   Flow: statut_rejet → raison_rejet → domaine_activite
   
2. Trend: Délai attente par Agent dans le temps
   X: annee_mois
   Y: jours_attente_moyen
   Line: par agent_approbateur_id

3. Bubble: Zone × Délai × Volume
   X: nom_zone
   Y: delai_moyen_traitement_jours
   Size: nombre_conventions
   Color: pourcentage_respect_sla

4. KPI Card: % Conventions en retard (par zone)
   Métrique: conventions_en_retard / total
```

### Pour API Performance

```
1. Heatmap: Environment × Category
   Rows: environment
   Cols: endpoint_category
   Valeur: sla_status (color)

2. Trend: Performance intra-jour par Category
   X: annee_mois (détail jour)
   Y: duration_avg_ms_global
   Line: par endpoint_category

3. Gauge: SLA Status par Environment
   Métrique: % endpoints_ok
   Cibles: 95% (prod), 90% (staging)
```

---

## 5. CONSIDÉRATIONS TECHNIQUES

### Concernant les Données Source

#### ⚠️ Vérifications Requises

```
1. fait_conventions doit contenir:
   ✓ entreprise_id (pour jointure)
   ✓ montant_convention (NUMERIC - peut être NULL)
   ✓ date_limite_reponse (DATE - peut être NULL)
   ✓ approuve_par (INT - agent_id, peut être NULL)
   ✓ raison_rejet (TEXT - peut être NULL)

2. dim_entreprises doit contenir:
   ✓ entreprise_id (PK)
   ✓ zone_id (FK vers dim_zones_industrielles)
   ✓ domaine_activite_id (FK vers dim_domaines)

3. dim_agents doit contenir:
   ✓ agent_id (PK)
   ✓ nom_agent, prenom_agent (pour jointure approuve_par)
```

### Performance & Optimisation

```sql
-- Index primaires (déjà créés)
CREATE INDEX idx_conventions_entreprise ON dwh_facts.fait_conventions(entreprise_id);
CREATE INDEX idx_conventions_dates ON dwh_facts.fait_conventions(date_creation, date_modification);
CREATE INDEX idx_conventions_approuve ON dwh_facts.fait_conventions(approuve_par);

-- Index mart pour accélération requêtes
CREATE INDEX idx_mart_conventions_zone ON mart_conventions_validation(zone_industrielle_id);
CREATE INDEX idx_mart_conventions_agent ON mart_conventions_validation(agent_id);
```

### Volume de Données

```
Hypothèse:
- 50,000 conventions/mois
- 100 zones industrielles
- 500 entreprises
- 50 agents
- 10 statuts

Grain Avant: 5,000 lignes/mois
Grain Après: 50,000 × 100 × 500 × 50 = potentiellement très grand!

RECOMMANDATION:
- Ajouter filtres dans les CTEs (ex: WHERE montant_convention > 0)
- Partition par annee_mois si volume > 1M de lignes
- Tester performance avant déploiement en prod
```

### SCD Type 2 (Slowly Changing Dimensions)

```
Les jointures vers dim_* utilisent des LEFT JOINs sans historique SCD.
Si besoin audit compliance strict:
- Joindre sur dim_entreprises.is_current = TRUE
- Ou capturer valid_from/valid_to lors de l'agrégation
```

---

## 6. PLAN DE DÉPLOIEMENT

### Phase 1: Préparation (Jour 1)
- [ ] Valider colonnes dans fait_conventions
- [ ] Vérifier pas de NULL critique
- [ ] Tester jointures en sandbox

### Phase 2: Déploiement DBT (Jour 2-3)
```bash
# 1. Exécuter migrations
dbt run --select marts.compliance.*

# 2. Valider résultats
dbt test --select marts.compliance.*

# 3. Tester performance
EXPLAIN ANALYZE SELECT * FROM mart_conventions_validation;

# 4. Comparer grains
SELECT COUNT(*) FROM mart_conventions_validation;
```

### Phase 3: Validation Métier (Jour 4-5)
- [ ] Spot checks données (ex: taux validation)
- [ ] Validation productivité agents
- [ ] Validation respect SLA vs attentes

### Phase 4: Déploiement Frontend (Jour 6+)
- [ ] Intégrer nouvelles dimensions au dashboard
- [ ] Créer 3-4 nouvelles visualisations
- [ ] Ajouter filtres: domaine, zone, agent

---

## 7. ROLLBACK PLAN

En cas de problème:

```bash
# Restaurer version précédente
git checkout HEAD~1 -- models/marts/compliance/

# Redéployer anciens marts
dbt run --select marts.compliance.* --full-refresh

# Valider
dbt test --select marts.compliance.*
```

---

## 8. DOCUMENTATION POUR ÉQUIPE BI

### Pour les Développeurs Frontend

```javascript
// Nouvelles colonnes disponibles dans API
endpoints:
  /api/compliance/conventions_summary → inclut: domaine_activite, zone, agent_id
  /api/compliance/delays_summary → inclut: raison_rejet, jours_attente_moyen
  /api/compliance/api_performance → inclut: environment, endpoint_category

Nouveaux filtres:
- domaine_activite (dropdown)
- nom_zone (dropdown)
- tranche_montant (multi-select)
- respect_sla (toggle)
- environment (radio)
- endpoint_category (multi-select)
```

### Pour les Analystes Métier

```
Nouvelles KPIs disponibles:
1. Taux validation par secteur d'activité (%)
2. Délai moyen par zone industrielle (jours)
3. Productivité agents (conventions/jour)
4. % conventions en retard vs SLA
5. % requêtes API lentes par environment
6. Causes de rejet (top 5)
```

---

## RÉSUMÉ DES CHANGEMENTS

| Mart | Dimensions Avant | Dimensions Après | Nouvelles Métriques |
|------|-----------------|-----------------|-------------------|
| Conventions | 5 | 15 | 8 |
| Délai Approbation | 5 | 18 | 10 |
| API Performance | 4 | 6 | 5 |
| **TOTAL** | **14** | **39** | **23** |

**Impact**: ✅ x2.8 dimensions | ✅ x1.6 métriques | ✅ +5 visualisations possibles

---

**Préparé par**: SIGETI BI Team  
**Prêt pour**: DBT Deploy  
**Next Review**: Post-déploiement (7 décembre 2025)
