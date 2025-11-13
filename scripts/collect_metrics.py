"""
Collecte et stockage des métriques d'exécution dbt
Permet le suivi historique des performances
"""

import json
from datetime import datetime
from pathlib import Path
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_metrics_table():
    """Crée une table pour stocker les métriques d'exécution"""
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database=os.getenv('DWH_DB_NAME'),
        user=os.getenv('DWH_DB_USER'),
        password=os.getenv('DBT_PASSWORD')
    )
    
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dwh.dbt_run_metrics (
            run_id SERIAL PRIMARY KEY,
            run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_models INT,
            successful_models INT,
            failed_models INT,
            total_tests INT,
            passed_tests INT,
            failed_tests INT,
            total_duration_seconds DECIMAL(10,2),
            staging_duration_seconds DECIMAL(10,2),
            dimensions_duration_seconds DECIMAL(10,2),
            facts_duration_seconds DECIMAL(10,2),
            marts_duration_seconds DECIMAL(10,2),
            run_status VARCHAR(20),
            error_message TEXT
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Table dbt_run_metrics créée")

def parse_run_results():
    """Parse les résultats d'exécution dbt"""
    run_results_path = Path("target/run_results.json")
    
    if not run_results_path.exists():
        print("⚠️  Fichier run_results.json non trouvé")
        return None
    
    with open(run_results_path, 'r') as f:
        data = json.load(f)
    
    # Extraire les métriques
    results = data.get('results', [])
    
    total_models = len([r for r in results if r['resource_type'] == 'model'])
    successful_models = len([r for r in results if r['resource_type'] == 'model' and r['status'] == 'success'])
    failed_models = len([r for r in results if r['resource_type'] == 'model' and r['status'] == 'error'])
    
    total_tests = len([r for r in results if r['resource_type'] == 'test'])
    passed_tests = len([r for r in results if r['resource_type'] == 'test' and r['status'] == 'pass'])
    failed_tests = len([r for r in results if r['resource_type'] == 'test' and r['status'] == 'fail'])
    
    # Calculer les durées par couche
    def get_layer_duration(layer_name):
        layer_results = [r for r in results if layer_name in r.get('unique_id', '')]
        return sum(r.get('execution_time', 0) for r in layer_results)
    
    metrics = {
        'total_models': total_models,
        'successful_models': successful_models,
        'failed_models': failed_models,
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'staging_duration': get_layer_duration('staging'),
        'dimensions_duration': get_layer_duration('dimensions'),
        'facts_duration': get_layer_duration('facts'),
        'marts_duration': get_layer_duration('marts'),
        'total_duration': data.get('elapsed_time', 0),
        'run_status': 'success' if failed_models == 0 and failed_tests == 0 else 'failed'
    }
    
    return metrics

def store_metrics(metrics):
    """Stocke les métriques dans PostgreSQL"""
    if not metrics:
        return
    
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database=os.getenv('DWH_DB_NAME'),
        user=os.getenv('DWH_DB_USER'),
        password=os.getenv('DBT_PASSWORD')
    )
    
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO dwh.dbt_run_metrics (
            total_models, successful_models, failed_models,
            total_tests, passed_tests, failed_tests,
            total_duration_seconds,
            staging_duration_seconds,
            dimensions_duration_seconds,
            facts_duration_seconds,
            marts_duration_seconds,
            run_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING run_id;
    """, (
        metrics['total_models'],
        metrics['successful_models'],
        metrics['failed_models'],
        metrics['total_tests'],
        metrics['passed_tests'],
        metrics['failed_tests'],
        metrics['total_duration'],
        metrics['staging_duration'],
        metrics['dimensions_duration'],
        metrics['facts_duration'],
        metrics['marts_duration'],
        metrics['run_status']
    ))
    
    run_id = cursor.fetchone()[0]
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Métriques stockées (run_id: {run_id})")
    return run_id

if __name__ == "__main__":
    print("📊 Collecte des métriques dbt...\n")
    
    # Créer la table si elle n'existe pas
    create_metrics_table()
    
    # Parser et stocker les métriques
    metrics = parse_run_results()
    if metrics:
        print(f"\n📈 Résumé de l'exécution:")
        print(f"   Modèles: {metrics['successful_models']}/{metrics['total_models']} succès")
        print(f"   Tests: {metrics['passed_tests']}/{metrics['total_tests']} passés")
        print(f"   Durée totale: {metrics['total_duration']:.2f}s")
        
        store_metrics(metrics)
