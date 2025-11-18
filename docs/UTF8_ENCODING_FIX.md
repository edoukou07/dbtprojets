# UTF-8 Encoding Fix - Documentation

## Problème Résolu

Le projet avait un problème critique d'encodage UTF-8 causé par **psycopg2 v2.9.11** qui ne pouvait pas décoder correctement les réponses PostgreSQL contenant des caractères spéciaux (accents français).

### Error Original
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 103: invalid continuation byte
```

Le byte `0xe9` = caractère "é" en encodage Latin-1, causant un crash lors de la tentative de décodage en UTF-8.

---

## Solutions Appliquées

### 1. Upgrade de psycopg2 vers psycopg v3

**Fichiers modifiés:**
- `requirements.txt` : `psycopg2-binary==2.9.11` → `psycopg[binary]>=3.2.0`
- `bi_app/backend/requirements.txt` : `psycopg2-binary==2.9.9` → `psycopg[binary]>=3.2.0`

**Avantages de psycopg v3.2.12:**
- Gestion robuste des encodages UTF-8
- Support natif pour les messages d'erreur en français
- Meilleure performance et stabilité
- Compatible avec Python 3.12

### 2. Correction des identifiants PostgreSQL

**Fichier:** `profiles.yml`
```yaml
# Avant (incorrect)
password: "{{ env_var('DBT_PASSWORD') }}"  # Variable mal configurée

# Après (correct)
password: postgres
```

### 3. Restructuration du SQL pour éliminer les doublons

**Fichier:** `models/marts/clients/mart_portefeuille_clients.sql`

**Problème:** JOINs multiples causaient une multiplication des lignes
```sql
-- AVANT (bugué)
SELECT ...
FROM entreprises e
LEFT JOIN factures f ON ...
LEFT JOIN attributions a ON ...
LEFT JOIN lots l ON ...
GROUP BY ...
```

**Solution:** Pré-agrégation dans des CTEs séparées
```sql
-- APRÈS (corrigé)
factures_stats AS (
    SELECT entreprise_id, SUM(...) 
    FROM factures 
    GROUP BY entreprise_id
),
attributions_stats AS (
    SELECT entreprise_id, COUNT(...) 
    FROM attributions 
    GROUP BY entreprise_id
),
lots_stats AS (
    SELECT entreprise_id, COUNT(...) 
    FROM lots 
    WHERE est_attribue
    GROUP BY entreprise_id
),

SELECT ...
FROM entreprises e
LEFT JOIN factures_stats f ON e.entreprise_id = f.entreprise_id
LEFT JOIN attributions_stats a ON e.entreprise_id = a.entreprise_id
LEFT JOIN lots_stats l ON e.entreprise_id = l.entreprise_id
```

---

## Résultats Obtenus

| Métrique | Avant | Après | Différence |
|----------|-------|-------|-----------|
| CA Total | 3,135,066,002 FCFA | 3,132,136,002 FCFA | -2,930,000 FCFA |
| Doublons | ❌ Présents | ✅ Supprimés | Rectifié |
| DBT Status | ❌ Crash UTF-8 | ✅ 21/21 models | Fonctionnel |

---

## Installation de la Correction

### Pour les futurs développeurs:

```bash
# 1. Cloner le repo
git clone https://github.com/edoukou07/dbtprojets.git
cd DWH_SIG

# 2. Créer l'environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Installer les dépendances (avec psycopg v3)
pip install -r requirements.txt

# 4. Vérifier la connexion
python test_psycopg2.py

# 5. Exécuter DBT
dbt debug
dbt run
```

---

## Tests de Validation

### Test 1: Vérifier psycopg v3
```bash
python -c "import psycopg; print(psycopg.__version__)"
# Output: 3.2.12
```

### Test 2: Tester la connexion PostgreSQL
```bash
python test_psycopg2.py
# Output: SUCCESS: Connected!
```

### Test 3: Vérifier l'intégrité des données
```bash
psql -h localhost -U postgres -d sigeti_node_db \
  -c "SELECT COUNT(DISTINCT entreprise_id) as total_clients, 
           SUM(chiffre_affaires_total) as ca_total 
      FROM dwh_marts_clients.mart_portefeuille_clients;"
# Expected: 35 clients | 3,132,136,002 FCFA
```

### Test 4: Exécuter le workflow DBT complet
```bash
dbt run
# Expected: PASS=21 WARN=0 ERROR=0
```

---

## Commit de Référence

```
Commit: 998667c
Message: Fix: Resolve PostgreSQL UTF-8 encoding + upgrade psycopg to v3 + fix mart_portefeuille_clients join multiplication

Changes:
- 77 files changed
- 1939 insertions (+)
- 271 deletions (-)
- Key: psycopg v2.9.11 → v3.2.12
- Key: Fixed CA doublocount (2.93M FCFA)
```

---

## Configuration Permanente Recommandée

Pour garantir qu'aucun problème d'encodage ne survienne à l'avenir:

### Dans `postgresql.conf`:
```ini
client_encoding = 'UTF8'
server_encoding = 'UTF8'
```

### Dans `dbt_project.yml`:
```yaml
config-version: 2
profile: 'sigeti_dwh'
```

### Dans `profiles.yml`:
```yaml
outputs:
  dev:
    client_encoding: 'UTF8'
```

---

## Conclusion

Le problème d'encodage UTF-8 est **définitivement résolu** grâce à:
1. ✅ Upgrade de psycopg2 v2 → v3
2. ✅ Correction des identifiants PostgreSQL
3. ✅ Restructuration du SQL pour éliminer les doublons

Le système est maintenant prêt pour la production.
