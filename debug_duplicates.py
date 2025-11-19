#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

print("=== DEBUG: Check for duplicate demands ===")
cursor.execute('''
SELECT 
    lot_id,
    COUNT(*) as cnt
FROM demandes_attribution
GROUP BY lot_id
HAVING COUNT(*) > 1
ORDER BY cnt DESC
''')

duplicates = cursor.fetchall()
print(f"Lots with multiple demandes: {len(duplicates)}")
for lot_id, cnt in duplicates[:10]:
    print(f"  Lot {lot_id}: {cnt} demandes")
    cursor.execute('''
        SELECT id, statut, created_at
        FROM demandes_attribution
        WHERE lot_id = %s
        ORDER BY created_at
    ''', [lot_id])
    for dem_id, statut, created_at in cursor.fetchall():
        print(f"    - Demande {dem_id}: {statut} ({created_at})")

print("\n=== DEBUG: Yopougon lots breakdown ===")
cursor.execute('''
SELECT 
    l.id,
    l.numero,
    l.statut::text,
    COUNT(CASE WHEN da.statut = 'VALIDE' THEN 1 END) as valide_count,
    COUNT(CASE WHEN da.statut != 'VALIDE' THEN 1 END) as other_count,
    COUNT(*) as total_demandes
FROM lots l
LEFT JOIN demandes_attribution da ON l.id = da.lot_id
WHERE l.zone_industrielle_id = (
    SELECT id FROM zones_industrielles WHERE libelle ILIKE '%Yopougon%'
)
GROUP BY l.id, l.numero, l.statut::text
ORDER BY l.id
''')

print("Lot | Statut | VALIDE | Other | Total Demandes")
for lot_id, numero, statut, valide, other, total in cursor.fetchall():
    print(f"{lot_id:3d} | {numero:8s} | {statut:12s} | {valide:6d} | {other:5d} | {total:6d}")

print("\n=== The problem: ===")
print("Lots with multiple demandes get counted multiple times in the GROUP BY")
print("We need to only count VALIDE demandes without duplication")
