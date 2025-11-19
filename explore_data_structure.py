import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection

print("="*80)
print("EXPLORATION DE LA STRUCTURE DES DONNÉES")
print("="*80)

cursor = connection.cursor()

# Vérifier les tables disponibles
print("\n1️⃣ TABLES DISPONIBLES:")
cursor.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema IN ('dwh_staging', 'dwh_dimensions', 'dwh_facts')
    ORDER BY table_schema, table_name
""")
tables = cursor.fetchall()
for schema, table in tables:
    print(f"  {schema}.{table}")

# Vérifier les colonnes de fait_factures
print("\n2️⃣ COLONNES dans dwh_facts.fait_factures:")
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'dwh_facts' AND table_name = 'fait_factures'
    ORDER BY ordinal_position
""")
columns = cursor.fetchall()
for col, dtype in columns:
    print(f"  - {col}: {dtype}")

# Vérifier les données de test
print("\n3️⃣ ÉCHANTILLON DE DONNÉES (fait_factures):")
cursor.execute("""
    SELECT DISTINCT entreprise_id, collecte_id, demande_attribution_id, ayant_droit_id
    FROM "dwh_facts"."fait_factures"
    LIMIT 5
""")
result = cursor.fetchall()
for row in result:
    print(f"  entreprise_id={row[0]}, collecte_id={row[1]}, demande_attr={row[2]}, ayant_droit={row[3]}")

# Vérifier s'il y a une table avec lot_id lié aux factures
print("\n4️⃣ RECHERCHE: Lien vers les lots")
cursor.execute("""
    SELECT table_name, column_name 
    FROM information_schema.columns 
    WHERE (column_name LIKE '%lot%' OR column_name LIKE '%zone%')
    AND table_schema IN ('dwh_staging', 'dwh_dimensions', 'dwh_facts')
    ORDER BY table_name, column_name
""")
lot_cols = cursor.fetchall()
for table, col in lot_cols:
    print(f"  {table}.{col}")
