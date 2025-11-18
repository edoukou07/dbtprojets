#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=sigeti_node_db user=postgres password=postgres host=localhost')
cur = conn.cursor()

# Get financial KPIs by period
print("=== KPIs Financier par Période ===\n")
cur.execute('''
    SELECT 
        annee, 
        mois, 
        SUM(montant_total_facture)::bigint as ca_total, 
        SUM(montant_paye)::bigint as ca_paye,
        ROUND(AVG(taux_paiement_pct)::numeric, 2) as taux_paiement
    FROM dwh_marts_financier.mart_performance_financiere 
    GROUP BY annee, mois 
    ORDER BY annee DESC, mois DESC
    LIMIT 10
''')

rows = cur.fetchall()
for r in rows:
    print(f"Année {r[0]} Mois {r[1]:02d}: CA Total={r[2]:,} FCFA, CA Payé={r[3]:,} FCFA, Taux Paiement={r[4]}%")

# Get annual totals for 2025
print("\n=== Totals 2025 (Annuel) ===")
cur.execute('''
    SELECT 
        SUM(montant_total_facture)::bigint as ca_total_2025,
        SUM(montant_paye)::bigint as ca_paye_2025,
        ROUND(AVG(taux_paiement_pct)::numeric, 2) as taux_paiement_2025
    FROM dwh_marts_financier.mart_performance_financiere 
    WHERE annee = 2025
''')
r = cur.fetchone()
if r:
    print(f"CA Total 2025: {r[0]:,} FCFA")
    print(f"CA Payé 2025: {r[1]:,} FCFA")
    print(f"Taux Paiement 2025: {r[2]}%")

conn.close()
print("\n✅ Vérification terminée")
