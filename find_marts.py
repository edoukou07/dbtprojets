#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=sigeti_dwh user=postgres password=postgres host=localhost')
cur = conn.cursor()

# List all marts tables
print("=== Tables Marts Disponibles ===\n")
cur.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_name LIKE '%mart%' OR table_schema LIKE '%mart%'
    ORDER BY table_schema, table_name
""")

for schema, table in cur.fetchall():
    print(f"{schema}.{table}")

print("\n=== Recherche mart_performance_financiere ===")
cur.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_name LIKE '%performance%' OR table_name LIKE '%financiere%'
""")

for row in cur.fetchall():
    print(f"Found: {row[0]}.{row[1]}")

conn.close()
