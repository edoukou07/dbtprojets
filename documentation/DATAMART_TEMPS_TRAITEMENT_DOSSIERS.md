# 📊 Documentation Technique : Datamart Temps de Traitement des Dossiers

## Table des Matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Source de Données](#2-source-de-données)
3. [Architecture du Datamart](#3-architecture-du-datamart)
4. [Détail des Transformations](#4-détail-des-transformations)
5. [Indicateurs de Goulot d'Étranglement](#5-indicateurs-de-goulot-détranglement)
6. [Schéma de Sortie](#6-schéma-de-sortie)
7. [Cas d'Usage et Requêtes](#7-cas-dusage-et-requêtes)
8. [Maintenance et Rafraîchissement](#8-maintenance-et-rafraîchissement)

---

## 1. Vue d'ensemble

### 1.1 Objectif

Le datamart `mart_temps_traitement_dossiers` a pour objectif d'analyser les temps de traitement des dossiers de demande d'attribution et d'identifier les **goulots d'étranglement** dans le workflow de traitement.

### 1.2 Problématique Métier

Les dossiers de demande d'attribution passent par plusieurs étapes de validation :
- Création → Vérification CEPICI → Vérification SOGEDI → Paiement → Récépissé → Analyse recevabilité → Commissions → Validation finale

**Questions clés auxquelles répond ce datamart :**
- Quelles étapes prennent le plus de temps ?
- Où se situent les goulots d'étranglement ?
- Quels processus sont instables (forte variabilité) ?
- Quel gain de temps peut-on espérer en optimisant ?

### 1.3 Informations Techniques

| Attribut | Valeur |
|----------|--------|
| **Nom du modèle** | `mart_temps_traitement_dossiers` |
| **Schéma** | `dwh_marts_rh` |
| **Matérialisation** | Table |
| **Fréquence de rafraîchissement** | Quotidien |
| **Tags** | `rh`, `performance`, `P1` |
| **Index** | `etape_id`, `action`, `est_goulot_etranglement` |

---

## 2. Source de Données

### 2.1 Table Source Principale

Le datamart s'appuie sur la table **`historique_demandes`** qui enregistre chaque action effectuée sur un dossier de demande d'attribution.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         historique_demandes                             │
├─────────────────────────────────────────────────────────────────────────┤
│ Colonne                 │ Type         │ Description                    │
├─────────────────────────┼──────────────┼────────────────────────────────┤
│ id                      │ INTEGER      │ Identifiant unique de l'entrée │
│ demande_attribution_id  │ INTEGER      │ N° du dossier de demande       │
│ utilisateur_id          │ INTEGER      │ Agent ayant effectué l'action  │
│ action                  │ VARCHAR      │ Type d'action effectuée        │
│ etape_source            │ INTEGER      │ N° de l'étape de départ        │
│ etape_destination       │ INTEGER      │ N° de l'étape d'arrivée        │
│ statut_avant            │ VARCHAR      │ Statut avant l'action          │
│ statut_apres            │ VARCHAR      │ Statut après l'action          │
│ date_action             │ TIMESTAMPTZ  │ Horodatage précis de l'action  │
│ commentaire             │ TEXT         │ Commentaire optionnel          │
│ donnees                 │ JSONB        │ Données additionnelles         │
└─────────────────────────┴──────────────┴────────────────────────────────┘
```

### 2.2 Types d'Actions Tracées

| Action | Description | Étape |
|--------|-------------|-------|
| `CREATION_DEMANDE` | Création initiale du dossier | 1→2 |
| `VERIFICATION_CEPICI` | Vérification par le CEPICI | 2→3 |
| `VERIFICATION_SOGEDI` | Vérification par SOGEDI | 3→4 |
| `PAIEMENT` | Enregistrement du paiement | 4→4 |
| `GENERER_RECEPISSE_DEPOT` | Génération du récépissé | 4→5 |
| `UPLOAD_RECEPISSE_SIGNE` | Upload du récépissé signé | 5→6 |
| `ANALYSE_RECEVABILITE` | Analyse de recevabilité | 6→7 |
| `GENERATION_ATTESTATION_RECEVABILITE` | Génération attestation | 7→7 |
| `SIGNATURE_ATTESTATION_RECEVABILITE` | Signature attestation | 7→8 |
| `SOUMETTRE_RAPPORT_TECHNIQUE` | Soumission rapport technique | 8→9 |
| `TRAITER_DEMANDE_COMMISSION_INTERNE` | Commission interne | 9→10 |
| `TRAITER_DEMANDE_COMMISSION_INTERMINISTERIELLE` | Commission interministérielle | 10→11 |
| `REDACTION_LAMEV` | Rédaction LAMEV | 11→11 |
| `SIGNATURE_LAMEV` | Signature LAMEV | 11→12 |
| `DOCUMENTS_MODIFIES_SOUMIS` | Modification de documents | Variable |

### 2.3 Exemple de Données Sources

```sql
-- Exemple de suivi d'un dossier DAZI-2025-0001
SELECT demande_attribution_id, action, date_action, etape_source, etape_destination
FROM historique_demandes
WHERE demande_attribution_id = 1
ORDER BY date_action;
```

| demande_attribution_id | action | date_action | etape_source | etape_destination |
|------------------------|--------|-------------|--------------|-------------------|
| 1 | CREATION_DEMANDE | 2025-10-03 16:35:08 | 1 | 2 |
| 1 | VERIFICATION_CEPICI | 2025-10-03 16:35:55 | 2 | 3 |
| 1 | VERIFICATION_SOGEDI | 2025-10-03 16:36:24 | 3 | 4 |
| 1 | PAIEMENT | 2025-10-03 16:36:37 | 4 | 4 |
| 1 | GENERER_RECEPISSE_DEPOT | 2025-10-03 16:36:40 | 4 | 5 |
| ... | ... | ... | ... | ... |

---

## 3. Architecture du Datamart

### 3.1 Vue d'Ensemble de l'Architecture

Le datamart est construit en 4 étapes (CTEs) successives :

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      FLUX DE TRANSFORMATION                             │
└─────────────────────────────────────────────────────────────────────────┘

    ┌───────────────────────┐
    │  historique_demandes  │  ← Table source
    └───────────┬───────────┘
                │
                ▼
    ┌───────────────────────┐
    │   CTE 1: transitions  │  Calcul des durées entre actions
    │                       │  (fonction analytique LEAD)
    └───────────┬───────────┘
                │
                ▼
    ┌───────────────────────┐
    │ CTE 2: stats_par_etape│  Agrégation statistique par action
    │                       │  (AVG, MEDIAN, STDDEV, PERCENTILES)
    └───────────┬───────────┘
                │
                ▼
    ┌───────────────────────┐
    │   CTE 3: goulots      │  Calcul des indicateurs de goulot
    │                       │  (ratios, scores, classifications)
    └───────────┬───────────┘
                │
                ▼
    ┌───────────────────────┐
    │    CTE 4: final       │  Enrichissement et recommandations
    │                       │  (rankings, recommandations)
    └───────────┬───────────┘
                │
                ▼
    ┌───────────────────────┐
    │  mart_temps_traitement│  ← Table finale
    │      _dossiers        │
    └───────────────────────┘
```

### 3.2 Diagramme de Dépendances dbt

```
{{ source('sigeti_source', 'historique_demandes') }}
                    │
                    ▼
    ┌───────────────────────────────────┐
    │ mart_temps_traitement_dossiers    │
    │ (dwh_marts_rh)                    │
    └───────────────────────────────────┘
```

---

## 4. Détail des Transformations

### 4.1 CTE 1 : `transitions` - Calcul des Durées

#### Objectif
Calculer le temps écoulé entre chaque action d'un même dossier.

#### Logique Technique

```sql
with transitions as (
    select
        h.id as historique_id,
        h.demande_attribution_id as dossier_id,
        h.utilisateur_id as agent_id,
        h.action,
        h.etape_source,
        h.etape_destination,
        h.date_action,
        
        -- Fonction LEAD : récupère la date de l'action suivante
        lead(h.date_action) over (
            partition by h.demande_attribution_id  -- Grouper par dossier
            order by h.date_action                  -- Ordonner chronologiquement
        ) as date_action_suivante,
        
        -- Calcul de la durée en minutes
        extract(epoch from (
            lead(h.date_action) over (
                partition by h.demande_attribution_id 
                order by h.date_action
            ) - h.date_action
        )) / 60 as duree_minutes
        
    from historique_demandes h
)
```

#### Explication de la Fonction LEAD()

La fonction `LEAD()` est une fonction analytique (window function) qui permet d'accéder à la valeur d'une ligne suivante dans le même ensemble de résultats.

```
┌─────────────────────────────────────────────────────────────────────────┐
│              FONCTIONNEMENT DE LEAD()                                   │
└─────────────────────────────────────────────────────────────────────────┘

Dossier DAZI-2025-0001 :

┌────┬─────────────────────┬─────────────┬──────────────────┬─────────────┐
│ N° │ Action              │ date_action │ LEAD(date_action)│ Durée       │
├────┼─────────────────────┼─────────────┼──────────────────┼─────────────┤
│ 1  │ CREATION_DEMANDE    │ 16:35:08    │ 16:35:55 ───────►│ 47 sec      │
│ 2  │ VERIFICATION_CEPICI │ 16:35:55    │ 16:36:24 ───────►│ 29 sec      │
│ 3  │ VERIFICATION_SOGEDI │ 16:36:24    │ 16:36:37 ───────►│ 13 sec      │
│ 4  │ PAIEMENT            │ 16:36:37    │ 16:36:40 ───────►│ 3 sec       │
│ 5  │ GENERER_RECEPISSE   │ 16:36:40    │ 16:38:49 ───────►│ 2 min 9 sec │
│ ...│ ...                 │ ...         │ ...              │ ...         │
│ 15 │ SIGNATURE_LAMEV     │ 16:49:22    │ NULL ───────────►│ NULL (fin)  │
└────┴─────────────────────┴─────────────┴──────────────────┴─────────────┘

PARTITION BY demande_attribution_id : Chaque dossier est traité séparément
ORDER BY date_action : Les actions sont ordonnées chronologiquement
```

#### Pourquoi cette approche ?

Cette méthode mesure le **temps réel** passé à chaque étape :
- La durée de l'action `CREATION_DEMANDE` = temps entre la création et la première vérification
- Si ce temps est long, cela indique une attente (file d'attente, manque de ressources)

---

### 4.2 CTE 2 : `stats_par_etape` - Agrégation Statistique

#### Objectif
Calculer des statistiques descriptives pour chaque type d'action.

#### Métriques Calculées

| Métrique | Fonction SQL | Description |
|----------|--------------|-------------|
| `nb_occurrences` | `COUNT(*)` | Nombre total d'exécutions de cette action |
| `nb_dossiers_distincts` | `COUNT(DISTINCT dossier_id)` | Nombre de dossiers uniques concernés |
| `nb_agents_impliques` | `COUNT(DISTINCT agent_id)` | Nombre d'agents différents |
| `duree_moyenne_minutes` | `AVG(duree_minutes)` | Temps moyen de l'étape |
| `mediane_minutes` | `PERCENTILE_CONT(0.5)` | Valeur médiane (50ème percentile) |
| `ecart_type_minutes` | `STDDEV(duree_minutes)` | Dispersion des valeurs |
| `p75_minutes` | `PERCENTILE_CONT(0.75)` | 75ème percentile |
| `p90_minutes` | `PERCENTILE_CONT(0.90)` | 90ème percentile |
| `p95_minutes` | `PERCENTILE_CONT(0.95)` | 95ème percentile |
| `min_minutes` | `MIN(duree_minutes)` | Durée minimale observée |
| `max_minutes` | `MAX(duree_minutes)` | Durée maximale observée |
| `temps_total_minutes` | `SUM(duree_minutes)` | Temps cumulé pour cette action |

#### Pourquoi utiliser la Médiane en plus de la Moyenne ?

```
┌─────────────────────────────────────────────────────────────────────────┐
│              MOYENNE vs MÉDIANE                                         │
└─────────────────────────────────────────────────────────────────────────┘

Exemple : Durées observées pour VERIFICATION_SOGEDI
[5 min, 6 min, 7 min, 8 min, 1000 min]  ← Un cas exceptionnel

Moyenne = (5+6+7+8+1000) / 5 = 205.2 min  ← Faussée par l'outlier !
Médiane = 7 min                            ← Représente mieux la réalité

┌──────────────────────────────────────────────────────────────┐
│  0    50   100   150   200   250   ...   1000                │
│  ├────┼────┼─────┼─────┼─────┼─────────────┤                 │
│  ▲    ▲                 ▲                  ▲                 │
│  │    │                 │                  │                 │
│  5-8  Médiane=7        Moyenne=205       Outlier=1000       │
└──────────────────────────────────────────────────────────────┘

La médiane est ROBUSTE aux valeurs extrêmes.
```

#### Comprendre les Percentiles

```
┌─────────────────────────────────────────────────────────────────────────┐
│              PERCENTILES (P75, P90, P95)                                │
└─────────────────────────────────────────────────────────────────────────┘

Distribution des durées pour une action (100 occurrences) :

    ▲ Fréquence
    │
    │    ████
    │   ██████
    │  ████████
    │ ██████████
    │████████████████
    └──────────────────────────────────────────────► Durée (min)
       │         │         │         │
       0        P75       P90       P95
              (75%)     (90%)     (95%)

P75 = 15 min → 75% des cas sont traités en moins de 15 min
P90 = 45 min → 90% des cas sont traités en moins de 45 min  
P95 = 120 min → 95% des cas sont traités en moins de 2h

Les cas au-delà du P95 sont des "outliers" à investiguer.
```

---

### 4.3 CTE 3 : `goulots` - Indicateurs de Goulot d'Étranglement

#### Objectif
Identifier et quantifier les goulots d'étranglement.

#### Calcul des Statistiques Globales

```sql
stats_globales as (
    select
        avg(duree_moyenne_minutes) as moyenne_globale_minutes,
        percentile_cont(0.5) within group (order by duree_moyenne_minutes) as mediane_globale_minutes,
        sum(temps_total_minutes) as temps_total_workflow
    from stats_par_etape
)
```

Ces valeurs servent de **référence** pour comparer chaque étape.

---

## 5. Indicateurs de Goulot d'Étranglement

### 5.1 Liste des 12 Indicateurs

| N° | Indicateur | Formule | Seuil Critique |
|----|------------|---------|----------------|
| 1 | `ratio_vs_moyenne_globale` | `durée_étape / moyenne_globale` | > 2 |
| 2 | `ratio_vs_mediane_globale` | `durée_étape / médiane_globale` | > 2 |
| 3 | `pct_temps_total_workflow` | `temps_étape / temps_total × 100` | > 10% |
| 4 | `coefficient_variation_pct` | `écart_type / moyenne × 100` | > 100% |
| 5 | `indice_dispersion_p90` | `P90 / médiane` | > 3 |
| 6 | `score_goulot` | Score composite (0-100) | > 50 |
| 7 | `niveau_goulot` | Classification catégorielle | CRITIQUE |
| 8 | `est_goulot_etranglement` | Booléen | TRUE |
| 9 | `gain_potentiel_minutes` | `temps_total × 0.5` | - |
| 10 | `rang_duree_moyenne` | Classement par durée | Top 3 |
| 11 | `rang_temps_total` | Classement par temps cumulé | Top 3 |
| 12 | `rang_variabilite` | Classement par variabilité | Top 3 |

### 5.2 Détail des Indicateurs Clés

#### Indicateur 1 : Ratio vs Moyenne Globale

```sql
ratio_vs_moyenne_globale = duree_moyenne_minutes / moyenne_globale_minutes
```

**Interprétation :**
| Ratio | Signification |
|-------|---------------|
| < 1 | Étape plus rapide que la moyenne |
| 1-1.5 | Étape normale |
| 1.5-2 | Étape légèrement longue |
| 2-3 | Goulot potentiel |
| > 3 | **Goulot confirmé** |

**Exemple :**
```
CREATION_DEMANDE : durée = 1108 min, moyenne_globale = 177 min
Ratio = 1108 / 177 = 6.26

→ Cette étape prend 6x plus de temps que la moyenne !
```

#### Indicateur 3 : Part du Temps Total (% Workflow)

```sql
pct_temps_total_workflow = (temps_total_minutes / temps_total_workflow) × 100
```

**Interprétation :**
```
┌─────────────────────────────────────────────────────────────────────────┐
│              RÉPARTITION DU TEMPS DANS LE WORKFLOW                      │
└─────────────────────────────────────────────────────────────────────────┘

Temps total du workflow = 17 746 minutes (295h)

┌──────────────────────────────────────────────────────────────────────┐
│████████████████████████████████████████████│░░░░░│▒▒▒│▓▓│ │ │ │ │ │ │
└──────────────────────────────────────────────────────────────────────┘
 │                                            │     │   │
 │                                            │     │   └─ Autres (15.2%)
 │                                            │     └─ VERIF_SOGEDI (6.8%)
 │                                            └─ DOCS_MODIFIES (15.5%)
 └─ CREATION_DEMANDE (62.6%) ← GOULOT CRITIQUE !

Une seule étape consomme plus de 60% du temps total !
```

#### Indicateur 4 : Coefficient de Variation (CV)

```sql
coefficient_variation_pct = (ecart_type_minutes / duree_moyenne_minutes) × 100
```

Le CV mesure la **stabilité/prévisibilité** d'un processus.

**Interprétation :**
| CV | Signification |
|----|---------------|
| < 50% | Processus stable et prévisible |
| 50-100% | Variabilité modérée |
| 100-200% | Processus instable |
| > 200% | **Processus très instable** - Problème de standardisation |

**Exemple :**
```
Étape A : moyenne=10min, écart_type=2min  → CV = 20%  (stable)
Étape B : moyenne=10min, écart_type=25min → CV = 250% (instable)

L'étape B est imprévisible : parfois 2min, parfois 1h !
→ Investigation nécessaire sur les causes de variation
```

#### Indicateur 6 : Score Composite de Goulot

```sql
score_goulot = (
    -- 40% basé sur le ratio de temps (plafonné à 10x)
    (LEAST(ratio_vs_moyenne_globale, 10) / 10 × 40) +
    
    -- 30% basé sur la part du workflow (plafonné à 50%)
    (LEAST(pct_temps_total_workflow, 50) / 50 × 30) +
    
    -- 30% basé sur la variabilité (plafonné à 200%)
    (LEAST(coefficient_variation / 100, 2) / 2 × 30)
)
```

**Décomposition du score :**
```
┌─────────────────────────────────────────────────────────────────────────┐
│              CALCUL DU SCORE DE GOULOT                                  │
└─────────────────────────────────────────────────────────────────────────┘

Exemple : CREATION_DEMANDE
- Ratio = 6.26 → min(6.26, 10) / 10 × 40 = 25.04 points
- % Workflow = 62.6% → min(62.6, 50) / 50 × 30 = 30 points
- CV = 237% → min(237/100, 2) / 2 × 30 = 30 points

Score total = 25.04 + 30 + 30 = 85.04 / 100

┌────────────────────────────────────────────────────────────────┐
│ Score: ████████████████████████████████████████████░░░░░░░░░░░ │
│        0        20        40        60        80       100     │
│                                            ▲                   │
│                                         85.04                  │
└────────────────────────────────────────────────────────────────┘
```

#### Indicateur 7 : Classification du Niveau de Goulot

```sql
CASE
    WHEN ratio > 3 AND pct_workflow > 15% THEN 'CRITIQUE'
    WHEN ratio > 2 OR pct_workflow > 10%  THEN 'MAJEUR'
    WHEN ratio > 1.5                       THEN 'MODERE'
    ELSE 'NORMAL'
END as niveau_goulot
```

**Matrice de Classification :**
```
                    Ratio vs Moyenne
                    <1.5    1.5-2   2-3     >3
              ┌─────────────────────────────────┐
         <5%  │ NORMAL  │MODERE │MAJEUR │MAJEUR │
   %     5-10%│ NORMAL  │MODERE │MAJEUR │MAJEUR │
   W    10-15%│ MAJEUR  │MAJEUR │MAJEUR │CRITIQUE
   o    >15%  │ MAJEUR  │MAJEUR │CRITIQUE│CRITIQUE
   r         └─────────────────────────────────┘
   k
   f
   l
   o
   w
```

---

### 5.3 Recommandations Automatiques

Le datamart génère des recommandations basées sur les indicateurs :

```sql
CASE
    WHEN niveau_goulot = 'CRITIQUE' 
        THEN 'URGENT: Revoir le processus, automatiser ou ajouter des ressources'
    WHEN niveau_goulot = 'MAJEUR' AND coefficient_variation_pct > 100 
        THEN 'Standardiser le processus - forte variabilité détectée'
    WHEN niveau_goulot = 'MAJEUR' 
        THEN 'Analyser les causes racines et optimiser'
    WHEN coefficient_variation_pct > 150 
        THEN 'Investiguer les cas extrêmes (>P90)'
    WHEN niveau_goulot = 'MODERE' 
        THEN 'Surveiller et documenter les bonnes pratiques'
    ELSE 'Processus nominal'
END as recommandation
```

---

## 6. Schéma de Sortie

### 6.1 Structure Complète de la Table

```sql
CREATE TABLE dwh_marts_rh.mart_temps_traitement_dossiers (
    -- IDENTIFICATION
    etape_id                    INTEGER PRIMARY KEY,
    action                      VARCHAR(100),
    etape_source               INTEGER,
    etape_destination          INTEGER,
    
    -- VOLUME
    nb_occurrences             INTEGER,
    nb_dossiers_distincts      INTEGER,
    nb_agents_impliques        INTEGER,
    
    -- TEMPS DE TRAITEMENT
    duree_moyenne_minutes      NUMERIC(10,2),
    duree_moyenne_heures       NUMERIC(10,2),
    duree_moyenne_jours        NUMERIC(10,4),
    mediane_minutes            NUMERIC(10,2),
    ecart_type_minutes         NUMERIC(10,2),
    
    -- DISTRIBUTION
    min_minutes                NUMERIC(10,2),
    p75_minutes                NUMERIC(10,2),
    p90_minutes                NUMERIC(10,2),
    p95_minutes                NUMERIC(10,2),
    max_minutes                NUMERIC(10,2),
    temps_total_minutes        NUMERIC(10,2),
    temps_total_heures         NUMERIC(10,2),
    
    -- INDICATEURS GOULOT D'ÉTRANGLEMENT
    ratio_vs_moyenne_globale   NUMERIC(10,2),
    ratio_vs_mediane_globale   NUMERIC(10,2),
    pct_temps_total_workflow   NUMERIC(10,2),
    coefficient_variation_pct  NUMERIC(10,2),
    indice_dispersion_p90      NUMERIC(10,2),
    score_goulot               NUMERIC(10,2),
    niveau_goulot              VARCHAR(20),     -- CRITIQUE, MAJEUR, MODERE, NORMAL
    est_goulot_etranglement    BOOLEAN,
    gain_potentiel_minutes     NUMERIC(10,2),
    gain_potentiel_heures      NUMERIC(10,2),
    
    -- RANKINGS
    rang_duree_moyenne         INTEGER,
    rang_temps_total           INTEGER,
    rang_variabilite           INTEGER,
    
    -- RECOMMANDATION
    recommandation             TEXT,
    
    -- MÉTADONNÉES
    dbt_updated_at             TIMESTAMP WITH TIME ZONE
);

-- INDEX
CREATE INDEX idx_etape_id ON dwh_marts_rh.mart_temps_traitement_dossiers(etape_id);
CREATE INDEX idx_action ON dwh_marts_rh.mart_temps_traitement_dossiers(action);
CREATE INDEX idx_goulot ON dwh_marts_rh.mart_temps_traitement_dossiers(est_goulot_etranglement);
```

### 6.2 Exemple de Données de Sortie

| action | niveau_goulot | duree_moy_min | pct_workflow | score_goulot | recommandation |
|--------|---------------|---------------|--------------|--------------|----------------|
| CREATION_DEMANDE | CRITIQUE | 1108.84 | 62.56 | 92.94 | URGENT: Revoir le processus... |
| DOCUMENTS_MODIFIES_SOUMIS | CRITIQUE | 548.36 | 15.47 | 44.83 | URGENT: Revoir le processus... |
| VERIFICATION_SOGEDI | MODERE | 240.00 | 6.77 | 41.19 | Investiguer les cas extrêmes |
| SOUMETTRE_RAPPORT_TECHNIQUE | NORMAL | 168.75 | 6.66 | 39.01 | Investiguer les cas extrêmes |
| ... | ... | ... | ... | ... | ... |

---

## 7. Cas d'Usage et Requêtes

### 7.1 Identifier les Goulots Critiques

```sql
SELECT 
    action,
    niveau_goulot,
    duree_moyenne_minutes,
    pct_temps_total_workflow,
    recommandation
FROM dwh_marts_rh.mart_temps_traitement_dossiers
WHERE niveau_goulot IN ('CRITIQUE', 'MAJEUR')
ORDER BY score_goulot DESC;
```

### 7.2 Analyser la Variabilité des Processus

```sql
SELECT 
    action,
    duree_moyenne_minutes,
    mediane_minutes,
    coefficient_variation_pct,
    CASE 
        WHEN coefficient_variation_pct > 200 THEN 'INSTABLE'
        WHEN coefficient_variation_pct > 100 THEN 'VARIABLE'
        ELSE 'STABLE'
    END as stabilite
FROM dwh_marts_rh.mart_temps_traitement_dossiers
ORDER BY coefficient_variation_pct DESC;
```

### 7.3 Calculer le Gain Potentiel Total

```sql
SELECT 
    SUM(gain_potentiel_heures) as gain_total_heures,
    COUNT(*) FILTER (WHERE niveau_goulot = 'CRITIQUE') as nb_critiques,
    COUNT(*) FILTER (WHERE niveau_goulot = 'MAJEUR') as nb_majeurs
FROM dwh_marts_rh.mart_temps_traitement_dossiers
WHERE est_goulot_etranglement = true;
```

### 7.4 Distribution par Niveau

```sql
SELECT 
    niveau_goulot,
    COUNT(*) as nb_etapes,
    SUM(pct_temps_total_workflow) as pct_temps_total,
    ROUND(AVG(duree_moyenne_minutes), 2) as duree_moyenne
FROM dwh_marts_rh.mart_temps_traitement_dossiers
GROUP BY niveau_goulot
ORDER BY 
    CASE niveau_goulot 
        WHEN 'CRITIQUE' THEN 1 
        WHEN 'MAJEUR' THEN 2 
        WHEN 'MODERE' THEN 3 
        ELSE 4 
    END;
```

---

## 8. Maintenance et Rafraîchissement

### 8.1 Commande de Rafraîchissement dbt

```bash
# Rafraîchir uniquement ce mart
dbt run --select mart_temps_traitement_dossiers

# Rafraîchir avec les dépendances
dbt run --select +mart_temps_traitement_dossiers

# Rafraîchir en mode full-refresh
dbt run --select mart_temps_traitement_dossiers --full-refresh
```

### 8.2 Fréquence Recommandée

| Scénario | Fréquence |
|----------|-----------|
| Production | Quotidien (nuit) |
| Analyse ad-hoc | À la demande |
| Reporting mensuel | Hebdomadaire |

### 8.3 Surveillance

**Vérifications à effectuer :**
1. Nombre de lignes générées (`SELECT COUNT(*) FROM ...`)
2. Présence de goulots critiques (`WHERE niveau_goulot = 'CRITIQUE'`)
3. Valeurs NULL inattendues (`WHERE duree_moyenne_minutes IS NULL`)

---

## Annexes

### A. Glossaire

| Terme | Définition |
|-------|------------|
| **Goulot d'étranglement** | Étape du processus qui limite le débit global |
| **Coefficient de variation (CV)** | Mesure de dispersion relative (écart-type/moyenne) |
| **Percentile** | Valeur en dessous de laquelle se trouve un pourcentage donné |
| **LEAD()** | Fonction analytique SQL accédant à la ligne suivante |
| **CTE** | Common Table Expression - sous-requête nommée |

### B. Références

- Source : `sigeti_source.historique_demandes`
- Schéma cible : `dwh_marts_rh`
- Documentation dbt : [models/marts/rh/mart_temps_traitement_dossiers.sql](../models/marts/rh/mart_temps_traitement_dossiers.sql)

---

*Document généré le 18 décembre 2025*
*Version 1.0*
