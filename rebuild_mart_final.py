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

print("=== Clear and rebuild mart ===")

# Clear the mart table
cursor.execute('DELETE FROM "dwh_marts_occupation"."mart_occupation_zones"')

# Rebuild with correct logic
sql_fix = '''
WITH zones as (
    SELECT 
        id,
        libelle as nom_zone
    FROM zones_industrielles
),

occupation_data as (
    SELECT
        z.id as zone_id,
        z.nom_zone,
        COUNT(l.id) as nombre_total_lots,
        COUNT(CASE WHEN l.statut::text = 'disponible' THEN 1 END) as lots_disponibles,
        COUNT(DISTINCT CASE 
            WHEN EXISTS (
                SELECT 1 FROM demandes_attribution da 
                WHERE da.lot_id = l.id AND da.statut = 'VALIDE'
            ) THEN l.id
        END) as lots_attribues,
        COUNT(CASE 
            WHEN l.statut::text != 'disponible' 
            AND NOT EXISTS (
                SELECT 1 FROM demandes_attribution da
                WHERE da.lot_id = l.id AND da.statut = 'VALIDE'
            )
            THEN 1 
        END) as lots_reserves,
        SUM(l.superficie) as superficie_totale,
        SUM(CASE WHEN l.statut::text = 'disponible' THEN l.superficie ELSE 0 END) as superficie_disponible,
        SUM(CASE 
            WHEN EXISTS (
                SELECT 1 FROM demandes_attribution da 
                WHERE da.lot_id = l.id AND da.statut = 'VALIDE'
            )
            THEN l.superficie 
            ELSE 0 
        END) as superficie_attribuee,
        ROUND(
            (COUNT(DISTINCT CASE 
                WHEN EXISTS (
                    SELECT 1 FROM demandes_attribution da 
                    WHERE da.lot_id = l.id AND da.statut = 'VALIDE'
                ) THEN l.id
            END)::numeric 
             / NULLIF(COUNT(l.id), 0)::numeric * 100), 
            2
        ) as taux_occupation_pct,
        SUM(l.prix) as valeur_totale_lots,
        SUM(CASE WHEN l.statut::text = 'disponible' THEN l.prix ELSE 0 END) as valeur_lots_disponibles,
        COUNT(CASE WHEN l.viabilite = true THEN 1 END) as lots_viabilises,
        ROUND(
            (COUNT(CASE WHEN l.viabilite = true THEN 1 END)::numeric 
             / NULLIF(COUNT(l.id), 0)::numeric * 100), 
            2
        ) as taux_viabilisation_pct
    FROM zones z
    LEFT JOIN lots l ON l.zone_industrielle_id = z.id
    GROUP BY z.id, z.nom_zone
)

INSERT INTO "dwh_marts_occupation"."mart_occupation_zones"
(
    zone_id, nom_zone, nombre_total_lots, lots_disponibles, lots_attribues, lots_reserves,
    superficie_totale, superficie_disponible, superficie_attribuee, taux_occupation_pct,
    valeur_totale_lots, valeur_lots_disponibles, lots_viabilises, taux_viabilisation_pct,
    nombre_demandes_attribution, demandes_approuvees, demandes_rejetees, demandes_en_attente,
    delai_moyen_traitement, taux_approbation_pct
)
SELECT 
    zone_id, nom_zone, nombre_total_lots, lots_disponibles, lots_attribues, lots_reserves,
    superficie_totale, superficie_disponible, superficie_attribuee, taux_occupation_pct,
    valeur_totale_lots, valeur_lots_disponibles, lots_viabilises, taux_viabilisation_pct,
    NULL, NULL, NULL, NULL, NULL, NULL
FROM occupation_data
WHERE nombre_total_lots > 0
ORDER BY nom_zone
'''

cursor.execute(sql_fix)
connection.commit()
print('✓ Mart rebuilt!')

print("\n=== VERIFICATION: Lot accounting ===")
cursor.execute('''
SELECT 
    nom_zone,
    nombre_total_lots,
    lots_attribues,
    lots_disponibles,
    lots_reserves,
    (lots_attribues + lots_disponibles + lots_reserves) as total_check,
    CASE 
        WHEN (lots_attribues + lots_disponibles + lots_reserves) = nombre_total_lots THEN '✓'
        ELSE '✗ MISMATCH'
    END as status,
    taux_occupation_pct
FROM "dwh_marts_occupation"."mart_occupation_zones"
ORDER BY nom_zone
''')

for nom, total, attrib, dispo, reserves, check, status, taux in cursor.fetchall():
    print(f'{nom}:')
    print(f'  Total={total}, Attribués={attrib}, Disponibles={dispo}, Réservés={reserves}')
    print(f'  Check={check} {status}, Taux={taux}%')
