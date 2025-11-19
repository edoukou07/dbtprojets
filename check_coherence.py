#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection
c = connection.cursor()

print("=== Current MART data (from database) ===\n")
c.execute("""
SELECT nom_zone, nombre_total_lots, lots_attribues, lots_disponibles, lots_reserves, 
       (lots_attribues + lots_disponibles + lots_reserves) as check_total
FROM "dwh_marts_occupation"."mart_occupation_zones"
WHERE nom_zone LIKE '%Yopougon%' OR nom_zone LIKE '%Koumassi%' OR nom_zone LIKE '%Akoup%' OR nom_zone LIKE '%Vridi%'
ORDER BY nom_zone
""")

print("Zone | Total | Attrib | Dispo | Reserves | Check | Match")
print("-" * 70)
for zone, total, attrib, dispo, reserves, check in c.fetchall():
    match = "✓" if check == total else "✗"
    print(f"{zone:35s} | {total:5d} | {attrib:6d} | {dispo:5d} | {reserves:8d} | {check:5d} | {match}")

# Now check what the actual logic SHOULD be
print("\n=== Expected calculation (re-verify with actual lots) ===\n")

c.execute("""
SELECT 
    'Yopougon' as zone,
    COUNT(*) as total,
    COUNT(CASE WHEN l.statut::text = 'disponible' AND NOT EXISTS (
        SELECT 1 FROM demandes_attribution WHERE lot_id=l.id AND statut='VALIDE'
    ) THEN 1 END) as dispo_no_valide,
    COUNT(CASE WHEN EXISTS (
        SELECT 1 FROM demandes_attribution WHERE lot_id=l.id AND statut='VALIDE'
    ) THEN 1 END) as with_valide,
    COUNT(CASE WHEN l.statut::text != 'disponible' AND NOT EXISTS (
        SELECT 1 FROM demandes_attribution WHERE lot_id=l.id AND statut='VALIDE'
    ) THEN 1 END) as reserves
FROM lots l
WHERE l.zone_industrielle_id = (SELECT id FROM zones_industrielles WHERE libelle LIKE '%Yopougon%')
""")

zone, total, dispo, attrib, reserves = c.fetchone()
print(f"{zone}: Total={total}, Dispo(no VALIDE)={dispo}, With VALIDE={attrib}, Reserves(occupied no VALIDE)={reserves}")
print(f"Check: {dispo} + {attrib} + {reserves} = {dispo + attrib + reserves}")
