import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host="localhost",
        database="sigeti_node_db",
        user="postgres",
        password="sigeti123"
    )
    cursor = conn.cursor()
    
    # Test the corrected SQL logic
    sql = """
    WITH factures AS (
        SELECT * FROM dwh_facts.fait_factures
    ),
    temps AS (
        SELECT * FROM dwh_dimensions.dim_temps
    ),
    collectes AS (
        SELECT * FROM dwh_facts.fait_collectes
    ),
    paiements_par_collecte AS (
        SELECT
            f.collecte_id,
            t.annee,
            t.trimestre,
            SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) as montant_paye_collecte
        FROM factures f
        JOIN temps t ON f.date_creation_key = t.date_key
        WHERE f.collecte_id IS NOT NULL
        GROUP BY f.collecte_id, t.annee, t.trimestre
    )
    SELECT 
        t.annee,
        t.trimestre,
        COUNT(DISTINCT c.collecte_id) as nombre_collectes,
        COALESCE(SUM(pc.montant_paye_collecte), 0) as montant_total_recouvre
    FROM collectes c
    JOIN temps t ON c.date_debut_key = t.date_key
    LEFT JOIN paiements_par_collecte pc ON c.collecte_id = pc.collecte_id
        AND t.annee = pc.annee
        AND t.trimestre = pc.trimestre
    GROUP BY t.annee, t.trimestre
    ORDER BY t.annee, t.trimestre
    """
    
    cursor.execute(sql)
    print("CORRECTED AGGREGATION (facture-based):")
    for row in cursor.fetchall():
        print(f"  Year {row[0]}, Q{row[1]}: collectes={row[2]}, recouvre={row[3]:,.0f}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
