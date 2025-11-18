#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=sigeti_node_db user=postgres password=postgres host=localhost')
cur = conn.cursor()

print("=" * 70)
print("VÉRIFICATION DES KPIs OPÉRATIONNELS")
print("=" * 70)

# Check operationnel mart data
print("\n1. DONNÉES BRUTES DE mart_kpi_operationnels:")
cur.execute("""
    SELECT 
        annee,
        trimestre,
        nombre_collectes,
        nombre_demandes,
        demandes_approuvees,
        demandes_rejetees,
        demandes_en_attente,
        taux_recouvrement_global_pct,
        nombre_factures_emises
    FROM dwh_marts_operationnel.mart_kpi_operationnels
    ORDER BY annee DESC, trimestre DESC
""")

for row in cur.fetchall():
    print(f"  Année {row[0]} Q{row[1]}: " + 
          f"Collectes={row[2]}, Demandes={row[3]}, " +
          f"Approuvées={row[4]}, Rejetées={row[5]}, En Attente={row[6]}, " +
          f"Taux Recouvrement={row[7]}%, Factures={row[8]}")

# Summary for 2025
print("\n2. RÉSUMÉ 2025 (AGRÉGÉ SUR TOUS LES TRIMESTRES):")
cur.execute("""
    SELECT 
        SUM(nombre_collectes) as total_collectes,
        SUM(nombre_demandes) as total_demandes,
        SUM(demandes_approuvees) as total_approuvees,
        SUM(demandes_rejetees) as total_rejetees,
        SUM(demandes_en_attente) as total_en_attente,
        ROUND(AVG(taux_recouvrement_global_pct)::numeric, 2) as taux_moyen_recouvrement,
        SUM(nombre_factures_emises) as total_factures
    FROM dwh_marts_operationnel.mart_kpi_operationnels
    WHERE annee = 2025
""")

row = cur.fetchone()
if row:
    print(f"  Total Collectes 2025: {row[0]}")
    print(f"  Total Demandes 2025: {row[1]}")
    print(f"  Demandes Approuvées 2025: {row[2]}")
    print(f"  Demandes Rejetées 2025: {row[3]}")
    print(f"  Demandes En Attente 2025: {row[4]}")
    print(f"  Taux Recouvrement Moyen 2025: {row[5]}%")
    print(f"  Total Factures 2025: {row[6]}")

# Check Q4 2025 specifically (like dashboard)
print("\n3. Q4 2025 (CE QUE LE DASHBOARD AFFICHE):")
cur.execute("""
    SELECT 
        nombre_collectes,
        nombre_demandes,
        demandes_approuvees,
        demandes_rejetees,
        demandes_en_attente,
        taux_recouvrement_global_pct,
        nombre_factures_emises
    FROM dwh_marts_operationnel.mart_kpi_operationnels
    WHERE annee = 2025 AND trimestre = 4
""")

row = cur.fetchone()
if row:
    print(f"  Collectes Q4 2025: {row[0]}")
    print(f"  Demandes Q4 2025: {row[1]}")
    print(f"  Demandes Approuvées Q4 2025: {row[2]}")
    print(f"  Demandes Rejetées Q4 2025: {row[3]}")
    print(f"  Demandes En Attente Q4 2025: {row[4]}")
    print(f"  Taux Recouvrement Q4 2025: {row[5]}%")
    print(f"  Factures Q4 2025: {row[6]}")
else:
    print("  ❌ Pas de données Q4 2025")

conn.close()
print("\n✅ Vérification terminée")
