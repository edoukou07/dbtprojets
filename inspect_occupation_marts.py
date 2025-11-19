#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=sigeti_node_db user=postgres password=postgres host=localhost')
cur = conn.cursor()

print("=== DONNÉES BRUTES mart_occupation_zones ===\n")
cur.execute("""
    SELECT 
        zone_id,
        nombre_total_lots,
        lots_disponibles,
        lots_attribues,
        ROUND(taux_occupation_pct::numeric, 2) as taux,
        superficie_totale,
        superficie_disponible,
        superficie_attribuee
    FROM dwh_marts_occupation.mart_occupation_zones
""")

for row in cur.fetchall():
    print(f"Zone {row[0]}: {row[1]} lots, {row[3]} attribués, Taux={row[4]}%")

# Agrégations
print("\n=== AGRÉGATIONS ===")
cur.execute("""
    SELECT 
        SUM(nombre_total_lots) as total_lots,
        SUM(lots_disponibles) as lots_dispo,
        SUM(lots_attribues) as lots_attr,
        COUNT(*) as nb_zones,
        ROUND(SUM(lots_attribues)::numeric / SUM(nombre_total_lots)::numeric * 100, 2) as taux_occupation
    FROM dwh_marts_occupation.mart_occupation_zones
""")

row = cur.fetchone()
print(f"Total lots: {row[0]}")
print(f"Lots disponibles: {row[1]}")
print(f"Lots attribués: {row[2]}")
print(f"Nombre zones: {row[3]}")
print(f"Taux occupation global: {row[4]}%")

conn.close()
