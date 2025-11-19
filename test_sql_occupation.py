import os, sys, django
sys.path.insert(0, 'bi_app/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection

cursor = connection.cursor()

# Tester la requête SQL corrigée
cursor.execute("""
    SELECT 
        COUNT(DISTINCT da.entreprise_id) as nombre_clients,
        COUNT(DISTINCT dal.lot_id) as total_lots,
        COALESCE(SUM(l.superficie), 0) as superficie_totale
    FROM demandes_attribution da
    JOIN demande_attribution_lots dal ON da.id = dal.demande_attribution_id
    JOIN lots l ON dal.lot_id = l.id
    WHERE da.statut = 'VALIDE'
""")

result = cursor.fetchone()
print("Résultat SQL:")
print(f"  Nombre clients: {result[0]}")
print(f"  Total lots: {result[1]}")
print(f"  Superficie totale: {result[2]} m²")


