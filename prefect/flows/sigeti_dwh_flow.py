"""
Flow Prefect pour orchestrer les transformations dbt du Data Warehouse SIGETI
"""

from prefect import flow, task
from prefect_dbt.cli.commands import DbtCoreOperation
from pathlib import Path
import os
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Configuration
DBT_PROJECT_DIR = Path(__file__).parent.parent.parent.absolute()
DBT_PROFILES_DIR = DBT_PROJECT_DIR

# Charger les variables d'environnement
load_dotenv(DBT_PROJECT_DIR / '.env')


@task(name="Create DWH Database if not exists", retries=1)
def create_dwh_database():
    """Crée la base de données DWH si elle n'existe pas"""
    
    dwh_host = os.getenv('DWH_DB_HOST', 'localhost')
    dwh_port = os.getenv('DWH_DB_PORT', '5432')
    dwh_user = os.getenv('DWH_DB_USER', 'postgres')
    dwh_password = os.getenv('DBT_PASSWORD')
    dwh_dbname = os.getenv('DWH_DB_NAME', 'sigeti_dwh')
    
    if not dwh_password:
        raise ValueError("DBT_PASSWORD non defini dans le fichier .env")
    
    print(f"[INFO] Verification de l'existence de la base de donnees '{dwh_dbname}'...")
    
    try:
        # Connexion à la base postgres par défaut pour créer la DB
        conn = psycopg2.connect(
            host=dwh_host,
            port=dwh_port,
            user=dwh_user,
            password=dwh_password,
            database='postgres'  # Connexion à postgres pour créer la DB
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Vérifier si la base existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (dwh_dbname,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"[OK] La base de donnees '{dwh_dbname}' existe deja")
        else:
            print(f"[CREATE] Creation de la base de donnees '{dwh_dbname}'...")
            cursor.execute(f'CREATE DATABASE {dwh_dbname}')
            print(f"[OK] Base de donnees '{dwh_dbname}' creee avec succes")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"[ERROR] Erreur PostgreSQL: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Erreur inattendue: {e}")
        raise


