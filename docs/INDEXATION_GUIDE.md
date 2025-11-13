# 📊 Guide d'Indexation PostgreSQL - SIGETI DWH

## Vue d'ensemble

L'indexation a été intégrée dans le workflow Prefect pour optimiser automatiquement les performances des requêtes sur le Data Warehouse.

## Architecture

### Ordre d'exécution dans le pipeline

```
1. Staging      → Construction des vues sources
2. Dimensions   → Construction des tables de dimensions
3. INDEXATION   → Création des index PostgreSQL ⭐ NOUVEAU
4. Facts        → Construction des tables de faits
5. Marts        → Construction des data marts
6. Tests        → Validation des données
7. Documentation → Génération de la doc dbt
```

### Pourquoi après les dimensions ?

Les index sont créés **après les dimensions mais avant les facts** pour :
- ✅ Les clés étrangères existent déjà (dimensions chargées)
- ✅ Les facts bénéficient immédiatement des index lors de l'insertion
- ✅ Les jointures dans les facts sont accélérées dès le premier run

## Index créés

### 📈 Tables de Faits

#### `fait_attributions` (7 index)
```sql
-- Clés étrangères (optimise les JOIN)
CREATE INDEX idx_fait_attr_entreprise ON fait_attributions(entreprise_key);
CREATE INDEX idx_fait_attr_lot ON fait_attributions(lot_key);
CREATE INDEX idx_fait_attr_zone ON fait_attributions(zone_key);
CREATE INDEX idx_fait_attr_domaine ON fait_attributions(domaine_key);

-- Dates (optimise les filtres temporels)
CREATE INDEX idx_fait_attr_date_demande ON fait_attributions(date_demande_key);
CREATE INDEX idx_fait_attr_created_at ON fait_attributions(created_at);

-- Index composite (optimise les agrégations)
CREATE INDEX idx_fait_attr_entreprise_date ON fait_attributions(entreprise_key, date_demande_key);
```

#### `fait_factures` (6 index)
```sql
-- Clés étrangères
CREATE INDEX idx_fait_fact_entreprise ON fait_factures(entreprise_key);
CREATE INDEX idx_fait_fact_lot ON fait_factures(lot_key);
CREATE INDEX idx_fait_fact_date_creation ON fait_factures(date_creation_key);
CREATE INDEX idx_fait_fact_date_emission ON fait_factures(date_emission_key);

-- Index partiels (optimise les requêtes ciblées)
CREATE INDEX idx_fait_fact_statut_paiement ON fait_factures(statut_paiement)
    WHERE statut_paiement IN ('impaye', 'partiellement_paye');

CREATE INDEX idx_fait_fact_montant ON fait_factures(montant_facture)
    WHERE montant_facture > 0;
```

#### `fait_paiements` (4 index)
```sql
CREATE INDEX idx_fait_paie_entreprise ON fait_paiements(entreprise_key);
CREATE INDEX idx_fait_paie_facture ON fait_paiements(facture_key);
CREATE INDEX idx_fait_paie_date ON fait_paiements(date_paiement_key);
CREATE INDEX idx_fait_paie_mode ON fait_paiements(mode_paiement);
```

#### `fait_collectes` (3 index)
```sql
CREATE INDEX idx_fait_coll_zone ON fait_collectes(zone_key);
CREATE INDEX idx_fait_coll_date_debut ON fait_collectes(date_debut_key);
CREATE INDEX idx_fait_coll_date_fin ON fait_collectes(date_fin_prevue_key);
```

### 📁 Tables de Dimensions

#### `dim_temps` (3 index)
```sql
-- Date complète (requêtes exactes)
CREATE INDEX idx_dim_temps_date ON dim_temps(date);

-- Agrégations mensuelles
CREATE INDEX idx_dim_temps_annee_mois ON dim_temps(annee, mois);

-- Reporting trimestriel
CREATE INDEX idx_dim_temps_annee_trimestre ON dim_temps(annee, trimestre);
```

#### `dim_entreprises` (3 index)
```sql
-- Recherches par nom
CREATE INDEX idx_dim_entr_nom ON dim_entreprises(nom_entreprise);

-- Lookups par email
CREATE INDEX idx_dim_entr_email ON dim_entreprises(email);

-- Full-text search (requiert l'extension pg_trgm)
CREATE INDEX idx_dim_entr_nom_trgm ON dim_entreprises 
    USING gin (nom_entreprise gin_trgm_ops);
```

#### `dim_lots` (3 index)
```sql
-- Filtres par zone
CREATE INDEX idx_dim_lots_zone ON dim_lots(zone_id);

-- Lots disponibles/occupés
CREATE INDEX idx_dim_lots_statut ON dim_lots(statut);

-- Recherches par superficie
CREATE INDEX idx_dim_lots_superficie ON dim_lots(superficie)
    WHERE superficie > 0;
```

## Impact sur les performances

### Estimations théoriques

| Type de requête | Amélioration attendue |
|-----------------|----------------------|
| Jointures (JOIN) | **50-80%** plus rapide |
| Filtres par date (WHERE date = ...) | **70-90%** plus rapide |
| Agrégations (GROUP BY) | **40-60%** plus rapide |
| Recherches full-text | **95%** plus rapide |

