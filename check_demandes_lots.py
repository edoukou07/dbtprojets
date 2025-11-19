import os, sys, django
sys.path.insert(0, 'bi_app/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection

cursor = connection.cursor()

# Vérifier la relation entre demandes et lots
cursor.execute("""
    SELECT 
        da.entreprise_id,
        COUNT(DISTINCT dal.lot_id) as nombre_lots,
        SUM(l.superficie) as superficie_totale
    FROM demandes_attribution da
    JOIN demande_attribution_lots dal ON da.id = dal.demande_attribution_id
    JOIN lots l ON dal.lot_id = l.id
    WHERE da.statut = 'VALIDE'
    GROUP BY da.entreprise_id
    ORDER BY superficie_totale DESC
    LIMIT 10
""")
result = cursor.fetchall()
print("Demandes VALIDE avec lots:")
for row in result:
    print(f"  Entreprise {row[0]}: {row[1]} lots, {row[2]} m²")


