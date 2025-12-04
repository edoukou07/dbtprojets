# 📊 Analyse Complète des Dimensions - Data Marts Compliance

**Date**: 26 Novembre 2025  
**Scope**: Dashboard Compliance Compliance  
**Status**: Audit approfondi avec recommandations

---

## 1. STRUCTURE ACTUELLE DES MARTS COMPLIANCE

### 1.1 Marts Existants (3 marts)

#### 🟢 Mart 1: `mart_conventions_validation`
**Source**: `dwh_facts.fait_conventions`  
**Refresh**: Quotidien  
**Utilisateurs**: Métier conformité, Management

**Dimensions actuelles**:
- `annee` - Année d'extraction
- `mois` - Mois d'extraction
- `annee_mois` - Format YYYY-MM
- `etape_actuelle` - Étape du workflow (ENUM)
- `statut` - État convention (VALIDEE, REJETEE, EN_COURS, ARCHIVEE)

**Métriques** (8):
- `nombre_conventions` - Total
- `nombre_createurs` - Créateurs distincts
- `conventions_validees` - Comptage par statut
- `conventions_rejetees`
- `conventions_en_cours`
- `conventions_archivees`
- `taux_validation_pct` - Pourcentage
- `taux_rejet_pct`
- `delai_moyen_traitement_jours` - Calcul JJ (date_modification - date_creation)
- `delai_max_traitement_jours`

**Grain**: (annee_mois, etape_actuelle, statut)

---

#### 🟢 Mart 2: `mart_delai_approbation`
**Source**: `dwh_facts.fait_conventions`  
**Refresh**: Quotidien  
**Utilisateurs**: Process owners, Management

**Dimensions actuelles**:
- `annee` - Année
- `mois` - Mois
- `annee_mois` - Format YYYY-MM
- `etape_actuelle` - Étape du workflow
- `statut` - État (VALIDEE, REJETEE, EN_COURS)

**Métriques** (11):
- `nombre_conventions` - Total
- `nombre_conventions_uniques`
- `delai_moyen_traitement_jours` - Moyenne
- `delai_min_traitement_jours` - Minimum
- `delai_max_traitement_jours` - Maximum
- `delai_median_traitement_jours` - Percentile 50%
- `delai_p95_traitement_jours` - Percentile 95%
- `conventions_validees` - Comptage
- `conventions_rejetees`
- `conventions_en_cours`

**Grain**: (annee_mois, etape_actuelle, statut)

---

#### 🟢 Mart 3: `mart_api_performance`
**Source**: `dwh_facts.fait_api_logs`  
**Refresh**: Real-time  
**Utilisateurs**: Infra, Devops, Tech leads

**Dimensions actuelles**:
- `request_path` - Chemin API
- `request_method` - GET, POST, etc.
- `status_code` - HTTP 200, 404, 500, etc.
- `user_role` - Rôle utilisateur

**Métriques** (8):
- `total_requetes` - Volume
- `total_erreurs` - Comptage
- `total_requetes_lentes` - Requêtes > seuil
- `duration_avg_ms_global` - Moyenne temps réponse
- `duration_p99_ms_global` - P99
- `duration_max_ms_global` - Maximum
- `taux_erreur_pct` - Pourcentage
- `taux_erreur_serveur_pct`
- `sla_status` - OK/WARNING/CRITICAL

**Grain**: (request_path, request_method, status_code, user_role)

---

## 2. SOURCES DE DONNÉES DISPONIBLES

### 2.1 Tables dans la base source `sigeti_node_db`

```
Tables publiques disponibles:
├── entreprises           → Profil entreprise + statut
├── agents                → Info agents + type_agent_id, est_actif
├── audit_logs            → Actions utilisateurs (CREATE, READ, UPDATE, DELETE, etc.)
├── conventions           → Conventions + dates, statut, étapes, créateurs
├── decisions_commission  → Décisions d'attribution + status + date
├── operateurs            → Opérateurs du système
├── zones_industrielles   → Zones + localisation (PostGIS)
├── lots                  → Parcelles + zone_id
├── factures              → Factures + montant + dates
├── paiement_factures     → Paiements + statut + montant
├── collectes             → Opérations collecte
├── infractions           → Infractions + type + date_constat
├── demandes_attribution  → Demandes + statut
└── purges                → Libération terrain
```

### 2.2 Dimensions existantes dans le DWH

