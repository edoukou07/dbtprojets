import psycopg2

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="sigeti_node_db",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

print("=" * 100)
print("ANALYSE DES RELATIONS - PHASE 1")
print("=" * 100)

# 1. Check if there's a link between conventions and entreprises
print("\n1. LIEN CONVENTIONS → ENTREPRISES")
print("-" * 100)

# Check via raison_sociale (string match)
query1 = """
SELECT 
    COUNT(DISTINCT c.raison_sociale) as distinct_raison_sociale_conventions,
    COUNT(DISTINCT e.raison_sociale) as distinct_raison_sociale_entreprises,
    COUNT(DISTINCT c.raison_sociale) FILTER (
        WHERE c.raison_sociale IN (SELECT raison_sociale FROM entreprises)
    ) as matching_raison_sociale
FROM conventions c, entreprises e
LIMIT 1;
"""

cursor.execute(query1)
result = cursor.fetchone()
print(f"  Raisons sociales distinctes dans conventions: {result[0]}")
print(f"  Raisons sociales distinctes dans entreprises: {result[1]}")
print(f"  Raisons sociales qui matchent: {result[2]}")

# Check user_id in conventions
query2 = """
SELECT column_name 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'conventions'
AND column_name LIKE '%user%';
"""
cursor.execute(query2)
user_cols = cursor.fetchall()
print(f"\n  Colonnes avec 'user' dans conventions: {[col[0] for col in user_cols]}")

# 2. Check demandes_attribution table
print("\n2. TABLE DEMANDES_ATTRIBUTION")
print("-" * 100)

query3 = """
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'demandes_attribution'
AND column_name IN ('entreprise_id', 'lot_id', 'convention_id', 'montant')
ORDER BY ordinal_position;
"""
cursor.execute(query3)
cols = cursor.fetchall()
if cols:
    for col in cols:
        print(f"  ✓ {col[0]:<30} ({col[1]})")
else:
    print("  Table demandes_attribution non trouvée ou sans colonnes clés")

# 3. Check lots table
print("\n3. TABLE LOTS (pour zone_industrielle_id)")
print("-" * 100)

query4 = """
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'lots'
AND column_name IN ('id', 'zone_industrielle_id', 'entreprise_id', 'superficie')
ORDER BY ordinal_position;
"""
cursor.execute(query4)
cols = cursor.fetchall()
for col in cols:
    print(f"  ✓ {col[0]:<30} ({col[1]})")

# 4. Check decisions_commission table
print("\n4. TABLE DECISIONS_COMMISSION")
print("-" * 100)

query5 = """
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'decisions_commission'
AND column_name IN ('id', 'demande_attribution_id', 'montant_accorde', 'status', 'date_decision')
ORDER BY ordinal_position;
"""
cursor.execute(query5)
cols = cursor.fetchall()
for col in cols:
    print(f"  ✓ {col[0]:<30} ({col[1]})")

# 5. Sample data to understand the workflow
print("\n5. SAMPLE DATA - CONVENTIONS")
print("-" * 100)

query6 = """
SELECT 
    id,
    numero_convention,
    raison_sociale,
    statut,
    etape_actuelle,
    cree_par,
    date_creation
FROM conventions
ORDER BY date_creation DESC
LIMIT 3;
"""
cursor.execute(query6)
samples = cursor.fetchall()
for sample in samples:
    print(f"  ID: {sample[0]}, Num: {sample[1]}, Raison: {sample[2][:30]}, Statut: {sample[3]}, Etape: {sample[4]}")

# 6. Check if there's a foreign key constraint
print("\n6. CONTRAINTES DE CLÉ ÉTRANGÈRE")
print("-" * 100)

query7 = """
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND tc.table_name IN ('conventions', 'demandes_attribution', 'decisions_commission');
"""
cursor.execute(query7)
fks = cursor.fetchall()
if fks:
    for fk in fks:
        print(f"  {fk[0]}.{fk[1]} → {fk[2]}.{fk[3]}")
else:
    print("  Aucune contrainte de clé étrangère trouvée")

print("\n" + "=" * 100)

cursor.close()
conn.close()