### Exemples de requêtes optimisées

#### Avant l'indexation ❌
```sql
-- Scan séquentiel de toute la table
EXPLAIN SELECT * FROM fait_attributions WHERE entreprise_key = 10;
-- Seq Scan on fait_attributions  (cost=0.00..35.50 rows=1 width=100)
```

#### Après l'indexation ✅
```sql
-- Utilisation de l'index
EXPLAIN SELECT * FROM fait_attributions WHERE entreprise_key = 10;
-- Index Scan using idx_fait_attr_entreprise  (cost=0.15..8.17 rows=1 width=100)
```

## Utilisation

### Automatique via Prefect

L'indexation s'exécute automatiquement dans le workflow :

```powershell
# Run complet avec indexation
.\venv\Scripts\Activate.ps1
python prefect\flows\sigeti_dwh_flow.py
```

### Manuelle via psql

Pour recréer les index manuellement :

```powershell
# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Exécuter le script SQL
$env:PGPASSWORD="votre_mot_de_passe"
psql -U postgres -d sigeti_node_db -f scripts\create_indexes.sql
```

### Vérifier les index existants

```sql
-- Lister tous les index du schéma dwh
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname IN ('dwh_facts', 'dwh_dimensions')
ORDER BY tablename, indexname;
```

## Maintenance

### Analyser l'utilisation des index

```sql
-- Statistiques d'utilisation des index
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan AS "Nombre de scans",
    idx_tup_read AS "Tuples lus",
    idx_tup_fetch AS "Tuples récupérés"
FROM pg_stat_user_indexes
WHERE schemaname IN ('dwh_facts', 'dwh_dimensions')
ORDER BY idx_scan DESC;
```

### Identifier les index inutilisés

```sql
-- Index jamais utilisés (candidats à la suppression)
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname IN ('dwh_facts', 'dwh_dimensions');
```

### Reconstruire les index (maintenance)

```sql
-- Reconstruire un index fragmenté
REINDEX INDEX idx_fait_attr_entreprise;

-- Reconstruire tous les index d'une table
REINDEX TABLE fait_attributions;

-- Reconstruire tous les index d'un schéma
REINDEX SCHEMA dwh_facts;
```

### Mettre à jour les statistiques

```sql
-- Après insertion/modification massive
ANALYZE fait_attributions;
ANALYZE fait_factures;
ANALYZE fait_paiements;
ANALYZE fait_collectes;
```

## Optimisations avancées

### Index partiels

Utilisés quand on filtre fréquemment sur les mêmes valeurs :

```sql
-- Seulement les factures impayées (réduit la taille de l'index)
CREATE INDEX idx_factures_impayees ON fait_factures(entreprise_key)
    WHERE statut_paiement = 'impaye';
```

### Index composites

Utilisés pour les requêtes avec plusieurs colonnes :

```sql
-- Requêtes du type: WHERE entreprise_key = X AND date_key = Y
CREATE INDEX idx_composite ON fait_attributions(entreprise_key, date_key);
```

### Index GIN pour full-text

Utilisés pour les recherches textuelles :

```sql
-- Recherches floues sur les noms d'entreprises
CREATE INDEX idx_entreprise_fulltext ON dim_entreprises 
    USING gin (nom_entreprise gin_trgm_ops);

-- Exemple de requête
SELECT * FROM dim_entreprises WHERE nom_entreprise ILIKE '%soci%';
```

## Troubleshooting

### Les index ne sont pas utilisés ?

1. **Vérifier les statistiques sont à jour** :
   ```sql
   ANALYZE fait_attributions;
   ```

2. **Vérifier que PostgreSQL utilise bien l'index** :
   ```sql
   EXPLAIN ANALYZE SELECT * FROM fait_attributions WHERE entreprise_key = 10;
   ```

3. **Forcer l'utilisation d'index** (si nécessaire) :
   ```sql
   SET enable_seqscan = off;
   ```

### Performance dégradée après insertion massive ?

```sql
-- Reconstruire les index
REINDEX TABLE fait_attributions;

-- Mettre à jour les statistiques
ANALYZE fait_attributions;

-- Nettoyer les tuples morts
VACUUM ANALYZE fait_attributions;
```

### Espace disque insuffisant ?

```sql
-- Taille des index
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname IN ('dwh_facts', 'dwh_dimensions')
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Prochaines étapes

### PRIORITÉ 2 (court terme)

- ✅ Indexation PostgreSQL (FAIT)
- ⏳ Monitoring des métriques d'index
- ⏳ Dashboard de performance

### PRIORITÉ 3 (long terme)

- Partitionnement des tables de faits par date
- Index BRIN pour les colonnes ordonnées
- Compression des index (avec pg_repack)

## Références

- [PostgreSQL Index Types](https://www.postgresql.org/docs/current/indexes-types.html)
- [Index Maintenance](https://www.postgresql.org/docs/current/maintenance.html)
- [Performance Tips](https://www.postgresql.org/docs/current/performance-tips.html)

---

**Date de création** : 2025-11-13  
**Dernière mise à jour** : 2025-11-13  
**Intégration** : Workflow Prefect STEP 3
