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

print("=== Zones with REAL names (non-generated) ===")
cursor.execute('''
SELECT z.id, z.libelle, COUNT(l.id) as lot_count
FROM zones_industrielles z
LEFT JOIN lots l ON l.zone_industrielle_id = z.id
WHERE z.libelle IN ('BOUAKE', 'Zone Industrielle Akoupé-Zeudji PK24', 
                    'Zone Industrielle de Koumassi', 'Zone Industrielle de Vridi',
                    'Zone Industrielle de Yopougon')
GROUP BY z.id, z.libelle
ORDER BY lot_count DESC, z.libelle
''')

for zone_id, libelle, cnt in cursor.fetchall():
    print(f"{zone_id}: {libelle} -> {cnt} lots")

print("\n=== Analyze Yopougon lots with EVERY STATUS ===")
cursor.execute('''
SELECT 
    l.id,
    l.numero,
    l.statut::text as statut,
    CASE WHEN EXISTS (
        SELECT 1 FROM demandes_attribution da 
        WHERE da.lot_id = l.id AND da.statut = 'VALIDE'
    ) THEN 'VALIDE' ELSE 'NO_VALIDE' END as valide_status
FROM lots l
WHERE l.zone_industrielle_id = (
    SELECT id FROM zones_industrielles WHERE libelle = 'Zone Industrielle de Yopougon'
)
ORDER BY l.id
''')

print("LOT | NUMERO | STATUT | VALIDE")
disponible, attribues, reserves = 0, 0, 0
for lot_id, numero, statut, has_valide in cursor.fetchall():
    print(f"{lot_id:3d} | {numero:8s} | {statut:12s} | {has_valide}")
    if statut == 'disponible':
        disponible += 1
    elif has_valide == 'VALIDE':
        attribues += 1
    else:
        reserves += 1

print(f"\nManual count: disponible={disponible}, attribués={attribues}, réservés={reserves}")
print(f"Total: {disponible + attribues + reserves}")
