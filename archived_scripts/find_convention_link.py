import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="sigeti_node_db",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

print("=" * 100)
print("RECHERCHE DU LIEN: CONVENTIONS ↔ DEMANDES_ATTRIBUTION")
print("=" * 100)

# Check all columns in demandes_attribution
query1 = """
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'demandes_attribution'
ORDER BY ordinal_position;
"""
cursor.execute(query1)
cols = cursor.fetchall()

print("\n1. TOUTES LES COLONNES DE DEMANDES_ATTRIBUTION:")
print("-" * 100)
for col in cols:
    print(f"  {col[0]:<40} ({col[1]})")

# Check for convention-related columns
print("\n2. COLONNES LIÉES AUX CONVENTIONS:")
print("-" * 100)
convention_cols = [col for col in cols if 'convention' in col[0].lower()]
if convention_cols:
    for col in convention_cols:
        print(f"  ✓ {col[0]:<40} ({col[1]})")
else:
    print("  ✗ Aucune colonne 'convention' trouvée")

# Sample demandes_attribution data
query2 = """
SELECT *
FROM demandes_attribution
LIMIT 3;
"""
cursor.execute(query2)
samples = cursor.fetchall()
col_names = [desc[0] for desc in cursor.description]

print("\n3. SAMPLE DATA DEMANDES_ATTRIBUTION:")
print("-" * 100)
for i, sample in enumerate(samples, 1):
    print(f"\n  Enregistrement {i}:")
    for col_name, value in zip(col_names, sample):
        if value is not None and col_name in ['id', 'entreprise_id', 'lot_id', 'zone_id', 'user_id', 'created_at']:
            print(f"    {col_name:<30} : {value}")

# Check if there's a workflow table that might link them
print("\n4. RECHERCHE DE TABLES DE WORKFLOW:")
print("-" * 100)
query3 = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE '%workflow%' OR table_name LIKE '%etape%';
"""
cursor.execute(query3)
workflow_tables = cursor.fetchall()
for table in workflow_tables:
    print(f"  ✓ {table[0]}")

# Check lots table structure
print("\n5. STRUCTURE LOTS (pour comprendre l'attribution):")
print("-" * 100)
query4 = """
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'lots'
ORDER BY ordinal_position;
"""
cursor.execute(query4)
lots_cols = cursor.fetchall()
for col in lots_cols:
    print(f"  {col[0]:<40} ({col[1]})")

# Check if lots has convention_id
print("\n6. VÉRIFICATION: lots.convention_id ?")
print("-" * 100)
lots_convention_cols = [col for col in lots_cols if 'convention' in col[0].lower()]
if lots_convention_cols:
    for col in lots_convention_cols:
        print(f"  ✓ TROUVÉ: {col[0]:<40} ({col[1]})")
else:
    print("  ✗ Aucune colonne 'convention' dans lots")

print("\n" + "=" * 100)

cursor.close()
conn.close()
