# Script pour déployer le pipeline sur Prefect Server avec planification
# Ce script crée un déploiement avec exécution quotidienne à 2h du matin
# Compatible avec Prefect 3.x

import sys
import os

# Ajouter le répertoire parent au path pour importer le flow
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(parent_dir, 'flows'))

# Importer le flow
from sigeti_dwh_flow import sigeti_dwh_full_refresh

if __name__ == "__main__":
    print("📅 Déploiement du pipeline SIGETI DWH avec planification...")
    print("⏰ Horaire: Toutes les 10 minutes")
    print()
    
    # Utiliser la nouvelle API flow.serve() de Prefect 3.x
    # Cette commande démarre un serveur qui exécute le flow selon le cron
    sigeti_dwh_full_refresh.serve(
        name="sigeti-dwh-every-10min",
        cron="*/10 * * * *",  # Toutes les 10 minutes
        tags=["production", "dwh", "frequent"],
        description="Pipeline de rafraîchissement du Data Warehouse SIGETI - Toutes les 10 minutes",
        pause_on_shutdown=False,
        print_starting_message=True
    )
    
    print("\n✅ Déploiement actif!")
    print("📌 Le serveur Prefect est en cours d'exécution...")
    print("🌐 Interface web: http://127.0.0.1:4200")
    print("⚠️  Gardez cette fenêtre ouverte pour maintenir le déploiement actif")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
