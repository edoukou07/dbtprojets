#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=sigeti_node_db user=postgres password=postgres host=localhost')
cur = conn.cursor()

print("=" * 70)
print("VÉRIFICATION DES KPIs PORTEFEUILLE (CLIENTS)")
print("=" * 70)

# Check clients mart data
print("\n1. DONNÉES BRUTES DE mart_portefeuille_clients:")
cur.execute("""
    SELECT 
        COUNT(*) as nombre_clients,
        SUM(chiffre_affaires_total) as total_ca,
        SUM(ca_paye) as total_paye,
        SUM(ca_impaye) as total_impaye,
        ROUND(AVG(taux_paiement_pct)::numeric, 2) as taux_paiement_moyen
    FROM dwh_marts_clients.mart_portefeuille_clients
""")

row = cur.fetchone()
if row:
    print(f"  Total Clients: {row[0]}")
    print(f"  Total CA: {row[1]:,} FCFA")
    print(f"  Total Payé: {row[2]:,} FCFA")
    print(f"  Total Impayé: {row[3]:,} FCFA")
    print(f"  Taux Paiement Moyen: {row[4]}%")

# More details per client (top 5)
print("\n2. TOP 5 CLIENTS PAR CHIFFRE D'AFFAIRES:")
cur.execute("""
    SELECT 
        raison_sociale,
        chiffre_affaires_total,
        ca_paye,
        ca_impaye,
        ROUND(taux_paiement_pct::numeric, 2) as taux_paiement
    FROM dwh_marts_clients.mart_portefeuille_clients
    ORDER BY chiffre_affaires_total DESC
    LIMIT 5
""")

for i, row in enumerate(cur.fetchall(), 1):
    print(f"  {i}. {row[0]}: CA={row[1]:,}, Payé={row[2]:,}, Impayé={row[3]:,}, Taux={row[4]}%")

# Segmentation / risk analysis
print("\n3. DISTRIBUTION PAR TAUX DE PAIEMENT:")
cur.execute("""
    SELECT 
        CASE 
            WHEN taux_paiement_pct >= 90 THEN 'Excellent (≥90%)'
            WHEN taux_paiement_pct >= 70 THEN 'Bon (70-89%)'
            WHEN taux_paiement_pct >= 50 THEN 'Moyen (50-69%)'
            WHEN taux_paiement_pct >= 25 THEN 'Faible (25-49%)'
            ELSE 'Mauvais (<25%)'
        END as segment,
        COUNT(*) as nombre_clients,
        ROUND(AVG(taux_paiement_pct)::numeric, 2) as taux_moyen
    FROM dwh_marts_clients.mart_portefeuille_clients
    GROUP BY segment
    ORDER BY taux_moyen DESC
""")

for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} clients, Taux moyen={row[2]}%")

conn.close()
print("\n✅ Vérification terminée")
