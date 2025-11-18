#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=sigeti_node_db user=postgres password=postgres host=localhost')
cur = conn.cursor()

print("=== INSPECTION DE mart_kpi_operationnels ===\n")

# Count rows
cur.execute("SELECT COUNT(*) FROM dwh_marts_operationnel.mart_kpi_operationnels")
print(f"Total de lignes: {cur.fetchone()[0]}")

# Show all data
print("\nTOUTES LES LIGNES:")
cur.execute("""
    SELECT 
        annee,
        trimestre,
        nombre_collectes,
        collectes_cloturees,
        collectes_ouvertes,
        taux_recouvrement_global_pct,
        nombre_demandes,
        demandes_approuvees,
        demandes_rejetees,
        demandes_en_attente,
        nombre_factures_emises
    FROM dwh_marts_operationnel.mart_kpi_operationnels
    ORDER BY annee DESC, trimestre DESC
""")

for row in cur.fetchall():
    print(f"  {int(row[0])}.Q{int(row[1])}: " +
          f"Collectes={row[2]}, Demandes={row[6]}, " +
          f"Taux Recouvrement={row[5]}%")

conn.close()
