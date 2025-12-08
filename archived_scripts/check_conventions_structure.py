import psycopg2
from psycopg2 import sql

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="sigeti_node_db",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

# Get all columns from conventions table
query = """
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'conventions'
ORDER BY ordinal_position;
"""

cursor.execute(query)
columns = cursor.fetchall()

print("=" * 80)
print("STRUCTURE DE LA TABLE: conventions")
print("=" * 80)
print(f"{'Column Name':<40} {'Data Type':<20} {'Max Length':<10}")
print("-" * 80)

for col in columns:
    col_name, data_type, max_length = col
    max_len_str = str(max_length) if max_length else "N/A"
    print(f"{col_name:<40} {data_type:<20} {max_len_str:<10}")

print("=" * 80)
print(f"Total columns: {len(columns)}")
print("=" * 80)

# Check if specific columns exist
important_cols = ['entreprise_id', 'zone_industrielle_id', 'montant_convention', 
                  'date_limite_reponse', 'raison_rejet', 'approuve_par']

print("\nCOLONNES CRITIQUES POUR PHASE 1:")
print("-" * 80)

existing_cols = [col[0] for col in columns]
for col in important_cols:
    status = "✓ EXISTE" if col in existing_cols else "✗ MANQUANTE"
    print(f"{col:<40} {status}")

cursor.close()
conn.close()
