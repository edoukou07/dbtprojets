"""
Incremental Refresh Scheduling with Prefect
Manages scheduled incremental loads for dBT models with state tracking
"""

import subprocess
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

from prefect import flow, task, get_run_logger
from prefect.schedules import IntervalSchedule
from prefect.deployments import Deployment

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

PROJECT_DIR = Path(__file__).parent.parent.parent
DBT_DIR = PROJECT_DIR


@task(
    name="Check Incremental State",
    description="Check last incremental load timestamp",
    retries=2,
    retry_delay_seconds=5
)
def check_incremental_state() -> Dict[str, datetime]:
    """Check the last incremental load state for each incremental model"""
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
        
        # Query to get max timestamps from each incremental model
        incremental_models = {
            'fait_attributions': 'dwh_facts.fait_attributions',
            'fait_collectes': 'dwh_facts.fait_collectes',
            'fait_conventions': 'dwh_facts.fait_conventions',
            'fait_factures': 'dwh_facts.fait_factures',
            'fait_indemnisations': 'dwh_facts.fait_indemnisations',
            'fait_paiements': 'dwh_facts.fait_paiements'
        }
        
        state = {}
        for model_name, table_path in incremental_models.items():
            try:
                cursor.execute(f"""
                    SELECT MAX(dbt_processed_at) as last_run
                    FROM {table_path}
                """)
                result = cursor.fetchone()
                last_run = result[0] if result[0] else datetime(2020, 1, 1)
                state[model_name] = last_run
                logger.info(f"{model_name}: Last run at {last_run}")
            except Exception as e:
                logger.warning(f"Could not query {model_name}: {e}")
                state[model_name] = datetime(2020, 1, 1)
        
        cursor.close()
        conn.close()
        
        logger.info(f"Incremental state: {state}")
        return state
        
    except Exception as e:
        logger.error(f"Failed to check incremental state: {e}")
        raise


@task(
    name="Run Incremental Models",
    description="Execute dBT incremental models",
    retries=1,
    retry_delay_seconds=10
)
def run_incremental_models(state: Dict[str, datetime]) -> bool:
    """Run dBT incremental models with proper state management"""
    logger = get_run_logger()
    
    try:
        os.chdir(str(DBT_DIR))
        
        # Determine incremental_since timestamp (last successful run or 7 days ago)
        latest_timestamp = max(state.values()) if state else datetime.now() - timedelta(days=7)
        incremental_since = latest_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"Running incremental models since: {incremental_since}")
        
        # Run dBT incremental models only
        cmd = [
            'dbt', 'run',
            '--select', 'fait_attributions,fait_collectes,fait_conventions,fait_factures,fait_indemnisations,fait_paiements',
            '--threads', '8',
            '--var', f'incremental_since={incremental_since}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            logger.error(f"dBT run failed:\n{result.stderr}")
            raise Exception(f"dBT run failed with return code {result.returncode}")
        
        logger.info("Incremental models executed successfully")
        logger.info(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("dBT run timed out after 10 minutes")
        raise
    except Exception as e:
        logger.error(f"Error running incremental models: {e}")
        raise


@task(
    name="Run Data Quality Tests",
    description="Execute dBT data quality tests",
    retries=1,
    retry_delay_seconds=10
)
def run_quality_tests() -> bool:
    """Run data quality tests on incremental models"""
    logger = get_run_logger()
    
    try:
        os.chdir(str(DBT_DIR))
        
        # Run tests on incremental models
        cmd = [
            'dbt', 'test',
            '--select', 'fait_attributions,fait_collectes,fait_conventions,fait_factures,fait_indemnisations,fait_paiements,integration',
            '--threads', '8'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            logger.warning(f"Some tests failed:\n{result.stderr}")
            # Don't fail the flow, but log the issues
        
        logger.info("Quality tests completed")
        logger.info(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error("Tests timed out after 5 minutes")
        raise
    except Exception as e:
        logger.error(f"Error running quality tests: {e}")
        raise


@task(
    name="Update Refresh Metadata",
    description="Record incremental refresh execution metadata",
    retries=2,
    retry_delay_seconds=5
)
def update_refresh_metadata(success: bool) -> bool:
    """Update metadata tracking incremental refresh execution"""
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
        
        # Create metadata table if not exists
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
        
        # Insert metadata record
        cursor.execute("""
            INSERT INTO dbt_refresh_log (success, models_updated, notes)
            VALUES (%s, %s, %s)
        """, (success, 6, 'Incremental refresh via Prefect'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Metadata updated. Success: {success}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update metadata: {e}")
        return False


@flow(
    name="Incremental Refresh Pipeline",
    description="Scheduled incremental refresh of fact tables"
)
def incremental_refresh_flow():
    """Main flow for incremental refresh with proper state management"""
    logger = get_run_logger()
    
    logger.info("Starting incremental refresh flow")
    
    # Step 1: Check current state
    state = check_incremental_state()
    
    # Step 2: Run incremental models
    run_incremental_models(state)
    
    # Step 3: Run quality tests
    test_success = run_quality_tests()
    
    # Step 4: Update metadata
    update_refresh_metadata(test_success)
    
    logger.info("Incremental refresh flow completed successfully")


@flow(
    name="Full Refresh Pipeline",
    description="Full refresh of all dBT models (weekly)"
)
def full_refresh_flow():
    """Full refresh of all models with comprehensive validation"""
    logger = get_run_logger()
    
    logger.info("Starting full refresh flow")
    
    try:
        os.chdir(str(DBT_DIR))
        
        # Full dBT run
        logger.info("Running full dBT pipeline")
        cmd = ['dbt', 'run', '--threads', '8']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        if result.returncode != 0:
            logger.error(f"Full dBT run failed:\n{result.stderr}")
            raise Exception("Full dBT run failed")
        
        logger.info("Full dBT run completed")
        
        # Run all tests
        logger.info("Running all quality tests")
        cmd = ['dbt', 'test', '--threads', '8']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            logger.warning(f"Some tests failed:\n{result.stderr}")
        
        logger.info("Full refresh completed successfully")
        update_refresh_metadata(True)
        
    except Exception as e:
        logger.error(f"Full refresh failed: {e}")
        update_refresh_metadata(False)
        raise


# Schedule Definitions
daily_schedule = IntervalSchedule(
    interval=timedelta(days=1),
    start_date=datetime.now() + timedelta(hours=1)
)

weekly_schedule = IntervalSchedule(
    interval=timedelta(weeks=1),
    start_date=datetime.now() + timedelta(days=1)
)


if __name__ == "__main__":
    # Test flows locally
    incremental_refresh_flow()