@task(name="Copy Source Tables to DWH", retries=2)
def copy_source_tables():
    """Copie les tables sources de sigeti_node_db vers sigeti_dwh via pg_dump"""
    
    import subprocess
    import tempfile
    
    source_dbname = 'sigeti_node_db'
    dwh_dbname = os.getenv('DWH_DB_NAME', 'sigeti_dwh')
    pg_password = os.getenv('SOURCE_DB_PASSWORD', 'postgres')
    pg_user = os.getenv('SOURCE_DB_USER', 'postgres')
    
    tables = [
        'entreprises',
        'lots',
        'zones_industrielles',
        'factures',
        'paiement_factures',
        'collectes',
        'demandes_attribution',
        'domaines_activites'
    ]
    
    print(f"[INFO] Copie des tables sources de {source_dbname} vers {dwh_dbname}...")
    
    # Définir PGPASSWORD pour pg_dump et psql
    env = os.environ.copy()
    env['PGPASSWORD'] = pg_password
    
    try:
        for table in tables:
            print(f"[COPY] Table: {table}")
            
            # Créer fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as tmp:
                dump_file = tmp.name
            
            try:
                # Dump de la table (structure + données)
                dump_cmd = [
                    'pg_dump',
                    '-U', pg_user,
                    '-h', 'localhost',
                    '-d', source_dbname,
                    '-t', table,
                    '--clean',
                    '--if-exists',
                    '-f', dump_file
                ]
                
                result = subprocess.run(
                    dump_cmd,
                    env=env,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"  [ERROR] Dump failed: {result.stderr}")
                    continue
                
                # Import dans DWH
                import_cmd = [
                    'psql',
                    '-U', pg_user,
                    '-h', 'localhost',
                    '-d', dwh_dbname,
                    '-f', dump_file
                ]
                
                result = subprocess.run(
                    import_cmd,
                    env=env,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"  [OK] Table {table} copiee avec succes")
                else:
                    # Ignorer les warnings sur DROP CASCADE
                    if 'does not exist' not in result.stderr:
                        print(f"  [WARN] Import warnings: {result.stderr[:100]}")
                    else:
                        print(f"  [OK] Table {table} copiee avec succes")
                
            finally:
                # Nettoyer le fichier temporaire
                if os.path.exists(dump_file):
                    os.remove(dump_file)
        
        print("[SUCCESS] Copie des tables terminee!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
        raise


@task(name="Build Staging Models", retries=2)
def build_staging_models():
    """Construit les modèles staging (vues sources)"""
    result = DbtCoreOperation(
        commands=["dbt run --select staging.*"],
        project_dir=str(DBT_PROJECT_DIR),
        profiles_dir=str(DBT_PROFILES_DIR),
    ).run()
    return result


@task(name="Build Dimension Tables", retries=2)
def build_dimensions():
    """Construit les tables de dimensions"""
    result = DbtCoreOperation(
        commands=["dbt run --select dimensions.*"],
        project_dir=str(DBT_PROJECT_DIR),
        profiles_dir=str(DBT_PROFILES_DIR),
    ).run()
    return result


@task(name="Build Fact Tables", retries=2)
def build_facts():
    """Construit les tables de faits (incremental)"""
    result = DbtCoreOperation(
        commands=["dbt run --select facts.*"],
        project_dir=str(DBT_PROJECT_DIR),
        profiles_dir=str(DBT_PROFILES_DIR),
    ).run()
    return result


@task(name="Build Data Marts", retries=2)
def build_marts():
    """Construit les data marts analytiques"""
    result = DbtCoreOperation(
        commands=["dbt run --select marts.*"],
        project_dir=str(DBT_PROJECT_DIR),
        profiles_dir=str(DBT_PROFILES_DIR),
    ).run()
    return result


@task(name="Run dbt Tests")
def run_tests():
    """Exécute les tests dbt"""
    result = DbtCoreOperation(
        commands=["dbt test"],
        project_dir=str(DBT_PROJECT_DIR),
        profiles_dir=str(DBT_PROFILES_DIR),
    ).run()
    return result


@task(name="Generate Documentation")
def generate_docs():
    """Génère la documentation dbt"""
    DbtCoreOperation(
        commands=["dbt docs generate"],
        project_dir=str(DBT_PROJECT_DIR),
        profiles_dir=str(DBT_PROFILES_DIR),
    ).run()


@flow(
    name="SIGETI DWH - Full Refresh",
    description="Reconstruction complète du Data Warehouse SIGETI",
)
def sigeti_dwh_full_refresh():
    """
    Flow complet de construction du DWH SIGETI
    Ordre: Staging -> Dimensions -> Facts -> Marts
    Note: Les sources et le DWH sont dans la même base (sigeti_node_db)
          - Sources: schema public
          - DWH: schema dwh
    """
    
    print(f"[INFO] Demarrage du Full Refresh - {datetime.now()}")
    
    # Étape 1: Staging
    print("[STEP 1] Construction des modeles Staging...")
    staging_result = build_staging_models()
    
    # Étape 2: Dimensions
    print("[STEP 2] Construction des Dimensions...")
    dim_result = build_dimensions()
    
    # Étape 3: Facts
    print("[STEP 3] Construction des Tables de Faits...")
    facts_result = build_facts()
    
    # Étape 4: Marts
    print("[STEP 4] Construction des Data Marts...")
    marts_result = build_marts()
    
    # Étape 5: Tests
    print("[STEP 5] Execution des Tests...")
    test_result = run_tests()
    
    # Étape 6: Documentation
    print("[STEP 6] Generation de la Documentation...")
    generate_docs()
    
    print(f"[SUCCESS] Full Refresh termine - {datetime.now()}")
    facts_result = build_facts()
    
    # Étape 5: Marts
    print("[STEP 5] Construction des Data Marts...")
    marts_result = build_marts()
    
    # Étape 5: Tests
    print("[STEP 5] Execution des Tests...")
    test_result = run_tests()
    
    # Étape 6: Documentation
    print("[STEP 6] Generation de la Documentation...")
    generate_docs()
    
    print(f"[SUCCESS] Full Refresh termine - {datetime.now()}")
    
    return {
        "staging": staging_result,
        "dimensions": dim_result,
        "facts": facts_result,
        "marts": marts_result,
        "tests": test_result
    }


@flow(
    name="SIGETI DWH - Incremental",
    description="Mise à jour incrémentale du Data Warehouse SIGETI",
)
def sigeti_dwh_incremental():
    """
    Flow incrémental - Met à jour uniquement les faits et marts
    Les dimensions restent inchangées
    """
    
    print(f"🔄 Démarrage du refresh incrémental - {datetime.now()}")
    
    # Mise à jour des facts (incremental)
    print("📈 Mise à jour incrémentale des Faits...")
    facts_result = build_facts()
    
    # Reconstruction des marts
    print("🎯 Reconstruction des Data Marts...")
    marts_result = build_marts()
    
    # Tests
    print("✅ Exécution des Tests...")
    test_result = run_tests()
    
    print(f"✨ Refresh incrémental terminé - {datetime.now()}")
    
    return {
        "facts": facts_result,
        "marts": marts_result,
        "tests": test_result
    }


@flow(name="SIGETI DWH - Rebuild Marts Only")
def sigeti_dwh_rebuild_marts_only():
    """Reconstruit uniquement les data marts (rapide pour dashboard)"""
    
    print(f"🎯 Reconstruction des Data Marts uniquement - {datetime.now()}")
    
    marts_result = build_marts()
    
    print(f"✨ Reconstruction terminée - {datetime.now()}")
    
    return marts_result


if __name__ == "__main__":
    # Exécution locale pour test
    sigeti_dwh_full_refresh()
