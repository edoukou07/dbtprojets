# Script de monitoring de l'entrepôt de données SIGETI
# Affiche des statistiques sur les données et la santé du DWH

import psycopg2
from datetime import datetime
from tabulate import tabulate
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': os.getenv('DWH_DB_NAME', 'sigeti_node_db'),
    'user': os.getenv('DWH_DB_USER', 'postgres'),
    'password': os.getenv('DBT_PASSWORD', 'postgres')
}

def get_connection():
    """Établit une connexion à la base de données"""
    return psycopg2.connect(**DB_CONFIG)

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80 + "\n")

def get_layer_stats(conn, layer_name, schema_name):
    """Récupère les statistiques pour une couche donnée"""
    cursor = conn.cursor()
    
    query = f"""
    SELECT 
        schemaname,
        tablename as object_name,
        CASE 
            WHEN schemaname LIKE '%staging%' THEN 'VIEW'
            WHEN schemaname LIKE '%marts%' THEN 'VIEW'
            ELSE 'TABLE'
        END as object_type,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
    FROM pg_tables
    WHERE schemaname LIKE '%{schema_name}%'
    ORDER BY tablename;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    
    return results

def get_row_counts(conn, schema_pattern):
    """Compte les lignes dans les tables/vues d'un schéma"""
    cursor = conn.cursor()
    
    # Récupérer toutes les tables/vues
    cursor.execute(f"""
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema LIKE '{schema_pattern}'
        AND table_type IN ('BASE TABLE', 'VIEW')
        ORDER BY table_name;
    """)
    
    objects = cursor.fetchall()
    results = []
    
    for schema, table, obj_type in objects:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}";')
            count = cursor.fetchone()[0]
            results.append([table, obj_type, f"{count:,}"])
        except Exception as e:
            results.append([table, obj_type, f"Erreur: {str(e)[:30]}"])
    
    cursor.close()
    return results

def get_latest_updates(conn):
    """Récupère les dernières mises à jour des tables de faits"""
    cursor = conn.cursor()
    
    fact_tables = ['fait_attributions', 'fait_collectes', 'fait_factures', 'fait_paiements']
    results = []
    
    for table in fact_tables:
        try:
            # Essayer de trouver une colonne de date
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'dwh_facts' 
                AND table_name = '{table}'
                AND (column_name LIKE '%date%' OR column_name LIKE '%created%')
                LIMIT 1;
            """)
            
            date_col = cursor.fetchone()
            if date_col:
                cursor.execute(f'SELECT MAX({date_col[0]}) FROM dwh_facts.{table};')
                max_date = cursor.fetchone()[0]
                results.append([table, date_col[0], str(max_date) if max_date else 'N/A'])
        except:
            results.append([table, 'N/A', 'Erreur'])
    
    cursor.close()
    return results

def main():
    """Fonction principale"""
    print("\n" + "🔍 " * 20)
    print_header(f"SIGETI DWH - Tableau de Bord de Monitoring - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        conn = get_connection()
        print("✅ Connexion à la base de données établie\n")
        
        # 1. Statistiques par couche
        print_header("📊 1. STATISTIQUES PAR COUCHE")
        
        layers = [
            ("Staging", "staging"),
            ("Dimensions", "dimensions"),
            ("Facts", "facts"),
            ("Marts - Clients", "marts_clients"),
            ("Marts - Financier", "marts_financier"),
            ("Marts - Occupation", "marts_occupation"),
            ("Marts - Opérationnel", "marts_operationnel")
        ]
        
        for layer_name, schema_pattern in layers:
            counts = get_row_counts(conn, f'%{schema_pattern}%')
            if counts:
                print(f"\n{layer_name}:")
                print(tabulate(counts, headers=["Objet", "Type", "Lignes"], tablefmt="grid"))
        
        # 2. Dernières mises à jour
        print_header("📅 2. DERNIÈRES MISES À JOUR DES TABLES DE FAITS")
        latest = get_latest_updates(conn)
        if latest:
            print(tabulate(latest, headers=["Table", "Colonne Date", "Dernière Valeur"], tablefmt="grid"))
        
        # 3. Résumé global
        print_header("📈 3. RÉSUMÉ GLOBAL")
        cursor = conn.cursor()
        
        # Compter les objets par schéma
        cursor.execute("""
            SELECT 
                table_schema,
                COUNT(*) as nb_objets,
                string_agg(DISTINCT table_type, ', ') as types
            FROM information_schema.tables
            WHERE table_schema LIKE 'dwh%'
            GROUP BY table_schema
            ORDER BY table_schema;
        """)
        
        summary = cursor.fetchall()
        print(tabulate(summary, headers=["Schéma", "Nombre d'Objets", "Types"], tablefmt="grid"))
        
        cursor.close()
        conn.close()
        
        print("\n✅ Analyse terminée avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
