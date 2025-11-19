import os, sys, django
sys.path.insert(0, 'bi_app/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection

cursor = connection.cursor()

# Vérifier les tables disponibles
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%attribution%'
    ORDER BY table_name
""")
result = cursor.fetchall()
print(f"Tables contenant 'attribution': {result}")

# Vérifier les tables demandes
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%demande%'
    ORDER BY table_name
""")
result = cursor.fetchall()
print(f"\nTables contenant 'demande': {result}")

# Vérifier les lots
cursor.execute("""
    SELECT COUNT(*), AVG(superficie) as superficie_moy
    FROM lots
""")
result = cursor.fetchone()
print(f"\nLots:")
print(f"  Count: {result[0]}")
print(f"  Superficie moyenne: {result[1]}")

