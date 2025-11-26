import psycopg2

conn = psycopg2.connect(
    host='localhost', 
    port=5432, 
    database='sigeti_node_db', 
    user='postgres', 
    password='postgres'
)
cur = conn.cursor()

# Check all schemas and tables with "mart" in name
cur.execute("""
    SELECT table_schema, table_name FROM information_schema.tables 
    WHERE table_name LIKE '%mart%' OR table_name LIKE '%conformite%'
    ORDER BY table_schema, table_name
""")
print("Tables with 'mart' or 'conformite' in name:")
for row in cur.fetchall():
    print(f'  {row[0]}.{row[1]}')

# Check if marts_operationnel schema exists
cur.execute("""
    SELECT schema_name FROM information_schema.schemata 
    WHERE schema_name = 'marts_operationnel'
""")
if cur.fetchone():
    print("\n✓ Schema 'marts_operationnel' EXISTS")
else:
    print("\n✗ Schema 'marts_operationnel' DOES NOT EXIST")

conn.close()

