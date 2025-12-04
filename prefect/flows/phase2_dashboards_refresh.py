"""
Prefect Workflow pour les nouveaux Data Marts - Phase 2
Gère l'exécution et la validation des 4 nouveaux marts (implantation_suivi, indemnisations, emplois_crees, creances_agees)
avec monitoring, tests de qualité et notifications API
"""

import subprocess
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

from prefect import flow, task, get_run_logger

# Configuration
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

PROJECT_DIR = Path(__file__).parent.parent.parent
DBT_DIR = PROJECT_DIR

# Nouveaux marts Phase 2
PHASE2_MARTS = [
    'mart_implantation_suivi',
    'mart_indemnisations',
    'mart_emplois_crees',
    'mart_creances_agees'
]

PHASE2_FACTS = [
    'fait_implantations',
    'fait_indemnisations',
    'fait_emplois_crees',
    'fait_factures'
]

PHASE2_STAGING = [
    'stg_implantations',
    'stg_indemnisations',
    'stg_emplois_crees'
]


@task(
    name="Vérifier Staging Phase 2",
    description="Exécuter les modèles Staging des nouveaux marts",
    retries=1
)
def run_phase2_staging():
    """Exécuter les modèles de staging pour Phase 2"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    staging_list = ','.join(PHASE2_STAGING)
    cmd = ['dbt', 'run', '--select', staging_list, '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
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
            logger.info("✓ Staging Phase 2 exécuté avec succès")
            return True
        else:
            logger.error(f"Erreur Staging: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return False


@task(
    name="Construire Facts Phase 2",
    description="Exécuter les modèles Facts des nouveaux marts",
    retries=1
)
def run_phase2_facts():
    """Exécuter les modèles de facts pour Phase 2"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    facts_list = ','.join(PHASE2_FACTS)
    cmd = ['dbt', 'run', '--select', facts_list, '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
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
            logger.info("✓ Facts Phase 2 exécutés avec succès")
            return True
        else:
            logger.error(f"Erreur Facts: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return False


@task(
    name="Construire Marts Phase 2",
    description="Exécuter les modèles Marts des nouveaux marts",
    retries=1
)
def run_phase2_marts():
    """Exécuter les modèles de marts pour Phase 2"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    marts_list = ','.join(PHASE2_MARTS)
    cmd = ['dbt', 'run', '--select', marts_list, '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
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
            logger.info("✓ Marts Phase 2 exécutés avec succès")
            logger.info(result.stdout[-300:] if len(result.stdout) > 300 else result.stdout)
            return True
        else:
            logger.error(f"Erreur Marts: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return False


@task(
    name="Valider Qualité des Données Phase 2",
    description="Vérifier la qualité et la cohérence des données",
    retries=1
)
def validate_phase2_data() -> Dict[str, bool]:
    """Valider la qualité des données des nouveaux marts"""
    logger = get_run_logger()
    
    db_host = os.getenv('DWH_DB_HOST', 'localhost')
    db_port = os.getenv('DWH_DB_PORT', '5432')
    db_name = os.getenv('DWH_DB_NAME', 'sigeti_node_db')
    db_user = os.getenv('DWH_DB_USER', 'postgres')
    db_password = os.getenv('DWH_DB_PASSWORD', 'postgres')
    
    validation_results = {}
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=int(db_port),
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=5
        )
        cursor = conn.cursor()
        
        # Validation pour chaque mart
        validation_queries = {
            'mart_implantation_suivi': """
                SELECT 
                    COUNT(*) as row_count,
                    COUNT(CASE WHEN zone_id IS NULL THEN 1 END) as null_zones
                FROM dwh_marts_operationnel.mart_implantation_suivi
            """,
            'mart_indemnisations': """
                SELECT 
                    COUNT(*) as row_count,
                    COUNT(CASE WHEN zone_id IS NULL THEN 1 END) as null_zones
                FROM dwh_marts_financier.mart_indemnisations
            """,
            'mart_emplois_crees': """
                SELECT 
                    COUNT(*) as row_count,
                    COUNT(CASE WHEN zone_id IS NULL THEN 1 END) as null_zones
                FROM dwh_marts_operationnel.mart_emplois_crees
            """,
            'mart_creances_agees': """
                SELECT 
                    COUNT(*) as row_count,
                    COUNT(CASE WHEN tranche_anciennete IS NULL THEN 1 END) as null_values
                FROM dwh_marts_financier.mart_creances_agees
            """
        }
        
        for mart_name, query in validation_queries.items():
            try:
                cursor.execute(query)
                result = cursor.fetchone()
                row_count, null_count = result[0], result[1]
                
                # Validation: pas trop de NULLs, et données présentes (sauf indemnisations qui peut être vide)
                is_valid = null_count < row_count * 0.1 if row_count > 0 else (mart_name == 'mart_indemnisations')
                validation_results[mart_name] = is_valid
                
                logger.info(f"{mart_name}: {row_count} rows, {null_count} NULLs - {'✓ VALID' if is_valid else '⚠ WARNING'}")
            except Exception as e:
                logger.warning(f"Could not validate {mart_name}: {e}")
                validation_results[mart_name] = False
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to validate data: {e}")
        return {mart: False for mart in PHASE2_MARTS}
    
    return validation_results


@task(
    name="Invalider Cache API",
    description="Notifier l'API d'invalider le cache des nouveaux marts",
    retries=1
)
def invalidate_api_cache():
    """Invalider le cache API pour les nouveaux marts"""
    logger = get_run_logger()
    
    api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    
    endpoints = [
        '/api/implantation-suivi/summary',
        '/api/indemnisations/summary',
        '/api/emplois-crees/summary',
        '/api/creances-agees/summary'
    ]
    
    for endpoint in endpoints:
        try:
            # Faire une requête pour déclencher la création du cache
            url = f"{api_base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✓ Cache invalidated for {endpoint}")
            else:
                logger.warning(f"⚠ Issue with {endpoint}: {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not reach {endpoint}: {e}")
    
    return True


@task(
    name="Exécuter Tests Phase 2",
    description="Exécuter les tests de qualité pour les nouveaux marts",
    retries=1
)
def run_phase2_tests():
    """Exécuter les tests DBT pour Phase 2"""
    logger = get_run_logger()
    
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    
    # Sélectionner les tests pour les nouveaux marts
    cmd = ['dbt', 'test', '--select', 'tag:P2', '--project-dir', str(DBT_DIR), '--profiles-dir', str(DBT_DIR)]
    
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
            logger.info("✓ Tests Phase 2 réussis")
            return True
        else:
            logger.warning(f"⚠ Certains tests ont échoué: {result.stderr[:300]}")
            return False
            
    except Exception as e:
        logger.warning(f"Erreur lors des tests: {str(e)}")
        return False


@task(
    name="Enregistrer Métadonnées Refresh",
    description="Enregistrer les métadonnées de rafraîchissement Phase 2",
    retries=1
)
def log_phase2_refresh(success: bool, validation_results: Dict[str, bool]):
    """Enregistrer les métadonnées du refresh Phase 2"""
    logger = get_run_logger()
    
    db_host = os.getenv('DWH_DB_HOST', 'localhost')
    db_port = os.getenv('DWH_DB_PORT', '5432')
    db_name = os.getenv('DWH_DB_NAME', 'sigeti_node_db')
    db_user = os.getenv('DWH_DB_USER', 'postgres')
    db_password = os.getenv('DWH_DB_PASSWORD', 'postgres')
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=int(db_port),
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=5
        )
        cursor = conn.cursor()
        
        # Créer la table de log si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dbt_refresh_log (
                refresh_id SERIAL PRIMARY KEY,
                run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                models_updated INTEGER,
                rows_inserted INTEGER,
                execution_time_seconds NUMERIC,
                notes TEXT
            )
        """)
        
        # Insérer une ligne de log
        valid_marts = sum(1 for v in validation_results.values() if v)
        notes = f"Phase 2 refresh - {valid_marts}/{len(PHASE2_MARTS)} marts validated"
        
        cursor.execute("""
            INSERT INTO dbt_refresh_log (success, models_updated, notes)
            VALUES (%s, %s, %s)
        """, (success, len(PHASE2_MARTS), notes))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✓ Métadonnées enregistrées: {notes}")
        return True
        
    except Exception as e:
        logger.warning(f"Could not log metadata: {e}")
        return False


@flow(
    name="Phase 2 - Refresh Nouveaux Marts",
    description="Workflow complet pour rafraîchir les 4 nouveaux marts (implantation_suivi, indemnisations, emplois_crees, creances_agees)"
)
def phase2_dashboards_refresh_flow():
    """
    Flow principal pour exécuter et valider les nouveaux marts Phase 2
    Orchestration complète: Staging → Facts → Marts → Tests → Validation → Cache Invalidation
    """
    logger = get_run_logger()
    
    logger.info("=" * 80)
    logger.info("DEBUT DU PIPELINE PHASE 2 - NOUVEAUX MARTS")
    logger.info("=" * 80)
    logger.info(f"Marts à traiter: {', '.join(PHASE2_MARTS)}")
    
    # Étape 1: Exécuter Staging
    logger.info("\n[1/6] Exécution du Staging...")
    staging_ok = run_phase2_staging()
    if not staging_ok:
        logger.error("Staging échoué - arrêt du pipeline")
        log_phase2_refresh(False, {mart: False for mart in PHASE2_MARTS})
        return False
    
    # Étape 2: Exécuter Facts
    logger.info("\n[2/6] Construction des Facts...")
    facts_ok = run_phase2_facts()
    if not facts_ok:
        logger.error("Facts échoués - arrêt du pipeline")
        log_phase2_refresh(False, {mart: False for mart in PHASE2_MARTS})
        return False
    
    # Étape 3: Exécuter Marts
    logger.info("\n[3/6] Construction des Marts...")
    marts_ok = run_phase2_marts()
    if not marts_ok:
        logger.error("Marts échoués - arrêt du pipeline")
        log_phase2_refresh(False, {mart: False for mart in PHASE2_MARTS})
        return False
    
    # Étape 4: Tests de qualité
    logger.info("\n[4/6] Exécution des Tests de qualité...")
    tests_ok = run_phase2_tests()
    if not tests_ok:
        logger.warning("⚠ Certains tests ont échoué, mais on continue...")
    
    # Étape 5: Validation des données
    logger.info("\n[5/6] Validation des données...")
    validation_results = validate_phase2_data()
    all_valid = all(validation_results.values())
    
    if all_valid:
        logger.info("✓ Toutes les validations réussies")
    else:
        failed_marts = [mart for mart, valid in validation_results.items() if not valid]
        logger.warning(f"⚠ Validation échouée pour: {', '.join(failed_marts)}")
    
    # Étape 6: Invalider le cache API
    logger.info("\n[6/6] Invalidation du cache API...")
    invalidate_api_cache()
    
    # Enregistrement final
    success = staging_ok and facts_ok and marts_ok and all_valid
    log_phase2_refresh(success, validation_results)
    
    logger.info("=" * 80)
    logger.info(f"PIPELINE PHASE 2 COMPLETED - Status: {'✓ SUCCESS' if success else '⚠ PARTIAL'}")
    logger.info("=" * 80)
    
    return success


if __name__ == "__main__":
    # Exécution locale pour test
    result = phase2_dashboards_refresh_flow()
    print(f"\nRésultat: {'SUCCÈS' if result else 'ÉCHEC'}")
