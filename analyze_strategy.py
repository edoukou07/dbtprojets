import psycopg2
import json

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="sigeti_node_db",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

print("=" * 100)
print("STRATÉGIE ALTERNATIVE - ENRICHISSEMENT DES MARTS")
print("=" * 100)

# Comprendre la logique métier actuelle
print("\n1. ANALYSE: Que contient réellement fait_conventions?")
print("-" * 100)

# Check fait_conventions in DWH
query1 = """
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_schema = 'dwh_facts' 
AND table_name = 'fait_conventions'
ORDER BY ordinal_position;
"""
cursor.execute(query1)
cols = cursor.fetchall()

if cols:
    print("  ✓ Table dwh_facts.fait_conventions existe:")
    for col in cols:
        print(f"    {col[0]:<40} ({col[1]})")
else:
    print("  ✗ Table dwh_facts.fait_conventions n'existe pas encore")
    
# Alternative: check staging
query2 = """
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('dwh', 'staging', 'dwh_facts', 'dwh_dimensions')
AND table_name LIKE '%convention%';
"""
cursor.execute(query2)
tables = cursor.fetchall()

print("\n2. TABLES CONVENTION DANS LE DWH:")
print("-" * 100)
for table in tables:
    print(f"  {table[0]}.{table[1]}")

# Check entreprises table
print("\n3. DONNÉES DISPONIBLES DANS CONVENTIONS (source):")
print("-" * 100)
query3 = """
SELECT 
    id,
    numero_convention,
    raison_sociale,
    forme_juridique,
    domaine_activite,
    cree_par,
    statut,
    etape_actuelle
FROM conventions
WHERE id IS NOT NULL
ORDER BY date_creation DESC
LIMIT 5;
"""
cursor.execute(query3)
samples = cursor.fetchall()
col_names = [desc[0] for desc in cursor.description]

for i, sample in enumerate(samples, 1):
    print(f"\n  Convention {i}:")
    for col_name, value in zip(col_names, sample):
        print(f"    {col_name:<25} : {value}")

# Check entreprises matching
print("\n4. MATCHING ENTREPRISES via raison_sociale:")
print("-" * 100)
query4 = """
SELECT 
    c.id as convention_id,
    c.raison_sociale as conv_raison_sociale,
    e.id as entreprise_id,
    e.raison_sociale as entr_raison_sociale,
    e.domaine_activite_id,
    e.forme_juridique
FROM conventions c
LEFT JOIN entreprises e ON LOWER(TRIM(c.raison_sociale)) = LOWER(TRIM(e.raison_sociale))
WHERE c.id IS NOT NULL
LIMIT 10;
"""
cursor.execute(query4)
matches = cursor.fetchall()

if matches:
    matched_count = sum(1 for m in matches if m[2] is not None)
    print(f"  Sur {len(matches)} conventions, {matched_count} ont un match avec entreprises")
    print("\n  Exemples:")
    for match in matches[:3]:
        status = "✓ MATCH" if match[2] else "✗ NO MATCH"
        print(f"    Conv#{match[0]}: {match[1][:30]:<30} → Entr#{match[2] if match[2] else 'N/A'} {status}")

# Strategy recommendation
print("\n" + "=" * 100)
print("RECOMMANDATION STRATÉGIQUE:")
print("=" * 100)
print("""
Basé sur l'analyse, voici les options:

OPTION A - Enrichissement direct (RAPIDE):
  1. Ajouter entreprise_id via JOIN fuzzy sur raison_sociale
  2. Ajouter domaine_activite depuis la colonne conventions.domaine_activite (texte)
  3. Utiliser les données déjà dans conventions (raison_sociale, forme_juridique, etc.)
  
  Avantages: Implémentation immédiate
  Inconvénients: Pas de lien vers zones_industrielles, pas de montants

OPTION B - Enrichissement via cree_par → users → entreprises (SI LIEN EXISTE):
  1. conventions.cree_par → users.id
  2. users → entreprises (si users.entreprise_id existe)
  3. entreprises → domaine_activite
  
  Avantages: Lien robuste
  Inconvénients: Dépend de la structure users

OPTION C - Ajout de colonnes manquantes à la table source (LONG TERME):
  1. ALTER TABLE conventions ADD COLUMN entreprise_id INT
  2. ALTER TABLE conventions ADD COLUMN montant_convention NUMERIC
  3. ALTER TABLE conventions ADD COLUMN date_limite_reponse TIMESTAMP
  4. Migration des données existantes
  
  Avantages: Solution complète et pérenne
  Inconvénients: Modification du schéma source, migration nécessaire

RECOMMANDATION: Commencer par OPTION A pour un quick win, puis OPTION C pour pérennité
""")

print("=" * 100)

cursor.close()
conn.close()
