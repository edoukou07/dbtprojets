#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

# Vérifier toutes les zones
cursor.execute('''
SELECT 
    nom_zone,
    nombre_total_lots,
    lots_attribues,
    lots_disponibles,
    taux_occupation_pct
FROM "dwh_marts_occupation"."mart_occupation_zones"
ORDER BY nom_zone
''')

results = cursor.fetchall()
print('Donnees dans la mart:')
for r in results:
    print(f'{r[0]}: Total={r[1]}, Attribues={r[2]}, Disponibles={r[3]}, Taux={r[4]}%')
