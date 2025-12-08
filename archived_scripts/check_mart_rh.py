import psycopg2

# Connexion à la base de données
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    dbname='sigeti_node_db',
    user='postgres',
    password='Minsiticloud@2024'
)

cur = conn.cursor()

print("=" * 80)
print("VERIFICATION MART RH - mart_agents_productivite")
print("=" * 80)

# Statistiques globales
cur.execute("""
    SELECT 
        COUNT(*) as total_agents,
        SUM(nombre_collectes) as total_collectes,
        ROUND(AVG(taux_recouvrement_moyen_pct), 2) as taux_moyen,
        ROUND(AVG(delai_moyen_traitement_jours), 2) as delai_moyen
    FROM dwh_marts_rh.mart_agents_productivite
""")

row = cur.fetchone()
print(f"\n📊 Statistiques globales:")
print(f"  - Nombre d'agents: {row[0]}")
print(f"  - Total collectes: {row[1]}")
print(f"  - Taux recouvrement moyen: {row[2]}%")
print(f"  - Délai moyen traitement: {row[3]} jours")

# Top 5 agents par productivité
cur.execute("""
    SELECT 
        nom_complet,
        nombre_collectes,
        montant_total_recouvre,
        taux_recouvrement_moyen_pct,
        rang_productivite_global
    FROM dwh_marts_rh.mart_agents_productivite
    ORDER BY montant_total_recouvre DESC NULLS LAST
    LIMIT 5
""")

print(f"\n🏆 Top 5 agents par montant recouvré:")
for row in cur.fetchall():
    print(f"  {row[4]}. {row[0]}: {row[2]:,.0f} XOF ({row[1]} collectes, {row[3]}% taux)")

# Distribution des agents par nombre de collectes
cur.execute("""
    SELECT 
        CASE 
            WHEN nombre_collectes = 0 THEN '0 collecte'
            WHEN nombre_collectes BETWEEN 1 AND 5 THEN '1-5 collectes'
            WHEN nombre_collectes BETWEEN 6 AND 10 THEN '6-10 collectes'
            ELSE '11+ collectes'
        END as categorie,
        COUNT(*) as nombre_agents
    FROM dwh_marts_rh.mart_agents_productivite
    GROUP BY 
        CASE 
            WHEN nombre_collectes = 0 THEN '0 collecte'
            WHEN nombre_collectes BETWEEN 1 AND 5 THEN '1-5 collectes'
            WHEN nombre_collectes BETWEEN 6 AND 10 THEN '6-10 collectes'
            ELSE '11+ collectes'
        END
    ORDER BY MIN(nombre_collectes)
""")

print(f"\n📈 Distribution par nombre de collectes:")
for row in cur.fetchall():
    print(f"  - {row[0]}: {row[1]} agents")

conn.close()
print("\n" + "=" * 80)
