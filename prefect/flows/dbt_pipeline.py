"""
Workflow Prefect pour exécuter le pipeline DBT SIGETI
"""

import subprocess
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import psycopg2

from prefect import flow, task, get_run_logger

# Charger les variables d'environnement depuis .env
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Configuration - Chemin vers le projet DBT
PROJECT_DIR = Path(__file__).parent.parent.parent
DBT_DIR = PROJECT_DIR


@task(
    name="Vérifier la connexion",
    description="Tester la connexion PostgreSQL",
    retries=2,
    retry_delay_seconds=5
)
def verify_database():
    """Vérifier que PostgreSQL est accessible"""
    logger = get_run_logger()
    
    # Récupérer les variables d'environnement
    db_host = os.getenv('DWH_DB_HOST', 'localhost')
    db_port = os.getenv('DWH_DB_PORT', '5432')
    db_name = os.getenv('DWH_DB_NAME', 'sigeti_node_db')
    db_user = os.getenv('DWH_DB_USER', 'postgres')
    db_password = os.getenv('DWH_DB_PASSWORD', 'postgres')
    
    try:
        # Utiliser psycopg2 directement au lieu de psql
        conn = psycopg2.connect(
            host=db_host,
            port=int(db_port),
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        logger.info(f"✓ Connexion PostgreSQL OK - {version[:50]}")
        return True
            
    except Exception as e:
        logger.error(f"Erreur connexion: {str(e)}")
        return False


@task(
    name="DBT Debug",
    description="Valider la configuration DBT",
    retries=1
)
def dbt_debug():
    """Exécuter dbt debug pour valider la configuration"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    env['PYTHONIOENCODING'] = 'utf-8'
    
    cmd = ['dbt', 'debug', '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(DBT_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info("✓ DBT Debug OK")
            return True
        else:
            logger.error(f"DBT Debug échoué: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return False


@task(
    name="DBT Run Staging",
    description="Exécuter les modèles Staging",
    retries=1
)
def dbt_run_staging():
    """Exécuter les modèles de staging"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    cmd = ['dbt', 'run', '--select', 'staging.*', '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(DBT_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("✓ Staging exécuté avec succès")
            return True
        else:
            logger.error(f"Erreur Staging: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return False


@task(
    name="DBT Run Dimensions",
    description="Exécuter les modèles Dimensions",
    retries=1
)
def dbt_run_dimensions():
    """Exécuter les modèles de dimensions"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    cmd = ['dbt', 'run', '--select', 'dimensions.*', '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(DBT_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("✓ Dimensions exécutées avec succès")
            return True
        else:
            logger.error(f"Erreur Dimensions: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return False


@task(
    name="DBT Run Facts",
    description="Exécuter les modèles Facts",
    retries=1
)
def dbt_run_facts():
    """Exécuter les modèles de facts"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    cmd = ['dbt', 'run', '--select', 'facts.*', '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(DBT_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("✓ Facts exécutés avec succès")
            return True
        else:
            logger.error(f"Erreur Facts: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return False


@task(
    name="DBT Run Marts",
    description="Exécuter les modèles Marts",
    retries=1
)
def dbt_run_marts():
    """Exécuter les modèles de marts"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    cmd = ['dbt', 'run', '--select', 'marts.*', '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(DBT_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("✓ Marts exécutés avec succès")
            return True
        else:
            logger.error(f"Erreur Marts: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return False


@task(
    name="DBT Tests",
    description="Exécuter les tests de qualité",
    retries=1
)
def dbt_test():
    """Exécuter les tests DBT"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    cmd = ['dbt', 'test', '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(DBT_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("✓ Tests réussis")
            return True
        else:
            logger.error(f"Erreur Tests: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return False


@flow(
    name="Pipeline DBT SIGETI",
    description="Pipeline complet DBT avec staging, dimensions, facts, marts et tests",
    validate_parameters=False
)
def dbt_pipeline_flow():
    """
    Flow principal pour exécuter le pipeline DBT complet
    """
    logger = get_run_logger()
    logger.info("=" * 80)
    logger.info("DEBUT DU PIPELINE DBT SIGETI")
    logger.info("=" * 80)
    
    # Vérification initiale
    db_ok = verify_database()
    if not db_ok:
        logger.error("Impossible de se connecter à PostgreSQL")
        return False
    
    # Debug DBT
    debug_ok = dbt_debug()
    if not debug_ok:
        logger.error("DBT Debug échoué")
        return False
    
    # Exécution séquentielle
    staging_ok = dbt_run_staging()
    if not staging_ok:
        logger.error("Staging échoué - arrêt du pipeline")
        return False
    
    dims_ok = dbt_run_dimensions()
    if not dims_ok:
        logger.error("Dimensions échouées - arrêt du pipeline")
        return False
    
    facts_ok = dbt_run_facts()
    if not facts_ok:
        logger.error("Facts échoués - arrêt du pipeline")
        return False
    
    marts_ok = dbt_run_marts()
    if not marts_ok:
        logger.error("Marts échoués - arrêt du pipeline")
        return False
    
    # Tests de qualité
    tests_ok = dbt_test()
    if not tests_ok:
        logger.warning("Certains tests ont échoué, mais le pipeline continue")
    
    logger.info("=" * 80)
    logger.info("PIPELINE DBT SIGETI COMPLETED")
    logger.info("=" * 80)
    
    return True


if __name__ == "__main__":
    # Exécution locale pour test
    result = dbt_pipeline_flow()
    print(f"\nRésultat: {'SUCCÈS' if result else 'ÉCHEC'}")