```
dwh_dimensions/:
├── dim_entreprises        → raison_sociale, domaine_activite_id, forme_juridique
├── dim_agents             → nom_agent, prenom_agent, type_agent_id, est_actif
├── dim_zones_industrielles → nom_zone, localisation (géo), description
├── dim_lots               → numero_lot, superficie, zone_id, statut_lot
├── dim_domaines_activites → code_secteur, description_activite
├── dim_infractions_types  → type_infraction, gravite
├── dim_temps              → annee, mois, trimestre, jour_semaine
└── dim_convention_stages  → etape_id, nom_etape, ordre_execution
```

### 2.3 Facts existantes dans le DWH

```
dwh_facts/:
├── fait_conventions      → convention_id, dates, statuts, étapes, montants
├── fait_api_logs         → request_path, user_role, status_code, timings
├── fait_attributions     → attribution_id, lot_id, entreprise_id, montants
├── fait_factures         → facture_id, montants, dates_paiement
├── fait_paiements        → paiement_id, montant, statut
├── fait_collectes        → collecte_id, montant_collecte
└── fait_infractions      → infraction_id, convention_id, date_constat
```

---

## 3. ANALYSE GAP - DIMENSIONS MANQUANTES

### 3.1 Mart Conventions Validation - Opportunités

#### 🔴 Dimensions manquantes (IMPORTANTES):

1. **`entreprise_id` / Dimension Entreprise**
   - Permet segmentation par: raison_sociale, domaine_activite, forme_juridique
   - Impact: Voir validation rate par secteur d'activité
   - Complexité: BASSE (simple join sur fait_conventions.entreprise_id)
   - Exemple métrique: "Taux validation par domaine d'activité"

2. **`agent_responsable_id` / Dimension Agent**
   - Chaîne créée_par dans fait_conventions vers dim_agents
   - Impact: Performance par agent, traçabilité
   - Complexité: BASSE (join via cree_par)
   - Exemple métrique: "Productivité agents (conventions par jour)"

3. **`zone_id` / Dimension Zones**
   - Via entreprise → zone (localisation géographique)
   - Impact: Voir délai de traitement par zone
   - Complexité: MOYENNE (join chaîné: convention → entreprise → zone)
   - Exemple métrique: "Délai moyen par zone industrielle"

4. **`montant_convention`** (métrique manquante)
   - Issue de fait_conventions.montant_convention
   - Impact: Corrélation validation vs montant
   - Complexité: TRÈS BASSE (ajout colonne)
   - Exemple métrique: "Taux rejet par tranche de montant"

#### 🟡 Dimensions optionnelles (ANALYSES AVANCÉES):

5. **`commission_decision_id`** (si conventions liées à commissions)
   - Permet traçabilité des décisions
   - Impact: Analyser impact décision commission sur délai validation
   - Complexité: MOYENNE
   - Recommandation: Ajouter si besoin audit compliance

6. **`date_limite_reponse`** (dimension temps)
   - Pour analyser % convention traitée à temps vs % retard
   - Impact: KPI SLA traitement
   - Complexité: BASSE
   - Recommandation: Haute priorité

---

### 3.2 Mart Délai Approbation - Opportunités

#### 🔴 Dimensions manquantes (CRITIQUES):

1. **`entreprise_id` + Dimension Entreprise** ⭐
   - MÊME QUE CONVENTIONS VALIDATION
   - Impact supplémentaire: Correlation délai approval vs secteur
   - Exemple métrique: "Délai moyen approbation par secteur"

2. **`agent_approbateur_id` / Dimension Agent**
   - Traçabilité agent ayant approuvé/rejeté
   - Impact: Productivité par approuveur, délai approbateur
   - Complexité: MOYENNE (nécessite tracking approbation dans fact)
   - Recommandation: AJOUTER SI DONNÉE DISPONIBLE

3. **`raison_rejet`** (dimension texte)
   - Si convention rejetée: raison codifiée
   - Impact: Analyser causes retard (ex: docs manquants)
   - Complexité: BASSE (si colonne existe)
   - Recommandation: Haute priorité si données disponibles

#### 🟡 Métriques manquantes:

4. **`jours_en_attente_action`** (calcul additionnel)
   - Délai depuis que convention attend action (pas de progression)
   - Impact: Identifier goulets stagnation
   - Complexité: MOYENNE (calcul étagé)

---

### 3.3 Mart API Performance - Opportunités

#### 🟡 Dimensions manquantes (CONTEXTE):

1. **`environment`** (dev/staging/prod)
   - Impact: Voir SLA par environment
   - Complexité: TRÈS BASSE (si capturé dans logs)
   - Recommandation: Ajouter si possible

