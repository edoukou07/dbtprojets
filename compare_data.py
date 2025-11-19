#!/usr/bin/env python
import os
import sys
import django

# Ajouter le chemin du backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartOccupationZones
from django.db import connection
cursor = connection.cursor()

# Vérifier les données brutes de chaque zone
cursor.execute('''
SELECT 
    z.id,
    z.libelle,
    COUNT(DISTINCT l.id) as total_lots,
    COUNT(DISTINCT CASE WHEN da.id IS NOT NULL AND da.statut = 'VALIDE' THEN l.id END) as lots_attribues,
    COUNT(DISTINCT CASE WHEN l.statut = 'disponible' THEN l.id END) as lots_disponibles,
    SUM(l.prix) as valeur_totale
FROM zones_industrielles z
LEFT JOIN lots l ON z.id = l.zone_industrielle_id
LEFT JOIN demandes_attribution da ON l.id = da.lot_id
GROUP BY z.id, z.libelle
ORDER BY z.libelle
''')

zones_brutes = cursor.fetchall()

print('Donnees brutes de la base:')
print('=' * 100)
for z in zones_brutes:
    zone_id, nom, total, attrib, dispo, valeur = z
    if total > 0:
        taux = (attrib / total) * 100
    else:
        taux = 0
    print(f'{nom}: ID={zone_id}, Total={total}, Attribues={attrib}, Disponibles={dispo}, Taux={taux:.2f}%')

print('\n\nDonnees dans la mart:')
print('=' * 100)
mart_zones = MartOccupationZones.objects.all().order_by('nom_zone')
for z in mart_zones:
    print(f'{z.nom_zone}: Total={z.nombre_total_lots}, Attribues={z.lots_attribues}, Disponibles={z.lots_disponibles}, Taux={z.taux_occupation_pct}%')
