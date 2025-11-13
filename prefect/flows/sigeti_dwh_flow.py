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
import subprocess

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


@task(name="Run dbt Tests", retries=1)
def run_tests():
    """Exécute les tests dbt avec gestion de l'encodage UTF-8"""
    
    import subprocess
    
    print(f"[INFO] Execution des tests dbt...")
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    try:
        cmd = [
            'dbt',
            'test',
            '--profiles-dir', str(DBT_PROFILES_DIR),
            '--project-dir', str(DBT_PROJECT_DIR)
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'  # Remplace les caractères invalides au lieu de crasher
        )
        
        # Afficher la sortie
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"  {line}")
        
        if result.returncode == 0:
            print("[SUCCESS] Tous les tests ont reussi!")
            return True
        else:
            # Afficher les erreurs mais ne pas bloquer le pipeline
            print("[WARN] Certains tests ont echoue:")
            if result.stderr:
                for line in result.stderr.split('\n')[:20]:  # Limiter à 20 lignes
                    if line.strip():
                        print(f"  {line}")
            # Retourner True pour ne pas bloquer le pipeline
            print("[INFO] Pipeline continue malgre les echecs de tests")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'execution des tests: {e}")
        # Ne pas bloquer le pipeline
        return False


@task(name="Create New Partitions", retries=1)
def create_new_partitions():
    """Crée automatiquement les nouvelles partitions si nécessaire (année N+1, N+2)"""
    print("\n" + "="*70)
    print("[MAINTENANCE] Creation automatique des nouvelles partitions...")
    print("="*70)
    
    dwh_dbname = os.getenv('DWH_DB_NAME', 'sigeti_node_db')
    dwh_password = os.getenv('DBT_PASSWORD')
    
    # Années à créer (année courante + 2 ans futurs)
    current_year = datetime.now().year
    years_to_check = [current_year, current_year + 1, current_year + 2]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = dwh_password
    env['PGCLIENTENCODING'] = 'UTF8'
    
    created_count = 0
    
    for year in years_to_check:
        # Vérifier si la partition existe
        check_cmd = [
            'psql',
            '-h', 'localhost',
            '-U', 'postgres',
            '-d', dwh_dbname,
            '-t',
            '-c', f"SELECT COUNT(*) FROM pg_tables WHERE schemaname='dwh_facts' AND tablename='fait_attributions_{year}';"
        ]
        
        try:
            result = subprocess.run(
                check_cmd,
                env=env,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            count = result.stdout.strip()
            
            if count == '0':
                # Créer la partition
                print(f"  [INFO] Creation de la partition pour l'annee {year}...")
                
                create_cmd = [
                    'psql',
                    '-h', 'localhost',
                    '-U', 'postgres',
                    '-d', dwh_dbname,
                    '-c', f"""
                    CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_{year} 
                    PARTITION OF dwh_facts.fait_attributions
                    FOR VALUES FROM ({year}0101) TO ({year+1}0101);
                    
                    CREATE INDEX IF NOT EXISTS idx_attr_{year}_entreprise ON dwh_facts.fait_attributions_{year}(entreprise_key);
                    CREATE INDEX IF NOT EXISTS idx_attr_{year}_lot ON dwh_facts.fait_attributions_{year}(lot_key);
                    CREATE INDEX IF NOT EXISTS idx_attr_{year}_date ON dwh_facts.fait_attributions_{year}(date_demandee_key);
                    """
                ]
                
                create_result = subprocess.run(
                    create_cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                if create_result.returncode == 0:
                    print(f"  [OK] Partition {year} creee avec succes")
                    created_count += 1
                else:
                    print(f"  [WARN] Erreur creation partition {year}: {create_result.stderr[:100]}")
            else:
                print(f"  [OK] Partition {year} existe deja")
                
        except Exception as e:
            print(f"  [ERROR] Erreur verification partition {year}: {str(e)}")
    
    print(f"\n[SUCCESS] {created_count} nouvelle(s) partition(s) creee(s)")
    return created_count


@task(name="Weekly Vacuum and Analyze", retries=1)
def vacuum_and_analyze():
    """Exécute VACUUM et ANALYZE sur les tables principales (maintenance légère)"""
    print("\n" + "="*70)
    print("[MAINTENANCE] VACUUM et ANALYZE hebdomadaire...")
    print("="*70)
    
    dwh_dbname = os.getenv('DWH_DB_NAME', 'sigeti_node_db')
    dwh_password = os.getenv('DBT_PASSWORD')
    
    # Tables principales à maintenir
    tables = [
        "dwh_facts.fait_attributions",
        "dwh_facts.fait_factures",
        "dwh_facts.fait_collectes",
        "dwh_facts.fait_paiements",
        "dwh_dim.dim_entreprises",
        "dwh_marts.mart_kpi_operationnels",
        "dwh_marts.mart_portefeuille_clients",
        "dwh_marts.mart_occupation_zones",
        "dwh_marts.mart_performance_financiere"
    ]
    
    env = os.environ.copy()
    env['PGPASSWORD'] = dwh_password
    env['PGCLIENTENCODING'] = 'UTF8'
    
    for table in tables:
        print(f"  [INFO] VACUUM ANALYZE {table}...")
        
        cmd = [
            'psql',
            '-h', 'localhost',
            '-U', 'postgres',
            '-d', dwh_dbname,
            '-c', f"VACUUM ANALYZE {table};"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5 minutes max par table
            )
            
            if result.returncode == 0:
                print(f"  [OK] {table} termine")
            else:
                print(f"  [WARN] {table} echoue: {result.stderr[:100]}")
                
        except subprocess.TimeoutExpired:
            print(f"  [WARN] {table} timeout (> 5 min)")
        except Exception as e:
            print(f"  [ERROR] {table} erreur: {str(e)}")
    
    print("[SUCCESS] Maintenance hebdomadaire terminee")
    return True


@task(name="Create Database Indexes", retries=1)
def create_indexes():
    """Crée les index PostgreSQL pour optimiser les performances"""
    
    dwh_dbname = os.getenv('DWH_DB_NAME', 'sigeti_node_db')
    pg_user = os.getenv('DWH_DB_USER', 'postgres')
    pg_password = os.getenv('DBT_PASSWORD')
    
    index_file = DBT_PROJECT_DIR / 'scripts' / 'create_indexes.sql'
    
    if not index_file.exists():
        print(f"[WARN] Fichier d'index introuvable: {index_file}")
        return False
    
    print(f"[INFO] Creation des index PostgreSQL...")
    print(f"[INFO] Base de donnees: {dwh_dbname}")
    print(f"[INFO] Fichier SQL: {index_file}")
    
    env = os.environ.copy()
    env['PGPASSWORD'] = pg_password
    env['PGCLIENTENCODING'] = 'UTF8'
    
    try:
        cmd = [
            'psql',
            '-U', pg_user,
            '-h', 'localhost',
            '-d', dwh_dbname,
            '-f', str(index_file),
            '-v', 'ON_ERROR_STOP=0'  # Continue en cas d'erreur (index déjà existant)
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'  # Ignore les erreurs d'encodage
        )
        
        if result.returncode == 0:
            print("[SUCCESS] Index crees avec succes!")
            if result.stdout:
                # Afficher uniquement les lignes importantes
                for line in result.stdout.split('\n'):
                    if 'CREATE INDEX' in line or 'ANALYZE' in line or '✅' in line:
                        print(f"  {line}")
            return True
        else:
            # Les erreurs "relation already exists" sont normales
            if 'already exists' in result.stderr:
                print("[OK] Index deja existants (normal)")
                return True
            else:
                print(f"[WARN] Certains index n'ont pas pu etre crees:")
                print(result.stderr[:500])
                return True  # Ne pas bloquer le pipeline
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la creation des index: {e}")
        # Ne pas bloquer le pipeline pour une erreur d'indexation
        return False


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
    
    # Vérifier si c'est lundi (jour 0)
    is_monday = datetime.now().weekday() == 0
    
    if is_monday:
        print("\n" + "="*70)
        print("📅 LUNDI - Maintenance hebdomadaire activée")
        print("="*70)
        print("[MAINTENANCE] 1. Creation des nouvelles partitions")
        print("[MAINTENANCE] 2. VACUUM ANALYZE des tables principales")
        print("="*70 + "\n")
    
    # Étape 1: Staging
    print("[STEP 1] Construction des modeles Staging...")
    staging_result = build_staging_models()
    
    # Étape 2: Dimensions
    print("[STEP 2] Construction des Dimensions...")
    dim_result = build_dimensions()
    
    # Étape 3: Indexation
    print("[STEP 3] Creation des Index PostgreSQL...")
    index_result = create_indexes()
    
    # Étape 4: Facts
    print("[STEP 4] Construction des Tables de Faits...")
    facts_result = build_facts()
    
    # Étape 5: Marts
    print("[STEP 5] Construction des Data Marts...")
    marts_result = build_marts()
    
    # Étape 6: Tests
    print("[STEP 6] Execution des Tests...")
    test_result = run_tests()
    
    # Étape 7: Documentation
    print("[STEP 7] Generation de la Documentation...")
    generate_docs()
    
    # MAINTENANCE HEBDOMADAIRE (le lundi uniquement)
    if is_monday:
        print("\n" + "="*70)
        print("🔧 MAINTENANCE HEBDOMADAIRE")
        print("="*70)
        
        # Créer les nouvelles partitions
        create_new_partitions()
        
        # VACUUM et ANALYZE
        vacuum_and_analyze()
        
        print("="*70)
        print("✅ Maintenance hebdomadaire terminée")
        print("="*70 + "\n")
    
    print(f"[SUCCESS] Full Refresh termine - {datetime.now()}")
    
    return {
        "staging": staging_result,
        "dimensions": dim_result,
        "indexes": index_result,
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
