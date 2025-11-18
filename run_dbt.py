
"""
Runner DBT avec gestion correcte de l'encodage PostgreSQL
Inspire du workflow Prefect sigeti_dwh_setup.py
"""
import subprocess
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
PROJECT_DIR = Path(__file__).parent
load_dotenv(PROJECT_DIR / '.env')
def run_dbt_command(dbt_command):
    """Executer une commande DBT avec gestion de l'encodage"""
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    env['PYTHONIOENCODING'] = 'utf-8'
    cmd = ['dbt'] + dbt_command.split()
    print(f"▶ Execution: {' '.join(cmd)}")
    print(f"  PGCLIENTENCODING: {env['PGCLIENTENCODING']}")
    print()
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_DIR),
            env=env,
            capture_output=False,  
            text=True,
            encoding='utf-8',
            errors='replace'  
        )
        return result.returncode
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python run_dbt.py <dbt_command>")
        print("Example: python run_dbt.py 'run -s mart_performance_financiere'")
        sys.exit(1)
    dbt_command = ' '.join(sys.argv[1:])
    exit_code = run_dbt_command(dbt_command)
    sys.exit(exit_code)
if __name__ == "__main__":
    main()
