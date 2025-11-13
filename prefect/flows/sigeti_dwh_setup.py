"""
SIGETI DWH - Setup Initial (PRIORITÉ 3)
========================================

Flow Prefect pour configurer le partitionnement et la compression.

⚠️  EXÉCUTION: UNE SEULE FOIS lors du setup initial
🎯 Objectif: Préparer l'infrastructure pour optimisation performances

Étapes:
1. Créer les tables partitionnées (fait_attributions, fait_factures)
2. Appliquer la compression TOAST + LZ4
3. Créer les index sur chaque partition
4. Migrer les données existantes
5. Exécuter VACUUM FULL pour appliquer compression

Performance attendue:
- Réduction espace disque: 50-70%
- Requêtes date-range: 3-16x plus rapides
- Maintenance: 10x plus rapide (partition-level)
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from prefect import flow, task
from prefect.logging import get_run_logger

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "sigeti_node_db",
    "user": "postgres",
    "password": "postgres"
}


@task(name="check_prerequisites", retries=0)
def check_prerequisites():
    """Vérifier les prérequis avant le setup."""
    logger = get_run_logger()
    
    # Vérifier que les scripts SQL existent
    partition_script = SCRIPTS_DIR / "create_partitions.sql"
    compression_script = SCRIPTS_DIR / "apply_compression.sql"
    
    if not partition_script.exists():
        raise FileNotFoundError(f"Script manquant: {partition_script}")
    
    if not compression_script.exists():
        raise FileNotFoundError(f"Script manquant: {compression_script}")
    
    logger.info("✅ Prérequis validés")
    logger.info(f"   - Script partitions: {partition_script}")
    logger.info(f"   - Script compression: {compression_script}")
    
    return True


@task(name="create_partitioned_tables", retries=0)
def create_partitioned_tables():
    """Créer les tables partitionnées et migrer les données."""
    logger = get_run_logger()
    logger.info("🔧 Création des tables partitionnées...")
    
    script_path = SCRIPTS_DIR / "create_partitions.sql"
    
    # Construire la commande psql
    env = {
        "PGPASSWORD": DB_CONFIG["password"],
        "PGCLIENTENCODING": "UTF8"
    }
    
    cmd = [
        "psql",
        "-h", DB_CONFIG["host"],
        "-p", DB_CONFIG["port"],
        "-U", DB_CONFIG["user"],
        "-d", DB_CONFIG["dbname"],
        "-f", str(script_path),
        "-v", "ON_ERROR_STOP=1"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            env={**subprocess.os.environ.copy(), **env},
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            logger.info("✅ Tables partitionnées créées avec succès")
            logger.info(f"Output:\n{result.stdout}")
            
            # Compter les partitions créées
            count_cmd = [
                "psql",
                "-h", DB_CONFIG["host"],
                "-p", DB_CONFIG["port"],
                "-U", DB_CONFIG["user"],
                "-d", DB_CONFIG["dbname"],
                "-t",
                "-c", "SELECT COUNT(*) FROM pg_tables WHERE schemaname='dwh_facts' AND tablename LIKE 'fait_%_20%';"
            ]
            
            count_result = subprocess.run(
                count_cmd,
                env={**subprocess.os.environ.copy(), **env},
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            partition_count = count_result.stdout.strip()
            logger.info(f"📊 Partitions créées: {partition_count}")
            
            return True
        else:
            logger.error(f"❌ Erreur lors de la création des partitions:")
            logger.error(result.stderr)
            raise RuntimeError(f"Échec création partitions: {result.stderr}")
            
    except Exception as e:
        logger.error(f"❌ Exception: {str(e)}")
        raise


@task(name="apply_compression", retries=0)
def apply_compression():
    """Appliquer la compression TOAST + LZ4."""
    logger = get_run_logger()
    logger.info("🗜️  Application de la compression...")
    
    script_path = SCRIPTS_DIR / "apply_compression.sql"
    
    env = {
        "PGPASSWORD": DB_CONFIG["password"],
        "PGCLIENTENCODING": "UTF8"
    }
    
    cmd = [
        "psql",
        "-h", DB_CONFIG["host"],
        "-p", DB_CONFIG["port"],
        "-U", DB_CONFIG["user"],
        "-d", DB_CONFIG["dbname"],
        "-f", str(script_path),
        "-v", "ON_ERROR_STOP=1"
    ]
    
    try:
        # ⚠️  VACUUM FULL prend beaucoup de temps
        logger.warning("⏳ VACUUM FULL en cours... Cela peut prendre 5-30 minutes")
        logger.warning("⚠️  Les tables seront verrouillées pendant cette opération")
        
        result = subprocess.run(
            cmd,
            env={**subprocess.os.environ.copy(), **env},
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=1800  # 30 minutes max
        )
        
        if result.returncode == 0:
            logger.info("✅ Compression appliquée avec succès")
            logger.info(f"Output:\n{result.stdout}")
            
            # Mesurer les gains
            size_cmd = [
                "psql",
                "-h", DB_CONFIG["host"],
                "-p", DB_CONFIG["port"],
                "-U", DB_CONFIG["user"],
                "-d", DB_CONFIG["dbname"],
                "-c", """
                SELECT 
                    schemaname || '.' || tablename as table,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname IN ('dwh_facts', 'dwh_dim', 'dwh_marts')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10;
                """
            ]
            
            size_result = subprocess.run(
                size_cmd,
                env={**subprocess.os.environ.copy(), **env},
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            logger.info("📊 Taille des tables après compression:")
            logger.info(f"\n{size_result.stdout}")
            
            return True
        else:
            logger.error(f"❌ Erreur lors de l'application de la compression:")
            logger.error(result.stderr)
            raise RuntimeError(f"Échec compression: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout: VACUUM FULL a pris plus de 30 minutes")
        raise
    except Exception as e:
        logger.error(f"❌ Exception: {str(e)}")
        raise


@task(name="verify_setup", retries=0)
def verify_setup():
    """Vérifier que le setup s'est bien passé."""
    logger = get_run_logger()
    logger.info("🔍 Vérification du setup...")
    
    env = {
        "PGPASSWORD": DB_CONFIG["password"],
        "PGCLIENTENCODING": "UTF8"
    }
    
    # Vérifier les partitions
    cmd = [
        "psql",
        "-h", DB_CONFIG["host"],
        "-p", DB_CONFIG["port"],
        "-U", DB_CONFIG["user"],
        "-d", DB_CONFIG["dbname"],
        "-c", """
        SELECT 
            pt.tablename as partition,
            pg_size_pretty(pg_total_relation_size('dwh_facts.'||pt.tablename)) as size,
            (SELECT COUNT(*) FROM dwh_facts.fait_attributions WHERE attribution_key IS NOT NULL) as row_count_estimate
        FROM pg_tables pt
        WHERE pt.schemaname = 'dwh_facts' 
          AND pt.tablename LIKE 'fait_attributions_20%'
        ORDER BY pt.tablename;
        """
    ]
    
    result = subprocess.run(
        cmd,
        env={**subprocess.os.environ.copy(), **env},
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    if result.returncode == 0:
        logger.info("📊 État des partitions:")
        logger.info(f"\n{result.stdout}")
        logger.info("✅ Setup vérifié avec succès")
        return True
    else:
        logger.warning("⚠️  Impossible de vérifier les partitions")
        return False


@flow(name="SIGETI DWH - Setup Initial (PRIORITÉ 3)", log_prints=True)
def sigeti_dwh_setup():
    """
    Flow de setup initial pour PRIORITÉ 3.
    
    ⚠️  À exécuter UNE SEULE FOIS après le déploiement initial.
    
    Ce flow:
    1. Vérifie les prérequis
    2. Crée les tables partitionnées (2020-2030)
    3. Applique la compression TOAST + LZ4
    4. Migre les données existantes
    5. Exécute VACUUM FULL
    6. Vérifie le résultat
    
    Durée estimée: 10-30 minutes (selon volume de données)
    """
    logger = get_run_logger()
    
    logger.info("=" * 70)
    logger.info("🚀 SIGETI DWH - Setup Initial (PRIORITÉ 3)")
    logger.info("=" * 70)
    logger.info(f"⏰ Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    try:
        # Étape 1: Vérifier prérequis
        logger.info("[ÉTAPE 1/4] Vérification des prérequis...")
        check_prerequisites()
        logger.info("")
        
        # Étape 2: Créer partitions
        logger.info("[ÉTAPE 2/4] Création des tables partitionnées...")
        logger.warning("⚠️  Cette opération va migrer les données existantes")
        create_partitioned_tables()
        logger.info("")
        
        # Étape 3: Appliquer compression
        logger.info("[ÉTAPE 3/4] Application de la compression...")
        logger.warning("⚠️  VACUUM FULL va verrouiller les tables (5-30 min)")
        apply_compression()
        logger.info("")
        
        # Étape 4: Vérifier
        logger.info("[ÉTAPE 4/4] Vérification du setup...")
        verify_setup()
        logger.info("")
        
        logger.info("=" * 70)
        logger.info("✅ Setup PRIORITÉ 3 terminé avec succès!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("📝 Prochaines étapes:")
        logger.info("   1. Exécuter le flow quotidien normalement")
        logger.info("   2. Les nouvelles partitions seront créées automatiquement")
        logger.info("   3. Le VACUUM hebdomadaire sera géré automatiquement")
        logger.info("")
        logger.info(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "SUCCESS"
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ Erreur lors du setup: {str(e)}")
        logger.error("=" * 70)
        logger.error("")
        logger.error("🔧 Actions correctives:")
        logger.error("   1. Vérifier les logs ci-dessus")
        logger.error("   2. Vérifier la connexion PostgreSQL")
        logger.error("   3. Vérifier que psql est installé")
        logger.error("   4. Exécuter manuellement les scripts SQL si nécessaire")
        raise


if __name__ == "__main__":
    # Exécution locale
    print("\n⚠️  ATTENTION: Ce flow va modifier la structure de la base de données!")
    print("⚠️  Assurez-vous d'avoir une sauvegarde avant de continuer.\n")
    
    response = input("Voulez-vous continuer? (oui/non): ").strip().lower()
    
    if response == "oui":
        sigeti_dwh_setup()
    else:
        print("❌ Setup annulé par l'utilisateur")
        sys.exit(0)
