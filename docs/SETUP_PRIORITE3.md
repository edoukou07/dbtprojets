# Guide d'implémentation PRIORITÉ 3

## 🎯 Objectif

Déployer le partitionnement et la compression sur le DWH SIGETI pour optimiser:
- **Performances**: 3-16x plus rapide sur requêtes date-range
- **Espace disque**: -65% grâce à la compression
- **Maintenance**: Archivage instantané (DROP partition)

---

## ⚠️ Pré-requis

### Vérifications
```powershell
# 1. Vérifier que PRIORITÉ 1 et 2 sont implémentées
git log --oneline -5
# Devrait afficher:
#   b1d8f72 PRIORITE 2: Vues matérialisées
#   128086b PRIORITE 1: Indexation et tests

# 2. Vérifier les fichiers créés
ls scripts/create_partitions.sql
ls scripts/apply_compression.sql
ls prefect/flows/sigeti_dwh_setup.py
ls prefect/flows/sigeti_dwh_maintenance.py

# 3. Vérifier l'espace disque disponible (besoin x2 temporaire)
Get-PSDrive C | Select-Object Used,Free
```

### Sauvegarde (OBLIGATOIRE)
```powershell
# Sauvegarder la base complète
$env:PGPASSWORD="postgres"
pg_dump -h localhost -U postgres -d sigeti_node_db -F c -f "backup_avant_priorite3_$(Get-Date -Format 'yyyyMMdd_HHmmss').dump"
```

---

## 🚀 Déploiement

### Option 1: Exécution Automatique (RECOMMANDÉ)

Le setup flow gère tout automatiquement:

```powershell
# Exécuter le setup complet
python prefect/flows/sigeti_dwh_setup.py
```

Le flow va:
1. ✅ Vérifier les scripts SQL
2. ✅ Créer 22 partitions (2020-2030 pour 2 tables)
3. ✅ Créer 66 index sur les partitions
4. ✅ Migrer les données existantes
5. ✅ Appliquer compression TOAST + LZ4
6. ✅ Exécuter VACUUM FULL (30-60 min)
7. ✅ Vérifier le résultat

**Confirmation demandée**:
```
⚠️  ATTENTION: Ce flow va modifier la structure de la base de données!
⚠️  Assurez-vous d'avoir une sauvegarde avant de continuer.

Voulez-vous continuer? (oui/non):
```

### Option 2: Exécution Manuelle

Si vous préférez exécuter les scripts SQL manuellement:

```powershell
# 1. Créer les partitions
$env:PGPASSWORD="postgres"
psql -h localhost -U postgres -d sigeti_node_db -f scripts/create_partitions.sql

# 2. Appliquer la compression (⚠️ VACUUM FULL = 30-60 min)
psql -h localhost -U postgres -d sigeti_node_db -f scripts/apply_compression.sql
```

---

## ✅ Validation

### 1. Vérifier les partitions créées

```sql
-- Se connecter à la base
psql -h localhost -U postgres -d sigeti_node_db

-- Compter les partitions
SELECT COUNT(*) FROM pg_tables 
WHERE schemaname='dwh_facts' 
  AND tablename LIKE 'fait_attributions_20%';
-- Résultat attendu: 11 partitions

-- Lister avec taille
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('dwh_facts.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'dwh_facts' 
  AND tablename LIKE 'fait_%'
ORDER BY tablename;
```

### 2. Vérifier la compression

```sql
-- Gains de compression
SELECT 
    schemaname || '.' || tablename as table_name,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) as toast_index_size
FROM pg_tables 
WHERE schemaname IN ('dwh_facts', 'dwh_dim', 'dwh_marts')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

### 3. Tester le flow quotidien modifié

```powershell
# Exécuter le flow complet
python prefect/flows/sigeti_dwh_flow.py
```

**Output attendu** (si c'est lundi):
```
[STEP 1] Staging... ✅
[STEP 2] Dimensions... ✅
[STEP 3] Indexation... ✅
[STEP 4] Facts... ✅
[STEP 5] Marts... ✅
[STEP 6] Tests... ✅
[STEP 7] Documentation... ✅

📅 LUNDI - Maintenance hebdomadaire activée
[MAINTENANCE] 1. Creation des nouvelles partitions: 0 créées
[MAINTENANCE] 2. VACUUM ANALYZE: 9/9 tables terminées
```

### 4. Tester la maintenance mensuelle

```powershell
# Test manuel
python prefect/flows/sigeti_dwh_maintenance.py
```

---

## 📊 Mesurer les gains

### Performance - Requête date-range

**Avant PRIORITÉ 3**:
```sql
EXPLAIN ANALYZE
SELECT COUNT(*) FROM dwh_facts.fait_attributions
WHERE date_demandee_key BETWEEN 20230101 AND 20231231;
-- Durée attendue: 500-2000 ms (full table scan)
```

**Après PRIORITÉ 3**:
```sql
EXPLAIN ANALYZE
SELECT COUNT(*) FROM dwh_facts.fait_attributions
WHERE date_demandee_key BETWEEN 20230101 AND 20231231;
-- Durée attendue: 50-200 ms (partition pruning)
-- Plan: Seq Scan on fait_attributions_2023 (1 partition seulement)
```

### Espace disque

```sql
-- Taille totale DWH
SELECT 
    'Total DWH' as description,
    pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))) as size
