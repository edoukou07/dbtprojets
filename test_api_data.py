#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.core.cache import cache
from django.db import connection

print("=== CLEAR CACHE ===")
cache.clear()
print("✓ Cache cleared\n")

print("=== TEST API ENDPOINT: /api/occupation/by_zone/ ===")
cursor = connection.cursor()

cursor.execute("""
SELECT nom_zone, nombre_total_lots, lots_disponibles, lots_attribues, lots_reserves,
       superficie_totale, superficie_disponible, superficie_attribuee, taux_occupation_pct, valeur_totale_lots
FROM "dwh_marts_occupation"."mart_occupation_zones"
ORDER BY taux_occupation_pct DESC
""")

print("Zones returned:\n")
for zone_name, total, dispo, attrib, reserves, sup_tot, sup_dispo, sup_attrib, taux, valeur in cursor.fetchall():
    if 'Yopougon' in zone_name or 'Koumassi' in zone_name or 'Akoup' in zone_name:
        print(f"{zone_name}")
        print(f"  Total: {total}")
        print(f"  Attribués: {attrib}")
        print(f"  Disponibles: {dispo}")
        print(f"  Réservés: {reserves}")
        total_check = attrib + dispo + reserves
        match = "✓" if total_check == total else "✗"
        print(f"  Check: {total_check}/{total} {match}\n")
