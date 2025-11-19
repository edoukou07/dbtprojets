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

# Debugging: Check the actual data
print("=== DEBUG: Lots in Yopougon ===")
cursor.execute('''
SELECT 
    l.id,
    l.numero,
    l.statut::text,
    l.entreprise_id,
    da.statut as demande_statut
FROM lots l
LEFT JOIN demandes_attribution da ON l.id = da.lot_id
WHERE l.zone_industrielle_id = (
    SELECT id FROM zones_industrielles WHERE libelle ILIKE '%Yopougon%'
)
ORDER BY l.id
''')

for lot_id, numero, statut, entreprise_id, demande_statut in cursor.fetchall():
    print(f"  Lot {lot_id} (#{numero}): statut={statut!r}, entreprise_id={entreprise_id}, demande_statut={demande_statut}")

print("\n=== DEBUG: Demandes Attribution for Yopougon ===")
cursor.execute('''
SELECT DISTINCT 
    da.lot_id,
    da.statut,
    COUNT(*) as cnt
FROM demandes_attribution da
WHERE da.lot_id IN (
    SELECT id FROM lots 
    WHERE zone_industrielle_id = (
        SELECT id FROM zones_industrielles WHERE libelle ILIKE '%Yopougon%'
    )
)
GROUP BY da.lot_id, da.statut
ORDER BY da.lot_id
''')

for lot_id, statut, cnt in cursor.fetchall():
    print(f"  Lot {lot_id}: demande statut={statut} (count={cnt})")

print("\n=== Recalculating with correct logic ===")

# The issue: We're counting lots_reserves as all non-disponible lots
# But we should only count those without a VALIDE demande
sql_fix = '''
DELETE FROM "dwh_marts_occupation"."mart_occupation_zones";

WITH zones as (
    SELECT 
        z.id as zone_id,
        z.libelle as nom_zone
    FROM zones_industrielles z
),

occupation_data as (
    SELECT
        z.zone_id,
        z.nom_zone,
        COUNT(l.id) as nombre_total_lots,
        COUNT(CASE WHEN l.statut::text = 'disponible' THEN 1 END) as lots_disponibles,
        COUNT(DISTINCT CASE 
            WHEN da.statut = 'VALIDE' THEN da.lot_id 
        END) as lots_attribues,
        COUNT(CASE 
            WHEN l.statut::text != 'disponible' 
            AND NOT EXISTS (
                SELECT 1 FROM demandes_attribution da2 
                WHERE da2.lot_id = l.id AND da2.statut = 'VALIDE'
            )
            THEN 1 
        END) as lots_reserves,
        SUM(l.superficie) as superficie_totale,
        SUM(CASE WHEN l.statut::text = 'disponible' THEN l.superficie ELSE 0 END) as superficie_disponible,
        SUM(CASE 
            WHEN da.statut = 'VALIDE' THEN l.superficie 
            ELSE 0 
        END) as superficie_attribuee,
        ROUND(
            (COUNT(DISTINCT CASE WHEN da.statut = 'VALIDE' THEN da.lot_id END)::numeric 
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
    LEFT JOIN demandes_attribution da ON l.id = da.lot_id AND da.statut = 'VALIDE'
    GROUP BY z.zone_id, z.nom_zone
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
ORDER BY nom_zone;
'''

cursor.execute(sql_fix)
connection.commit()
print('✓ Mart fixed!')

print("\n=== VERIFICATION ===")
cursor.execute('''
SELECT 
    nom_zone,
    nombre_total_lots,
    lots_attribues,
    lots_disponibles,
    lots_reserves,
    (lots_attribues + lots_disponibles + lots_reserves) as total_check,
    taux_occupation_pct
FROM "dwh_marts_occupation"."mart_occupation_zones"
ORDER BY nom_zone
''')

results = cursor.fetchall()
for nom, total, attrib, dispo, reserves, check, taux in results:
    if total > 0:
        match = "✓" if check == total else "✗ MISMATCH"
        print(f'{nom}: Total={total}, Attribués={attrib}, Disponibles={dispo}, Réservés={reserves}, Check={check} {match}, Taux={taux}%')
