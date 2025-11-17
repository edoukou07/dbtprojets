"""
Déploiement Prefect - Planification du pipeline DBT SIGETI
Exécution toutes les 10 minutes
"""

from datetime import timedelta

# Importer le flow depuis le dossier flows
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flows.dbt_pipeline import dbt_pipeline_flow


def deploy_dbt_pipeline():
    """Créer et déployer le workflow DBT avec serve()"""
    
    print("=" * 80)
    print("DEPLOYMENT DBT PIPELINE")
    print("=" * 80)
    print(f"Nom: dbt-pipeline-10min")
    print(f"Intervalle: Toutes les 10 minutes")
    print(f"Status: Démarrage du serveur de flow...")
    print("=" * 80)
    print(f"\nDashboard Prefect: http://127.0.0.1:4200")
    print("=" * 80)
    
    # Utiliser serve() pour Prefect 3.x avec intervalle en secondes
    dbt_pipeline_flow.serve(
        name="dbt-pipeline-10min",
        interval=600,  # 600 secondes = 10 minutes
        tags=["dbt", "sigeti", "production"],
        description="Exécution toutes les 10 minutes du pipeline DBT SIGETI"
    )


if __name__ == "__main__":
    deploy_dbt_pipeline()
