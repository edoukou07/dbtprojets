#!/usr/bin/env python3
import psycopg

conn = psycopg.connect('dbname=sigeti_dwh user=postgres password=postgres host=localhost')
cur = conn.cursor()

# List all schemas
print("=== Tous les Schémas ===")
cur.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name")
for (schema,) in cur.fetchall():
    print(f"  {schema}")

# List all tables in dwh_marts_financier
print("\n=== Tables en dwh_marts_financier ===")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'dwh_marts_financier'
    ORDER BY table_name
""")
rows = cur.fetchall()
if rows:
    for (table,) in rows:
        print(f"  {table}")
else:
    print("  (No tables found)")

# Try to query the table
print("\n=== Test Query ===")
try:
    cur.execute("SELECT COUNT(*) FROM dwh_marts_financier.mart_performance_financiere")
    count = cur.fetchone()[0]
    print(f"✅ Table exists with {count} rows")
except psycopg.errors.UndefinedTable as e:
    print(f"❌ Table not found: {e}")

conn.close()
