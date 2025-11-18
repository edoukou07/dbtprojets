#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=sigeti_dwh user=postgres password=postgres host=localhost')
cur = conn.cursor()

# List all tables in marts schema
print("=== Toutes les Tables du Schéma 'marts' ===\n")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'marts'
    ORDER BY table_name
""")

for (table_name,) in cur.fetchall():
    print(table_name)

conn.close()
