#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.core.cache import cache

print("=== Clearing Django cache ===")
cache.clear()
print("✓ Cache cleared!")

# Verify the new data from Django ORM
try:
    from sigeti_bi.models import MartOccupationZones
    zones = MartOccupationZones.objects.filter(nom_zone__icontains='Yopougon').values(
        'nom_zone', 'nombre_total_lots', 'lots_attribues', 'lots_disponibles', 'lots_reserves', 'taux_occupation_pct'
    )
except Exception as e:
    print(f"Could not import model: {e}, using raw SQL instead")
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
    SELECT nom_zone, nombre_total_lots, lots_attribues, lots_disponibles, lots_reserves, taux_occupation_pct
    FROM "dwh_marts_occupation"."mart_occupation_zones"
    WHERE nom_zone ILIKE '%Yopougon%'
    """)
    cols = ['nom_zone', 'nombre_total_lots', 'lots_attribues', 'lots_disponibles', 'lots_reserves', 'taux_occupation_pct']
    zones = [dict(zip(cols, row)) for row in cursor.fetchall()]

print("\n=== Data from Django ORM ===")
for zone in zones:
    print(f"Zone: {zone['nom_zone']}")
    print(f"  Total: {zone['nombre_total_lots']}")
    print(f"  Attribués: {zone['lots_attribues']}")
    print(f"  Disponibles: {zone['lots_disponibles']}")
    print(f"  Réservés: {zone['lots_reserves']}")
    print(f"  Taux occupation: {zone['taux_occupation_pct']}%")
    total = zone['lots_attribues'] + zone['lots_disponibles'] + zone['lots_reserves']
    check = "✓" if total == zone['nombre_total_lots'] else "✗"
    print(f"  Total check: {total} {check}")
