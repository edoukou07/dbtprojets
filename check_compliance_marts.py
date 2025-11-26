import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='sigeti_node_db', user='postgres', password='postgres')
cur = conn.cursor()

cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema='dwh_marts_compliance'
    ORDER BY table_name
""")
print('Marts in dwh_marts_compliance:')
tables = cur.fetchall()
for row in tables:
    print(f'  - {row[0]}')
    
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema='dwh_marts_compliance' AND table_name='{row[0]}'
        ORDER BY ordinal_position
    """)
    for col in cur.fetchall():
        print(f'      {col[0]}: {col[1]}')

conn.close()