FROM pg_tables 
WHERE schemaname IN ('dwh_facts', 'dwh_dim', 'dwh_marts');

-- Attendu: ~140 MB (vs ~400 MB avant, -65%)
```

---

## 🔧 Maintenance Continue

### Quotidienne (Automatique)

Le flow quotidien s'exécute normalement:

```powershell
# Cron: 0 2 * * * (2h du matin)
python prefect/flows/sigeti_dwh_flow.py
```

**Durée**: 56 secondes (hors lundi)

### Hebdomadaire (Automatique - Lundi)

Chaque lundi, le flow quotidien exécute en plus:
- Création automatique des partitions N+1, N+2
- VACUUM ANALYZE sur 9 tables principales

**Durée**: 65-70 secondes (lundi)

### Mensuelle (Planifier)

Planifier l'exécution le 1er du mois:

**Windows Task Scheduler**:
```powershell
# Créer une tâche planifiée
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "C:\Users\hynco\Desktop\DWH_SIG\prefect\flows\sigeti_dwh_maintenance.py"

$trigger = New-ScheduledTaskTrigger -Monthly -At 3:00AM -DaysOfMonth 1

Register-ScheduledTask -TaskName "SIGETI DWH Maintenance Mensuelle" `
    -Action $action -Trigger $trigger -Description "Maintenance lourde mensuelle"
```

**Ou utiliser Prefect Deployment** (recommandé):
```powershell
cd C:\Users\hynco\Desktop\DWH_SIG\prefect\flows
prefect deploy --name "maintenance-mensuelle" `
    --interval "0 3 1 * *"  # 1er du mois à 3h
```

---

## 🐛 Troubleshooting

### Erreur: "partition does not exist"

**Cause**: Les partitions n'ont pas été créées correctement

**Solution**:
```powershell
# Re-exécuter le setup
python prefect/flows/sigeti_dwh_setup.py
```

### Erreur: "VACUUM FULL timeout"

**Cause**: VACUUM FULL prend trop de temps

**Solution**:
```powershell
# Exécuter en fenêtre de maintenance avec timeout plus long
# Modifier apply_compression.sql: timeout=3600 (1h)
```

### Erreur: "disk full"

**Cause**: VACUUM FULL nécessite x2 l'espace temporaire

**Solution**:
```powershell
# Vérifier espace disque
Get-PSDrive C | Select-Object Free

# Libérer de l'espace ou utiliser tablespace temporaire
# ALTER TABLE ... SET TABLESPACE temp_tablespace;
```

### Warning: "index not used"

**Cause**: Index créés mais pas utilisés par le planificateur

**Solution**:
```sql
-- Forcer l'analyse des statistiques
ANALYZE dwh_facts.fait_attributions;

-- Vérifier l'utilisation des index
SELECT * FROM pg_stat_user_indexes 
WHERE schemaname = 'dwh_facts' 
  AND idx_scan = 0;
```

---

## 📝 Prochaines étapes

### Après validation PRIORITÉ 3

1. **Commit et push**:
```powershell
git add .
git commit -m "PRIORITE 3: Partitionnement et compression

- Tables partitionnées: fait_attributions, fait_factures (2020-2030)
- Compression TOAST + LZ4 appliquée
- Maintenance hebdomadaire (lundi): partitions + VACUUM
- Maintenance mensuelle: VACUUM FULL + rapport santé

Gains:
- Performance requêtes: +3-16x
- Espace disque: -65%
- Archivage: 2h → 10ms
"

git push origin main
```

2. **Documentation**:
   - ✅ `docs/PRIORITE3_RESUME.md` créé
   - ✅ `docs/SETUP_PRIORITE3.md` créé (ce fichier)

3. **Monitoring**:
   - Planifier maintenance mensuelle
   - Surveiller taille des partitions
   - Vérifier logs hebdomadaires (lundi)

4. **PRIORITÉ 4-7** (optionnel):
   - PRIORITÉ 4: Row-Level Security
   - PRIORITÉ 5: Monitoring Grafana
   - PRIORITÉ 6: CI/CD GitHub Actions
   - PRIORITÉ 7: CDC Debezium

---

## 📚 Documentation complète

- **Résumé technique**: `docs/PRIORITE3_RESUME.md`
- **Scripts SQL**: `scripts/create_partitions.sql`, `scripts/apply_compression.sql`
- **Flows Prefect**: `prefect/flows/sigeti_dwh_*.py`

---

**Bonne chance avec le déploiement ! 🚀**
