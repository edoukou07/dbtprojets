#!/usr/bin/env python
"""
Script pour exécuter automatiquement l'envoi des rapports programmés
Exécutez ce script en arrière-plan pour qu'il vérifie et envoie les rapports toutes les minutes
"""
import os
import sys
import time
import subprocess
from pathlib import Path

# Changer vers le répertoire du backend
backend_dir = Path(__file__).parent
os.chdir(backend_dir)

print(f"📧 Scheduler de rapports démarré dans {backend_dir}")
print("Vérification des rapports programmés toutes les minutes...")
print("Appuyez sur Ctrl+C pour arrêter\n")

try:
    while True:
        try:
            # Exécuter le management command
            result = subprocess.run(
                [sys.executable, 'manage.py', 'send_scheduled_reports'],
                capture_output=True,
                text=True,
                cwd=backend_dir
            )
            
            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                print(f"Erreur: {result.stderr}", file=sys.stderr)
                
        except Exception as e:
            print(f"Erreur lors de l'exécution: {e}", file=sys.stderr)
        
        # Attendre 1 minute avant la prochaine vérification
        time.sleep(60)
        
except KeyboardInterrupt:
    print("\n\nScheduler arrêté par l'utilisateur")