2. **`client_id` / `service_id`**
   - Traçabilité des services appelant API
   - Impact: SLA par client/service
   - Complexité: BASSE (si capturé)

3. **`endpoint_category`** (catégorie fonctionnelle)
   - Ex: "conventions", "attributions", "payments", etc.
   - Impact: Performance par domaine métier
   - Complexité: BASSE (groupement des paths)
   - Recommandation: Classification utile

4. **`timestamp` granulaire** (heure/minute)
   - Actuellement: seulement jour + aggregation
   - Impact: Trend intra-jour, pattern pics utilisation
   - Complexité: HAUTE (volume data augmente)
   - Recommandation: Examiner si besoin

---

## 4. PLAN D'ACTION RECOMMANDÉ

### Phase 1: CRITIQUE (1-2 semaines)
**Impact: Élevé | Complexité: Basse | ROI: Très Haut**

```sql
1. Mart Conventions Validation - AJOUTER:
   - entreprise_id + join dim_entreprises → raison_sociale, domaine_activite
   - montant_convention → permet segmentation par tranche
   
2. Mart Délai Approbation - AJOUTER:
   - Même: entreprise_id + dimension entreprise
   - date_limite_reponse → calcul % respect délai
   - raison_rejet (si disponible)
   
Grains résultants:
  - (annee_mois, etape_actuelle, statut, entreprise_id)
  - (annee_mois, etape_actuelle, statut, tranche_montant)
```

**Nouvelles visualisations possibles**:
- Graphique: "Taux validation par domaine d'activité"
- Heatmap: "Délai moyen par zone industrielle"
- Waterfall: "% conventions en retard vs SLA"

---

### Phase 2: IMPORTANT (2-3 semaines)
**Impact: Moyen | Complexité: Moyenne | ROI: Haut**

```sql
1. Mart Conventions - AJOUTER:
   - agent_responsable_id + dim_agents → traçabilité créateur
   - zone_id → localisation (via entreprise)
   
2. Mart Délai Approbation - AJOUTER:
   - agent_approbateur_id → productivité approbateur
   - jours_en_attente_action → identifier stagnation

3. Mart API Performance - AMÉLIORER:
   - environment dimension
   - endpoint_category classification
```

**Nouvelles visualisations possibles**:
- Tableau: "Productivité agents par période"
- Heatmap: "Performance API par categorie + environment"
- Scatter: "Volume conventions vs Délai moyen (par zone)"

---

### Phase 3: OPTIONNEL (3-4 semaines)
**Impact: Faible-Moyen | Complexité: Haute | ROI: Moyen**

```sql
1. Time-series granulaire (heure)
   - Patterns intra-jour d'approbation
   
2. Commission decision tracking
   - Audit compliance complet
   
3. Cause analysis dimension
   - Root cause rejet + délai
```

---

## 5. MODÈLE DE DONNÉES PROPOSÉ

### Mart Conventions Validation (AMÉLIORÉ)

```sql
-- Dimensions: (annee_mois, etape_actuelle, statut, entreprise_id, tranche_montant)
-- Grain: (journalier + détail entreprise)

SELECT
    -- Dimension temps
    annee, mois, annee_mois,
    
    -- Dimensions métier
    etape_actuelle,
    statut,
    
    -- Nouvelles dimensions
    entreprise_id,
    raison_sociale,
    domaine_activite,
    forme_juridique,
    tranche_montant,
    zone_industrielle,
    
    -- Agent responsable
    agent_id,
    nom_agent_complet,
    
    -- Métriques existantes
    nombre_conventions,
    taux_validation_pct,
    
    -- Nouvelles métriques
    montant_total_conventions,
    montant_moyen_convention,
    pourcentage_respect_delai,
    
    -- Métrique productivité
    conventions_par_agent
```

### Mart Délai Approbation (AMÉLIORÉ)

```sql
-- Dimensions: (annee_mois, etape_actuelle, statut, entreprise_id, agent_approbateur_id)

SELECT
    -- Dimensions temps
    annee, mois, annee_mois,
    
    -- Dimensions métier
    etape_actuelle,
    statut,
    
    -- Nouvelles dimensions
    entreprise_id,
    raison_sociale,
    zone_industrielle,
    agent_approbateur_id,
    nom_approbateur,
    raison_rejet,
    
    -- Métriques délais
    delai_moyen_traitement_jours,
    delai_median_traitement_jours,
    delai_p95_traitement_jours,
    
    -- Nouvelles métriques
    jours_en_attente_action,  -- Stagnation
    pourcentage_respect_sla,
    conventions_en_retard
```

