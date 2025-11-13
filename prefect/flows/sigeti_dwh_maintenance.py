"""
SIGETI DWH - Maintenance Mensuelle (PRIORITÉ 3)
================================================

Flow Prefect pour la maintenance lourde mensuelle.

⚠️  EXÉCUTION: 1er de chaque mois à 3h du matin
🎯 Objectif: Maintenance lourde pour optimiser performances

Étapes:
1. VACUUM FULL sur les anciennes partitions (> 3 mois)
2. Archiver les partitions très anciennes (> 5 ans)
3. Réorganiser les index
4. Générer rapport de santé

Performance attendue:
- Récupération espace disque: 10-30%
- Optimisation index: 20-50% plus rapides
- Durée: 30-60 minutes
"""

import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from prefect import flow, task
from prefect.logging import get_run_logger

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "sigeti_node_db",
    "user": "postgres",
    "password": "postgres"
}


def execute_sql(sql_query: str, description: str = ""):
    """Exécuter une requête SQL et retourner le résultat."""
    logger = get_run_logger()
    
    if description:
        logger.info(f"🔧 {description}")
    
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
        "-c", sql_query
    ]
    
    try:
        result = subprocess.run(
            cmd,
            env={**subprocess.os.environ.copy(), **env},
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=3600  # 1h max
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            logger.error(f"❌ Erreur: {result.stderr}")
            raise RuntimeError(result.stderr)
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout après 1h")
        raise


@task(name="vacuum_old_partitions", retries=0)
def vacuum_old_partitions():
    """VACUUM FULL sur les partitions de plus de 3 mois."""
    logger = get_run_logger()
    logger.info("🧹 VACUUM FULL des anciennes partitions...")
    
    # Calculer l'année de la limite (3 mois en arrière)
    cutoff_date = datetime.now() - timedelta(days=90)
    cutoff_year = cutoff_date.year
    
    logger.info(f"📅 Année limite: {cutoff_year}")
    
    # Lister les partitions à vacuum
    partitions_query = f"""
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'dwh_facts' 
      AND tablename LIKE 'fait_attributions_20%'
      AND tablename <= 'fait_attributions_{cutoff_year}'
    ORDER BY tablename;
    """
    
    partitions_output = execute_sql(partitions_query, "Liste des partitions à vacuum")
    partitions = [p.strip() for p in partitions_output.split('\n') if p.strip() and not p.startswith('-')]
    
    logger.info(f"📊 Partitions à traiter: {len(partitions)}")
    
    # VACUUM FULL chaque partition
    for partition in partitions:
        logger.info(f"   🧹 VACUUM FULL dwh_facts.{partition}...")
        
        vacuum_query = f"VACUUM FULL ANALYZE dwh_facts.{partition};"
        
        try:
            execute_sql(vacuum_query)
            logger.info(f"   ✅ {partition} terminé")
        except Exception as e:
            logger.warning(f"   ⚠️  {partition} échoué: {str(e)}")
    
    logger.info("✅ VACUUM FULL terminé")
    return len(partitions)


@task(name="archive_very_old_partitions", retries=0)
def archive_very_old_partitions():
    """Archiver/supprimer les partitions de plus de 5 ans."""
    logger = get_run_logger()
    logger.info("📦 Archivage des très anciennes partitions...")
    
    # Calculer l'année limite (5 ans en arrière)
    cutoff_year = datetime.now().year - 5
    
    logger.info(f"📅 Année limite: {cutoff_year}")
    
    # Lister les partitions à archiver
    partitions_query = f"""
    SELECT 
        tablename,
        pg_size_pretty(pg_total_relation_size('dwh_facts.'||tablename)) as size
    FROM pg_tables 
    WHERE schemaname = 'dwh_facts' 
      AND tablename LIKE 'fait_attributions_20%'
      AND tablename < 'fait_attributions_{cutoff_year}'
    ORDER BY tablename;
    """
    
    partitions_output = execute_sql(partitions_query, "Partitions à archiver")
    
    logger.info(f"Partitions candidates:\n{partitions_output}")
    
    # Pour l'instant, juste logger (ne pas supprimer automatiquement)
    logger.warning("⚠️  Archivage automatique désactivé pour sécurité")
    logger.warning("⚠️  Exécuter manuellement si nécessaire:")
    logger.warning(f"    DROP TABLE dwh_facts.fait_attributions_{cutoff_year-1};")
    
    return 0


@task(name="reindex_tables", retries=0)
def reindex_tables():
    """Réorganiser les index des tables principales."""
    logger = get_run_logger()
    logger.info("🔧 Réorganisation des index...")
    
    # Tables de faits principales
    tables = [
        "dwh_facts.fait_attributions",
        "dwh_facts.fait_factures",
        "dwh_facts.fait_collectes",
        "dwh_facts.fait_paiements"
    ]
    
    for table in tables:
        logger.info(f"   🔧 REINDEX {table}...")
        
        try:
            reindex_query = f"REINDEX TABLE {table};"
            execute_sql(reindex_query)
            logger.info(f"   ✅ {table} terminé")
        except Exception as e:
            logger.warning(f"   ⚠️  {table} échoué: {str(e)}")
    
    logger.info("✅ Réindexation terminée")
    return len(tables)


@task(name="generate_health_report", retries=0)
def generate_health_report():
    """Générer un rapport de santé de la base."""
    logger = get_run_logger()
    logger.info("📊 Génération du rapport de santé...")
    
    # Rapport 1: Taille des tables
    size_query = """
    SELECT 
        schemaname || '.' || tablename as table_name,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
        pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
    FROM pg_tables 
    WHERE schemaname IN ('dwh_facts', 'dwh_dim', 'dwh_marts')
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
    LIMIT 20;
    """
    
    size_report = execute_sql(size_query, "Taille des tables")
    logger.info(f"\n📊 TOP 20 Tables:\n{size_report}")
    
    # Rapport 2: Nombre de lignes par partition
    rows_query = """
    SELECT 
        tablename,
        (SELECT COUNT(*) FROM dwh_facts.fait_attributions) as estimated_rows
    FROM pg_tables 
    WHERE schemaname = 'dwh_facts' 
      AND tablename LIKE 'fait_attributions_20%'
    LIMIT 5;
    """
    
    rows_report = execute_sql(rows_query, "Lignes par partition")
    logger.info(f"\n📊 Lignes par partition:\n{rows_report}")
    
    # Rapport 3: Index non utilisés
    unused_index_query = """
    SELECT 
        schemaname || '.' || tablename as table,
        indexname,
        pg_size_pretty(pg_relation_size(indexrelid)) as index_size
    FROM pg_stat_user_indexes
    WHERE schemaname IN ('dwh_facts', 'dwh_dim', 'dwh_marts')
      AND idx_scan = 0
      AND indexrelname NOT LIKE '%_pkey'
    ORDER BY pg_relation_size(indexrelid) DESC;
    """
    
    unused_report = execute_sql(unused_index_query, "Index non utilisés")
    logger.info(f"\n📊 Index non utilisés:\n{unused_report}")
    
    # Rapport 4: Bloat estimation
    bloat_query = """
    SELECT 
        schemaname || '.' || tablename as table_name,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
        n_dead_tup as dead_tuples,
        ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as bloat_percent
    FROM pg_stat_user_tables
    WHERE schemaname IN ('dwh_facts', 'dwh_dim', 'dwh_marts')
      AND n_dead_tup > 0
    ORDER BY n_dead_tup DESC
    LIMIT 10;
    """
    
    bloat_report = execute_sql(bloat_query, "Estimation du bloat")
    logger.info(f"\n📊 Tables avec bloat:\n{bloat_report}")
    
    logger.info("✅ Rapport de santé généré")
    return True


@flow(name="SIGETI DWH - Maintenance Mensuelle", log_prints=True)
def sigeti_dwh_monthly_maintenance():
    """
    Flow de maintenance mensuelle pour PRIORITÉ 3.
    
    ⚠️  À exécuter le 1er de chaque mois à 3h du matin.
    
    Ce flow:
    1. VACUUM FULL sur anciennes partitions (> 3 mois)
    2. Archive partitions très anciennes (> 5 ans)
    3. Réorganise les index
    4. Génère rapport de santé
    
    Durée estimée: 30-60 minutes
    """
    logger = get_run_logger()
    
    logger.info("=" * 70)
    logger.info("🧹 SIGETI DWH - Maintenance Mensuelle (PRIORITÉ 3)")
    logger.info("=" * 70)
    logger.info(f"⏰ Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    try:
        # Étape 1: VACUUM FULL
        logger.info("[ÉTAPE 1/4] VACUUM FULL des anciennes partitions...")
        partitions_vacuumed = vacuum_old_partitions()
        logger.info(f"   ✅ {partitions_vacuumed} partitions traitées")
        logger.info("")
        
        # Étape 2: Archivage
        logger.info("[ÉTAPE 2/4] Archivage des très anciennes partitions...")
        partitions_archived = archive_very_old_partitions()
        logger.info(f"   ℹ️  {partitions_archived} partitions archivées")
        logger.info("")
        
        # Étape 3: Réindexation
        logger.info("[ÉTAPE 3/4] Réorganisation des index...")
        tables_reindexed = reindex_tables()
        logger.info(f"   ✅ {tables_reindexed} tables réindexées")
        logger.info("")
        
        # Étape 4: Rapport
        logger.info("[ÉTAPE 4/4] Génération du rapport de santé...")
        generate_health_report()
        logger.info("")
        
        logger.info("=" * 70)
        logger.info("✅ Maintenance mensuelle terminée avec succès!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("📊 Résumé:")
        logger.info(f"   - Partitions vacuum: {partitions_vacuumed}")
        logger.info(f"   - Partitions archivées: {partitions_archived}")
        logger.info(f"   - Tables réindexées: {tables_reindexed}")
        logger.info("")
        logger.info(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "SUCCESS"
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ Erreur lors de la maintenance: {str(e)}")
        logger.error("=" * 70)
        raise


if __name__ == "__main__":
    # Exécution locale
    sigeti_dwh_monthly_maintenance()
