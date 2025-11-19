#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartOccupationZones
from django.core.cache import cache

# Vider le cache
cache.clear()
print("Cache cleared")

# Forcer une actualisation en rechargeant depuis la base
zones = MartOccupationZones.objects.all().values(
    'nom_zone', 'nombre_total_lots', 'lots_attribues', 'lots_disponibles', 'taux_occupation_pct'
).order_by('nom_zone')

print('\nDonnees du modele Django:')
for z in zones:
    print(f"{z['nom_zone']}: Total={z['nombre_total_lots']}, Attribues={z['lots_attribues']}, Disponibles={z['lots_disponibles']}, Taux={z['taux_occupation_pct']}%")
