import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='sigeti_node_db', user='postgres', password='postgres')
cursor = conn.cursor()

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users' ORDER BY ordinal_position;")
print('Colonnes users:', [r[0] for r in cursor.fetchall()])

cursor.close()
conn.close()
