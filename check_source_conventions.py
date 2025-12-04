"""
Vérifier l'état de la table source conventions
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    dbname='sigeti_node_db',
    user='postgres',
    password='Minsiticloud@2024'
)

cur = conn.cursor()

# Total et dates
cur.execute("SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM public.conventions")
row = cur.fetchone()
print(f"Total conventions: {row[0]}")
print(f"Date min: {row[1]}")
print(f"Date max: {row[2]}")

# Par statut
cur.execute("SELECT statut, COUNT(*) FROM public.conventions GROUP BY statut ORDER BY COUNT(*) DESC")
print("\nDistribution par statut:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

# Par forme juridique
cur.execute("SELECT forme_juridique, COUNT(*) FROM public.conventions WHERE forme_juridique IS NOT NULL GROUP BY forme_juridique ORDER BY COUNT(*) DESC")
print("\nDistribution par forme juridique:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

# Échantillon de données
cur.execute("SELECT id, raison_sociale, forme_juridique, domaine_activite, statut, created_at FROM public.conventions LIMIT 10")
print("\nÉchantillon de 10 conventions:")
print("-" * 120)
for r in cur.fetchall():
    print(f"ID: {r[0]:4d} | {r[1][:30]:30s} | {r[2]:10s} | {r[3][:40]:40s} | {r[4]:10s} | {r[5]}")

conn.close()
print("\n✓ Analyse terminée")
