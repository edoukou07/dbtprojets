#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

# Vérifier tous les statuts des lots de Yopougon
cursor.execute('''
SELECT 
    l.statut,
    COUNT(*) as nombre,
    STRING_AGG(CAST(l.id AS VARCHAR), ', ') as ids
FROM lots l
LEFT JOIN zones_industrielles z ON l.zone_industrielle_id = z.id
WHERE z.libelle LIKE '%Yopougon%'
GROUP BY l.statut
ORDER BY l.statut
''')

results = cursor.fetchall()
print('Statuts des lots de Yopougon:')
print('=' * 80)
total = 0
for statut, nombre, ids in results:
    print(f'{statut}: {nombre} lots (IDs: {ids})')
    total += nombre

print(f'\nTotal: {total} lots')

# Détail de chaque lot
print('\n\nDétail complet des lots:')
print('=' * 80)
cursor.execute('''
SELECT 
    l.id,
    l.numero,
    l.statut,
    l.entreprise_id,
    CASE WHEN da.id IS NOT NULL AND da.statut = 'VALIDE' THEN 'OUI' ELSE 'NON' END as attribution_valide
FROM lots l
LEFT JOIN zones_industrielles z ON l.zone_industrielle_id = z.id
LEFT JOIN demandes_attribution da ON l.id = da.lot_id
WHERE z.libelle LIKE '%Yopougon%'
ORDER BY l.id
''')

results = cursor.fetchall()
for lot_id, numero, statut, entreprise_id, attribution in results:
    print(f'Lot {lot_id}: Num={numero}, Statut={statut}, Entreprise={entreprise_id}, Attribution={attribution}')
