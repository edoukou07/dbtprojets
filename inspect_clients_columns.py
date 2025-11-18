#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=sigeti_node_db user=postgres password=postgres host=localhost')
cur = conn.cursor()

cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'dwh_marts_clients' AND table_name = 'mart_portefeuille_clients'
    ORDER BY ordinal_position
""")

print("Colonnes de mart_portefeuille_clients:")
for name, dtype in cur.fetchall():
    print(f"  {name}: {dtype}")

conn.close()
