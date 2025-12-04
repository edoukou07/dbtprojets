"""
Déploiement Prefect - Planification du pipeline DBT SIGETI
Exécution toutes les 10 minutes + Refresh Phase 2 séparé
"""

from datetime import timedelta

# Importer les flows depuis le dossier flows
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flows.dbt_pipeline import dbt_pipeline_flow
from flows.phase2_dashboards_refresh import phase2_dashboards_refresh_flow


def deploy_dbt_pipeline():
    """Créer et déployer le workflow DBT avec serve()"""
    
    print("=" * 80)
    print("DEPLOYMENT DBT PIPELINE + PHASE 2 MARTS")
    print("=" * 80)
    print(f"Flow 1 - dbt-pipeline-10min")
    print(f"  Intervalle: Toutes les 10 minutes")
    print(f"  Description: Pipeline DBT complet")
    print(f"\nFlow 2 - phase2-refresh-2h30")
    print(f"  Intervalle: Toutes les 2 heures 30 minutes")
    print(f"  Description: Refresh des 4 nouveaux marts")
    print(f"\nStatus: Démarrage du serveur de flows...")
    print("=" * 80)
    print(f"\nDashboard Prefect: http://127.0.0.1:4200")
    print("=" * 80)
    
    # Déployer le pipeline DBT principal
    dbt_pipeline_flow.serve(
        name="dbt-pipeline-10min",
        interval=600,  # 600 secondes = 10 minutes
        tags=["dbt", "sigeti", "production", "full-pipeline"],
        description="Exécution toutes les 10 minutes du pipeline DBT SIGETI"
    )


def deploy_phase2_dashboards():
    """Créer et déployer le workflow Phase 2 avec serve()"""
    
    print("=" * 80)
    print("DEPLOYMENT PHASE 2 DASHBOARDS")
    print("=" * 80)
    print(f"Nom: phase2-refresh-2h30")
    print(f"Intervalle: Toutes les 2 heures 30 minutes")
    print(f"Marts: implantation_suivi, indemnisations, emplois_crees, creances_agees")
    print(f"Status: Démarrage du serveur de flow...")
    print("=" * 80)
    print(f"\nDashboard Prefect: http://127.0.0.1:4200")
    print("=" * 80)
    
    # Utiliser serve() pour le workflow Phase 2
    phase2_dashboards_refresh_flow.serve(
        name="phase2-refresh-2h30",
        interval=9000,  # 9000 secondes = 2 heures 30 minutes
        tags=["phase2", "dashboards", "nouveaux-marts", "production"],
        description="Refresh des 4 nouveaux marts Phase 2"
    )


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 80)
    print("PREFECT DEPLOYMENT MANAGER - SIGETI")
    print("=" * 80)
    print("\nOptions:")
    print("  python deploy_dbt_pipeline.py main      -> Deploy DBT pipeline (10 min)")
    print("  python deploy_dbt_pipeline.py phase2    -> Deploy Phase 2 dashboards (2h30)")
    print("  python deploy_dbt_pipeline.py both      -> Deploy both pipelines")
    print("=" * 80 + "\n")
    
    if len(sys.argv) < 2 or sys.argv[1] == "main":
        deploy_dbt_pipeline()
    elif sys.argv[1] == "phase2":
        deploy_phase2_dashboards()
    elif sys.argv[1] == "both":
        print("Déploiement simultané des deux pipelines...\n")
        deploy_dbt_pipeline()
    else:
        print(f"Argument inconnu: {sys.argv[1]}")
        print("Utilisation: python deploy_dbt_pipeline.py [main|phase2|both]")