---

## 6. BÉNÉFICES ATTENDUS

| Dimension | Métrique résultante | Valeur métier | Impact |
|-----------|-------------------|---------------|--------|
| `entreprise_id` | Taux validation par secteur | Identifier secteurs à risque | 🟢 HAUT |
| `agent_responsable` | Productivité par agent | KPI RH + performance | 🟢 HAUT |
| `zone_industrielle` | Délai par zone | Optimization locale | 🟠 MOYEN |
| `montant_convention` | Corrélation montant/validation | Scoring risque | 🟢 HAUT |
| `date_limite_reponse` | % respect SLA | Governance compliance | 🟢 CRITIQUE |
| `raison_rejet` | Cause analysis | Process improvement | 🟠 MOYEN |
| `agent_approbateur` | Délai approbateur | Performance clearing | 🟠 MOYEN |
| `environment` (API) | SLA par environment | DevOps insights | 🟡 FAIBLE |

---

## 7. POINTS DE VIGILANCE

### ⚠️ Considérations techniques:

1. **Grain des données**: Vérifier que fait_conventions a bien:
   - `entreprise_id` (linkage)
   - `date_limite_reponse` (si applicable)
   - `montant_convention` (métrique)
   - `cree_par` (agent responsable)
   - `approuve_par` (agent approbateur - si disponible)

2. **Volume data**: 
   - Vérifier taille actuelle d'une grain comme (annee_mois × etape × statut × entreprise)
   - Risque: Explosion combinatoire si beaucoup d'entreprises

3. **Performance**: 
   - Index recommandé sur: `fait_conventions(entreprise_id, etape_actuelle, statut, annee_mois)`

4. **Historique**: 
   - SCD Type 2 sur dimensions (entreprises peuvent changer de statut)

---

## 8. CHECKLIST D'IMPLÉMENTATION

### Avant de développer:

- [ ] Valider disponibilité colonnes source (montant, date_limite, approuve_par)
- [ ] Consulter métier: priorité entre montant/zone/agent?
- [ ] Vérifier volume data (risk combinatoire)
- [ ] Planifier index supplémentaires
- [ ] Évaluer SLA refresh impact

### Développement:

- [ ] Créer modèles dbt dans `/models/marts/compliance/`
- [ ] Ajouter tests dbt (uniqueness, not_null sur clés)
- [ ] Documenter colonnes + métadonnées (cols.md)
- [ ] Valider grains et agrégations
- [ ] Tester performance (EXPLAIN ANALYZE)

### Validation:

- [ ] Comparer résultats vs requête adhoc
- [ ] Tester filtres dashboard côté frontend
- [ ] Mesurer temps refresh
- [ ] Validation métier (spot check chiffres)

---

## 9. SQL EXEMPLES D'AJOUTS RAPIDES

### Ajout montant_convention à mart_conventions_validation:

```sql
-- Modification simple de mart_conventions_validation.sql

aggregated as (
    select
        ...
        -- Nouvelles métriques montant
        SUM(c.montant_convention) as montant_total,
        ROUND(AVG(c.montant_convention), 2) as montant_moyen,
        
        -- Case pour tranche
        CASE 
            WHEN c.montant_convention < 10000000 THEN 'Moins de 10M'
            WHEN c.montant_convention < 50000000 THEN '10M-50M'
            ELSE 'Plus de 50M'
        END as tranche_montant,
        ...
    from conventions c
    group by annee, mois, annee_mois, etape_actuelle, statut, tranche_montant
)
```

### Ajout entreprise_id à mart_délai_approbation:

```sql
-- Join entreprise + domaine

from conventions c
LEFT JOIN dim_entreprises e ON c.entreprise_id = e.entreprise_id
LEFT JOIN dim_domaines_activites d ON e.domaine_activite_id = d.domaine_id
```

---

## CONCLUSION

**Potentiel d'amélioration**: **TRÈS HAUT** ⭐⭐⭐⭐⭐

Avec l'ajout de seulement 3-4 dimensions critiques:
- ✅ 5+ nouvelles visualisations dashboard
- ✅ 10+ nouveaux KPI métier  
- ✅ Traçabilité complète (convention → entreprise → agent → zone)
- ✅ Compliance & audit améliorés

**Recommandation**: Commencer par **Phase 1** (critiques) - ROI maximal pour effort minimal.

---

**Document préparé pour**: Team SIGETI BI  
**Next Review**: 3 décembre 2025
