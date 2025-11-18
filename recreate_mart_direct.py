
import psycopg2
from psycopg2 import sql
conn_params = {
    'host': 'localhost',
    'port': '5432',
    'database': 'sigeti_node_db',
    'user': 'sigeti_user',
    'password': 'sigeti_Dgvt2024'
}
def recreate_mart():
    """Recreate mart_performance_financiere table with corrected logic"""
    conn = None
    cursor = None
    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        print("✓ Connected to sigeti_node_db")
        print("\nDropping old mart_performance_financiere table...")
        cursor.execute("DROP TABLE IF EXISTS dwh_marts_financier.mart_performance_financiere CASCADE")
        conn.commit()
        print("✓ Old table dropped")
        print("\nCreating corrected mart_performance_financiere table...")
        create_sql = """
        CREATE TABLE dwh_marts_financier.mart_performance_financiere AS
        WITH factures AS (
            SELECT * FROM dwh_facts.fait_factures
        ),
        collectes AS (
            SELECT * FROM dwh_facts.fait_collectes
        ),
        temps AS (
            SELECT DISTINCT
                annee,
                mois,
                trimestre
            FROM dwh_dimensions.dim_temps
        ),
        factures_aggregees AS (
            SELECT
                t.annee,
                t.mois,
                t.trimestre,
                COUNT(DISTINCT f.facture_id) as nombre_factures,
                SUM(f.montant_total) as montant_total_facture,
                SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) as montant_paye,
                SUM(CASE WHEN NOT f.est_paye THEN f.montant_total ELSE 0 END) as montant_impaye,
                AVG(COALESCE(f.delai_paiement_jours, 0)) as delai_moyen_paiement,
                ROUND(
                    (SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END)::NUMERIC / 
                     NULLIF(SUM(f.montant_total), 0)::NUMERIC * 100), 
                    2
                ) as taux_paiement_pct
            FROM factures f
            LEFT JOIN temps t ON EXTRACT(YEAR FROM f.date_creation) = t.annee
                AND EXTRACT(MONTH FROM f.date_creation) = t.mois
            WHERE t.annee IS NOT NULL
            GROUP BY 
                t.annee,
                t.mois,
                t.trimestre
        ),
        collectes_aggregees AS (
            SELECT
                t.annee,
                t.trimestre,
                COUNT(DISTINCT c.collecte_id) as nombre_collectes,
                SUM(c.montant_a_recouvrer) as montant_total_a_recouvrer,
                SUM(CASE WHEN c.montant_total_recouvre > 0 THEN c.montant_total_recouvre ELSE 0 END) as montant_total_recouvre,
                AVG(COALESCE(c.taux_recouvrement, 0)) as taux_recouvrement_moyen,
                AVG(ABS(COALESCE(c.duree_reelle_jours, 0))) as duree_moyenne_collecte
            FROM collectes c
            LEFT JOIN temps t ON EXTRACT(YEAR FROM c.date_debut) = t.annee
                AND c.trimestre = t.trimestre
            WHERE t.annee IS NOT NULL
            GROUP BY 
                t.annee,
                t.trimestre
        )
        SELECT
            f.annee,
            f.mois,
            f.trimestre,
            f.nombre_factures,
            f.montant_total_facture,
            f.montant_paye,
            f.montant_impaye,
            f.delai_moyen_paiement,
            f.taux_paiement_pct,
            COALESCE(c.nombre_collectes, 0) as nombre_collectes,
            COALESCE(c.montant_total_a_recouvrer, 0) as montant_total_a_recouvrer,
            COALESCE(c.montant_total_recouvre, 0) as montant_total_recouvre,
            COALESCE(c.taux_recouvrement_moyen, 0) as taux_recouvrement_moyen,
            COALESCE(c.duree_moyenne_collecte, 0) as duree_moyenne_collecte
        FROM factures_aggregees f
        LEFT JOIN collectes_aggregees c 
            ON f.annee = c.annee 
            AND f.trimestre = c.trimestre
        """
        cursor.execute(create_sql)
        conn.commit()
        print("✓ Table created successfully")
        print("\nCreating indexes...")
        cursor.execute("CREATE INDEX idx_mart_perf_annee ON dwh_marts_financier.mart_performance_financiere(annee)")
        cursor.execute("CREATE INDEX idx_mart_perf_annee_trimestre ON dwh_marts_financier.mart_performance_financiere(annee, trimestre)")
        conn.commit()
        print("✓ Indexes created")
        print("\nVerifying data...")
        cursor.execute("SELECT COUNT(*) FROM dwh_marts_financier.mart_performance_financiere")
        count = cursor.fetchone()[0]
        print(f"✓ Table contains {count} rows")
        cursor.execute("""
            SELECT 
                annee, 
                trimestre, 
                montant_total_recouvre,
                duree_moyenne_collecte,
                montant_total_facture
            FROM dwh_marts_financier.mart_performance_financiere
            ORDER BY annee DESC, trimestre DESC
            LIMIT 5
        """)
        print("\nSample data:")
        for row in cursor.fetchall():
            print(f"  Year {row[0]}, Q{row[1]}: recouvre={row[2]:,.0f}, duree_moy={row[3]:.1f} days, factures={row[4]:,.0f}")
        print("\n✅ SUCCESS - Mart table recreated!")
        print("✅ Duree moyenne should now show POSITIVE values")
        print("✅ Montant total recouvre calculated from factures (not collectes)")
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return True
if __name__ == "__main__":
    recreate_mart()
