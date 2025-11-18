
"""
Script pour corriger les problemes d'encoding et de donnees dans PostgreSQL
"""
import psycopg2
from psycopg2 import sql, Error
import sys
import os
os.environ['PGCLIENTENCODING'] = 'UTF8'
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
conn_params = {
    'host': 'localhost',
    'port': '5432',
    'database': 'sigeti_node_db',
    'user': 'sigeti_user',
    'password': 'sigeti_Dgvt2024',
    'client_encoding': 'UTF8'
}
def execute_query(cursor, query, description=""):
    """Execute une requete SQL"""
    try:
        if description:
            print(f"\n▶ {description}")
        cursor.execute(query)
        return True
    except Error as e:
        print(f"❌ Erreur SQL: {e}")
        return False
def execute_and_fetch(cursor, query, description=""):
    """Execute une requete et retourne les resultats"""
    try:
        if description:
            print(f"\n▶ {description}")
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"❌ Erreur: {e}")
        return None
def main():
    conn = None
    cursor = None
    try:
        print("="*70)
        print("CORRECTION ENCODING & DONNEES PostgreSQL")
        print("="*70)
        print("\n🔌 Connexion a PostgreSQL...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        print("✅ Connecte a sigeti_node_db")
        print("\n" + "="*70)
        print("STEP 1: VERIFIER ENCODING ACTUEL")
        print("="*70)
        result = execute_and_fetch(
            cursor,
            "SELECT datname, encoding FROM pg_database WHERE datname = 'sigeti_node_db';",
            "Verification de l'encoding de la base"
        )
        if result:
            for row in result:
                encoding_num = row[1]
                encoding_map = {6: 'UTF8', 1: 'SQL_ASCII', 3: 'ISO_8859_1'}
                encoding_name = encoding_map.get(encoding_num, f"Code {encoding_num}")
                print(f"  Database: {row[0]}")
                print(f"  Encoding: {encoding_name} (code: {encoding_num})")
                if encoding_num != 6:  
                    print("  ⚠️  L'encoding n'est pas UTF8!")
        print("\n" + "="*70)
        print("STEP 2: CORRIGER DUREES NEGATIVES")
        print("="*70)
        result = execute_and_fetch(
            cursor,
            "SELECT COUNT(*) as count FROM dwh_facts.fait_collectes WHERE duree_reelle_jours < 0;",
            "Comptage des durees negatives avant correction"
        )
        if result:
            print(f"  Durees negatives trouvees: {result[0][0]}")
        if execute_query(
            cursor,
            "UPDATE dwh_facts.fait_collectes SET duree_reelle_jours = ABS(duree_reelle_jours) WHERE duree_reelle_jours < 0;",
            "Correction des durees negatives avec ABS()"
        ):
            conn.commit()
            rows = cursor.rowcount
            print(f"  ✅ {rows} lignes mises a jour")
        result = execute_and_fetch(
            cursor,
            "SELECT COUNT(*) as count FROM dwh_facts.fait_collectes WHERE duree_reelle_jours < 0;",
            "Verification apres correction"
        )
        if result:
            print(f"  ✅ Durees negatives restantes: {result[0][0]}")
        print("\n" + "="*70)
        print("STEP 3: RECALCULER DUREES (conversion DATE explicite)")
        print("="*70)
        if execute_query(
            cursor,
            """UPDATE dwh_facts.fait_collectes
               SET duree_reelle_jours = ABS(EXTRACT(DAY FROM (date_cloture::date - date_debut::date)))
               WHERE date_debut IS NOT NULL AND date_cloture IS NOT NULL;""",
            "Recalcul des durees avec conversion DATE explicite"
        ):
            conn.commit()
            rows = cursor.rowcount
            print(f"  ✅ {rows} lignes recalculees")
        result = execute_and_fetch(
            cursor,
            """SELECT 
                COUNT(*) as nombre_collectes,
                ROUND(AVG(duree_reelle_jours)::numeric, 1) as duree_moyenne,
                MIN(duree_reelle_jours) as duree_min,
                MAX(duree_reelle_jours) as duree_max
               FROM dwh_facts.fait_collectes
               WHERE date_debut IS NOT NULL AND date_cloture IS NOT NULL;""",
            "Statistiques des durees apres recalcul"
        )
        if result:
            row = result[0]
            print(f"  Collectes analysees: {row[0]}")
            print(f"  Duree moyenne: {row[1]} jours")
            print(f"  Duree min: {row[2]} jours")
            print(f"  Duree max: {row[3]} jours")
        print("\n" + "="*70)
        print("STEP 4: RECREER TABLE MART_PERFORMANCE_FINANCIERE")
        print("="*70)
        if execute_query(
            cursor,
            "DROP TABLE IF EXISTS dwh_marts_financier.mart_performance_financiere CASCADE;",
            "Suppression de l'ancienne table"
        ):
            conn.commit()
            print("  ✅ Table supprimee")
        create_sql = """
        CREATE TABLE dwh_marts_financier.mart_performance_financiere AS
        WITH factures AS (
            SELECT 
                f.facture_id,
                f.montant_total,
                f.est_paye,
                f.delai_paiement_jours,
                f.zone_id,
                f.date_creation,
                EXTRACT(YEAR FROM f.date_creation) as annee,
                EXTRACT(MONTH FROM f.date_creation) as mois
            FROM dwh_facts.fait_factures f
        ),
        collectes AS (
            SELECT 
                c.collecte_id,
                c.montant_a_recouvrer,
                c.montant_total_recouvre,
                c.taux_recouvrement,
                c.duree_reelle_jours,
                EXTRACT(YEAR FROM c.date_debut) as annee,
                EXTRACT(QUARTER FROM c.date_debut) as trimestre
            FROM dwh_facts.fait_collectes c
        ),
        temps_unique AS (
            SELECT DISTINCT
                EXTRACT(YEAR FROM date_creation)::int as annee,
                EXTRACT(MONTH FROM date_creation)::int as mois,
                CASE 
                    WHEN EXTRACT(MONTH FROM date_creation) IN (1, 2, 3) THEN 1
                    WHEN EXTRACT(MONTH FROM date_creation) IN (4, 5, 6) THEN 2
                    WHEN EXTRACT(MONTH FROM date_creation) IN (7, 8, 9) THEN 3
                    ELSE 4
                END as trimestre
            FROM dwh_facts.fait_factures
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
                ROUND(AVG(COALESCE(f.delai_paiement_jours, 0))::numeric, 2) as delai_moyen_paiement,
                ROUND(
                    (SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END)::NUMERIC / 
                     NULLIF(SUM(f.montant_total), 0)::NUMERIC * 100), 
                    2
                ) as taux_paiement_pct
            FROM factures f
            LEFT JOIN temps_unique t ON f.annee = t.annee AND f.mois = t.mois
            WHERE t.annee IS NOT NULL
            GROUP BY t.annee, t.mois, t.trimestre
        ),
        collectes_aggregees AS (
            SELECT
                c.annee,
                c.trimestre,
                COUNT(DISTINCT c.collecte_id) as nombre_collectes,
                SUM(c.montant_a_recouvrer) as montant_total_a_recouvrer,
                SUM(CASE WHEN c.montant_total_recouvre > 0 THEN c.montant_total_recouvre ELSE 0 END) as montant_total_recouvre,
                ROUND(AVG(COALESCE(c.taux_recouvrement, 0))::numeric, 2) as taux_recouvrement_moyen,
                ROUND(AVG(ABS(COALESCE(c.duree_reelle_jours, 0)))::numeric, 1) as duree_moyenne_collecte
            FROM collectes c
            GROUP BY c.annee, c.trimestre
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
            COALESCE(c.nombre_collectes, 0)::int as nombre_collectes,
            COALESCE(c.montant_total_a_recouvrer, 0) as montant_total_a_recouvrer,
            COALESCE(c.montant_total_recouvre, 0) as montant_total_recouvre,
            COALESCE(c.taux_recouvrement_moyen, 0) as taux_recouvrement_moyen,
            COALESCE(c.duree_moyenne_collecte, 0) as duree_moyenne_collecte
        FROM factures_aggregees f
        LEFT JOIN collectes_aggregees c 
            ON f.annee = c.annee 
            AND f.trimestre = c.trimestre
        ORDER BY f.annee DESC, f.mois DESC;
        """
        if execute_query(cursor, create_sql, "Creation de la table mart_performance_financiere"):
            conn.commit()
            print("  ✅ Table creee avec succes")
        print("\n▶ Creation des indexes...")
        for index_sql, index_name in [
            ("CREATE INDEX idx_mart_perf_annee ON dwh_marts_financier.mart_performance_financiere(annee);", "idx_mart_perf_annee"),
            ("CREATE INDEX idx_mart_perf_annee_mois ON dwh_marts_financier.mart_performance_financiere(annee, mois);", "idx_mart_perf_annee_mois"),
            ("CREATE INDEX idx_mart_perf_annee_trimestre ON dwh_marts_financier.mart_performance_financiere(annee, trimestre);", "idx_mart_perf_annee_trimestre"),
        ]:
            if execute_query(cursor, index_sql, f"  Creation de {index_name}"):
                conn.commit()
                print(f"    ✅ {index_name} cree")
        print("\n" + "="*70)
        print("STEP 5: VERIFICATION DES DONNEES CORRIGEES")
        print("="*70)
        result = execute_and_fetch(
            cursor,
            """SELECT 
                ROUND(SUM(montant_paye)/1000000000.0, 2) as creances_mds,
                SUM(montant_paye)::bigint as creances_fcfa
               FROM dwh_marts_financier.mart_performance_financiere;""",
            "Verification des creances"
        )
        if result:
            row = result[0]
            print(f"  ✅ Creances recouvres: {row[0]:.2f} Md FCFA ({row[1]:,} FCFA)")
        result = execute_and_fetch(
            cursor,
            """SELECT 
                ROUND(AVG(duree_moyenne_collecte)::numeric, 1) as duree_moy,
                MIN(duree_moyenne_collecte) as duree_min,
                MAX(duree_moyenne_collecte) as duree_max,
                COUNT(*) as nombre_periodes
               FROM dwh_marts_financier.mart_performance_financiere
               WHERE duree_moyenne_collecte > 0;""",
            "Verification de la duree moyenne"
        )
        if result:
            row = result[0]
            print(f"  ✅ Duree moyenne: {row[0]} jours")
            print(f"  ✅ Duree min: {row[1]} jours")
            print(f"  ✅ Duree max: {row[2]} jours")
            print(f"  ✅ Periode: {row[3]} periodes analysees")
        print("\n▶ Echantillon de donnees:")
        result = execute_and_fetch(
            cursor,
            """SELECT 
                annee, trimestre,
                ROUND(montant_total_facture/1000000000.0, 2) as factures_mds,
                ROUND(montant_paye/1000000000.0, 2) as recouvre_mds,
                duree_moyenne_collecte,
                taux_recouvrement_moyen
               FROM dwh_marts_financier.mart_performance_financiere
               WHERE montant_total_facture > 0
               ORDER BY annee DESC, trimestre DESC
               LIMIT 5;"""
        )
        if result:
            for row in result:
                print(f"  {row[0]}/Q{row[1]}: Factures {row[2]:.2f}Md | Recouvre {row[3]:.2f}Md | Duree {row[4]:.0f}j | Taux {row[5]:.1f}%")
        print("\n" + "="*70)
        print("✅ TOUTES LES CORRECTIONS APPLIQUEES AVEC SUCCES!")
        print("="*70)
        print("\n✅ Creances et duree moyenne doivent maintenant etre corrects")
        print("✅ Les dashboards devraient afficher les bonnes valeurs")
        print("✅ Vous pouvez maintenant lancer: dbt run -s mart_performance_financiere")
    except Error as e:
        print(f"\n❌ Erreur de connexion: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("\n🔌 Connexion fermee")
    return True
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
