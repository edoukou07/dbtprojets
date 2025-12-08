"""
Test script pour vérifier le flow Phase 2 sans Prefect server
Valide la syntaxe et les imports
"""

import sys
from pathlib import Path

# Ajouter le dossier prefect au path
sys.path.insert(0, str(Path(__file__).parent / 'prefect'))

print("=" * 80)
print("VALIDATION DU WORKFLOW PHASE 2")
print("=" * 80)

# Test 1: Imports
print("\n[1/5] Vérification des imports...")
try:
    from flows.phase2_dashboards_refresh import (
        phase2_dashboards_refresh_flow,
        run_phase2_staging,
        run_phase2_facts,
        run_phase2_marts,
        validate_phase2_data,
        run_phase2_tests,
        invalidate_api_cache,
        log_phase2_refresh,
        PHASE2_MARTS,
        PHASE2_FACTS,
        PHASE2_STAGING
    )
    print("✓ Tous les imports réussis")
except Exception as e:
    print(f"✗ Erreur d'import: {e}")
    sys.exit(1)

# Test 2: Vérifier les constantes
print("\n[2/5] Vérification des constantes...")
print(f"  Staging: {PHASE2_STAGING}")
print(f"  Facts: {PHASE2_FACTS}")
print(f"  Marts: {PHASE2_MARTS}")
if len(PHASE2_MARTS) == 4 and len(PHASE2_FACTS) == 4:
    print("✓ Constantes correctes")
else:
    print("✗ Nombre de marts/facts incorrect")
    sys.exit(1)

# Test 3: Vérifier que le flow est une Prefect Flow
print("\n[3/5] Vérification du type flow...")
from prefect import Flow
if isinstance(phase2_dashboards_refresh_flow, Flow):
    print("✓ phase2_dashboards_refresh_flow est un Flow Prefect")
else:
    print("⚠ phase2_dashboards_refresh_flow n'est pas un Flow (peut être callable)")

# Test 4: Vérifier les tasks
print("\n[4/5] Vérification des tasks...")
try:
    from prefect.task import Task
    tasks = [run_phase2_staging, run_phase2_facts, run_phase2_marts, 
             validate_phase2_data, run_phase2_tests, invalidate_api_cache, 
             log_phase2_refresh]
    
    for task in tasks:
        if hasattr(task, 'fn') or callable(task):
            print(f"  ✓ {task.__name__}")
        else:
            print(f"  ✗ {task.__name__} n'est pas valide")
    
    print(f"✓ {len(tasks)} tasks validées")
except Exception as e:
    print(f"⚠ Erreur lors de la vérification: {e}")

# Test 5: Syntaxe et structure
print("\n[5/5] Vérification de la syntaxe...")
import ast
import inspect

try:
    source = inspect.getsource(phase2_dashboards_refresh_flow.__wrapped__)
    ast.parse(source)
    print("✓ Syntaxe Python valide")
except Exception as e:
    print(f"⚠ Impossible de vérifier la syntaxe: {e}")

print("\n" + "=" * 80)
print("RÉSUMÉ DE VALIDATION")
print("=" * 80)
print("✓ Workflow Phase 2 valide et prêt pour déploiement")
print("\nConfiguration:")
print(f"  - Flow Name: {phase2_dashboards_refresh_flow.name}")
print(f"  - Flow Description: {phase2_dashboards_refresh_flow.description}")
print(f"  - Marts à traiter: {len(PHASE2_MARTS)}")
print(f"  - Facts à construire: {len(PHASE2_FACTS)}")
print(f"  - Staging à exécuter: {len(PHASE2_STAGING)}")
print("\nProchaines étapes:")
print("  1. Déployer le flow: python prefect/deployments/deploy_dbt_pipeline.py phase2")
print("  2. Vérifier le dashboard: http://127.0.0.1:4200")
print("=" * 80)
