-- =====================================================================
-- Script: apply_compression.sql
-- Description: Appliquer la compression sur les tables SIGETI DWH
-- Exécution: UNE SEULE FOIS lors du setup initial
-- =====================================================================

BEGIN;

-- =====================================================================
-- 1. Configuration TOAST EXTERNAL (compression déportée)
-- =====================================================================

-- Tables de faits (colonnes texte et JSON)
ALTER TABLE dwh_facts.fait_attributions ALTER COLUMN statut_demande SET STORAGE EXTERNAL;
ALTER TABLE dwh_facts.fait_factures ALTER COLUMN statut_paiement SET STORAGE EXTERNAL;
ALTER TABLE dwh_facts.fait_collectes ALTER COLUMN statut_collecte SET STORAGE EXTERNAL;

-- Tables de dimensions (colonnes texte longues)
ALTER TABLE dwh_dim.dim_entreprises ALTER COLUMN nom_entreprise SET STORAGE EXTERNAL;
ALTER TABLE dwh_dim.dim_entreprises ALTER COLUMN adresse_complete SET STORAGE EXTERNAL;
ALTER TABLE dwh_dim.dim_entreprises ALTER COLUMN activite_principale SET STORAGE EXTERNAL;

ALTER TABLE dwh_dim.dim_zones_industrielles ALTER COLUMN description SET STORAGE EXTERNAL;
ALTER TABLE dwh_dim.dim_zones_industrielles ALTER COLUMN localisation SET STORAGE EXTERNAL;

ALTER TABLE dwh_dim.dim_lots ALTER COLUMN description SET STORAGE EXTERNAL;

ALTER TABLE dwh_dim.dim_domaines ALTER COLUMN description SET STORAGE EXTERNAL;

-- =====================================================================
-- 2. Compression LZ4 (PostgreSQL 14+)
-- =====================================================================

-- Vérifier la version PostgreSQL
DO $$
DECLARE
    pg_version INTEGER;
BEGIN
    SELECT current_setting('server_version_num')::INTEGER INTO pg_version;
    
    IF pg_version >= 140000 THEN
        -- Activer la compression LZ4 sur les tables de faits
        ALTER TABLE dwh_facts.fait_attributions SET (toast_compression = 'lz4');
        ALTER TABLE dwh_facts.fait_factures SET (toast_compression = 'lz4');
        ALTER TABLE dwh_facts.fait_collectes SET (toast_compression = 'lz4');
        ALTER TABLE dwh_facts.fait_paiements SET (toast_compression = 'lz4');
        
        -- Activer sur les dimensions volumineuses
        ALTER TABLE dwh_dim.dim_entreprises SET (toast_compression = 'lz4');
        ALTER TABLE dwh_dim.dim_zones_industrielles SET (toast_compression = 'lz4');
        ALTER TABLE dwh_dim.dim_lots SET (toast_compression = 'lz4');
        
        -- Activer sur les marts matérialisées
        ALTER TABLE dwh_marts.mart_kpi_operationnels SET (toast_compression = 'lz4');
        ALTER TABLE dwh_marts.mart_portefeuille_clients SET (toast_compression = 'lz4');
        ALTER TABLE dwh_marts.mart_occupation_zones SET (toast_compression = 'lz4');
        ALTER TABLE dwh_marts.mart_performance_financiere SET (toast_compression = 'lz4');
        
        RAISE NOTICE '✅ Compression LZ4 activée (PostgreSQL %)', pg_version;
    ELSE
        RAISE NOTICE '⚠️  PostgreSQL < 14 - Compression LZ4 non disponible';
    END IF;
END $$;

-- =====================================================================
-- 3. VACUUM FULL pour appliquer la compression
-- =====================================================================

-- IMPORTANT: Cette opération prend un VERROU EXCLUSIF sur chaque table
-- Exécuter pendant une fenêtre de maintenance (hors production)

-- Tables de faits
VACUUM FULL ANALYZE dwh_facts.fait_attributions;
VACUUM FULL ANALYZE dwh_facts.fait_factures;
VACUUM FULL ANALYZE dwh_facts.fait_collectes;
VACUUM FULL ANALYZE dwh_facts.fait_paiements;

-- Tables de dimensions
VACUUM FULL ANALYZE dwh_dim.dim_entreprises;
VACUUM FULL ANALYZE dwh_dim.dim_zones_industrielles;
VACUUM FULL ANALYZE dwh_dim.dim_lots;
VACUUM FULL ANALYZE dwh_dim.dim_domaines;
VACUUM FULL ANALYZE dwh_dim.dim_date;

-- Marts matérialisées
VACUUM FULL ANALYZE dwh_marts.mart_kpi_operationnels;
VACUUM FULL ANALYZE dwh_marts.mart_portefeuille_clients;
VACUUM FULL ANALYZE dwh_marts.mart_occupation_zones;
VACUUM FULL ANALYZE dwh_marts.mart_performance_financiere;

COMMIT;

-- =====================================================================
-- 4. Afficher les gains de compression
-- =====================================================================

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as "Taille Totale",
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as "Taille Table",
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as "Taille TOAST+Index",
    ROUND(100.0 * (pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) / 
          NULLIF(pg_total_relation_size(schemaname||'.'||tablename), 0), 2) as "% Overhead"
FROM pg_tables 
WHERE schemaname IN ('dwh_facts', 'dwh_dim', 'dwh_marts')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- =====================================================================
-- 5. Configuration auto-vacuum pour maintenance continue
-- =====================================================================

-- Tables de faits (très actives)
ALTER TABLE dwh_facts.fait_attributions SET (
    autovacuum_vacuum_scale_factor = 0.05,  -- Vacuum quand 5% changé (vs 20% par défaut)
    autovacuum_analyze_scale_factor = 0.02  -- Analyze quand 2% changé
);

ALTER TABLE dwh_facts.fait_factures SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

ALTER TABLE dwh_facts.fait_collectes SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

ALTER TABLE dwh_facts.fait_paiements SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

-- Dimensions (moins actives)
ALTER TABLE dwh_dim.dim_entreprises SET (
    autovacuum_vacuum_scale_factor = 0.10,
    autovacuum_analyze_scale_factor = 0.05
);

-- ✅ Compression appliquée avec succès!
-- 💡 Exécuter ce script une seule fois lors du setup initial
-- 💡 Le VACUUM FULL hebdomadaire sera géré par le flow de maintenance
