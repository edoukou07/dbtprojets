-- =====================================================================
-- Script: create_partitions.sql
-- Description: Créer les tables partitionnées pour SIGETI DWH
-- Exécution: UNE SEULE FOIS lors du setup initial
-- =====================================================================

BEGIN;

-- =====================================================================
-- 1. FAIT_ATTRIBUTIONS - Partitionnement par année
-- =====================================================================

-- Créer la table MÈRE partitionnée
CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_partitioned (
    attribution_key SERIAL,
    demande_id INTEGER,
    entreprise_key INTEGER,
    lot_key INTEGER,
    zone_key INTEGER,
    domaine_key INTEGER,
    date_demandee_key INTEGER,
    date_approbation_key INTEGER,
    montant_attribution NUMERIC(15,2),
    superficie_demandee NUMERIC(10,2),
    superficie_attribuee NUMERIC(10,2),
    statut_demande VARCHAR(50),
    est_approuve BOOLEAN,
    est_rejete BOOLEAN,
    delai_traitement_jours INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (date_demandee_key);

-- Créer les partitions par année (2020-2030)
CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2020 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20200101) TO (20210101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2021 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20210101) TO (20220101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2022 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20220101) TO (20230101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2023 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20230101) TO (20240101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2024 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20240101) TO (20250101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2025 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20250101) TO (20260101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2026 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20260101) TO (20270101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2027 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20270101) TO (20280101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2028 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20280101) TO (20290101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2029 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20290101) TO (20300101);

CREATE TABLE IF NOT EXISTS dwh_facts.fait_attributions_2030 
PARTITION OF dwh_facts.fait_attributions_partitioned
FOR VALUES FROM (20300101) TO (20310101);

-- Créer les index sur CHAQUE partition
CREATE INDEX IF NOT EXISTS idx_attr_2020_entreprise ON dwh_facts.fait_attributions_2020(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2020_lot ON dwh_facts.fait_attributions_2020(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2020_date ON dwh_facts.fait_attributions_2020(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2021_entreprise ON dwh_facts.fait_attributions_2021(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2021_lot ON dwh_facts.fait_attributions_2021(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2021_date ON dwh_facts.fait_attributions_2021(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2022_entreprise ON dwh_facts.fait_attributions_2022(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2022_lot ON dwh_facts.fait_attributions_2022(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2022_date ON dwh_facts.fait_attributions_2022(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2023_entreprise ON dwh_facts.fait_attributions_2023(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2023_lot ON dwh_facts.fait_attributions_2023(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2023_date ON dwh_facts.fait_attributions_2023(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2024_entreprise ON dwh_facts.fait_attributions_2024(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2024_lot ON dwh_facts.fait_attributions_2024(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2024_date ON dwh_facts.fait_attributions_2024(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2025_entreprise ON dwh_facts.fait_attributions_2025(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2025_lot ON dwh_facts.fait_attributions_2025(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2025_date ON dwh_facts.fait_attributions_2025(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2026_entreprise ON dwh_facts.fait_attributions_2026(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2026_lot ON dwh_facts.fait_attributions_2026(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2026_date ON dwh_facts.fait_attributions_2026(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2027_entreprise ON dwh_facts.fait_attributions_2027(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2027_lot ON dwh_facts.fait_attributions_2027(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2027_date ON dwh_facts.fait_attributions_2027(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2028_entreprise ON dwh_facts.fait_attributions_2028(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2028_lot ON dwh_facts.fait_attributions_2028(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2028_date ON dwh_facts.fait_attributions_2028(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2029_entreprise ON dwh_facts.fait_attributions_2029(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2029_lot ON dwh_facts.fait_attributions_2029(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2029_date ON dwh_facts.fait_attributions_2029(date_demandee_key);

CREATE INDEX IF NOT EXISTS idx_attr_2030_entreprise ON dwh_facts.fait_attributions_2030(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_attr_2030_lot ON dwh_facts.fait_attributions_2030(lot_key);
CREATE INDEX IF NOT EXISTS idx_attr_2030_date ON dwh_facts.fait_attributions_2030(date_demandee_key);

-- Migrer les données existantes (si la table existe déjà)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'dwh_facts' AND tablename = 'fait_attributions') THEN
        -- Copier les données
        INSERT INTO dwh_facts.fait_attributions_partitioned 
        SELECT * FROM dwh_facts.fait_attributions
        ON CONFLICT DO NOTHING;
        
        -- Renommer l'ancienne table
        ALTER TABLE dwh_facts.fait_attributions RENAME TO fait_attributions_old_backup;
        
        -- Renommer la nouvelle table partitionnée
        ALTER TABLE dwh_facts.fait_attributions_partitioned RENAME TO fait_attributions;
        
        RAISE NOTICE '✅ Données migrées vers table partitionnée';
    ELSE
        -- Si la table n'existe pas encore, simplement renommer
        ALTER TABLE dwh_facts.fait_attributions_partitioned RENAME TO fait_attributions;
        RAISE NOTICE '✅ Table partitionnée créée';
    END IF;
END $$;

-- =====================================================================
-- 2. FAIT_FACTURES - Partitionnement par année
-- =====================================================================

CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_partitioned (
    facture_key SERIAL,
    facture_id INTEGER,
    entreprise_key INTEGER,
    collecte_key INTEGER,
    date_creation_key INTEGER,
    date_echeance_key INTEGER,
    montant_total NUMERIC(15,2),
    est_paye BOOLEAN,
    est_en_retard BOOLEAN,
    delai_paiement_jours INTEGER,
    statut_paiement VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (date_creation_key);

-- Créer partitions 2020-2030
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2020 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20200101) TO (20210101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2021 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20210101) TO (20220101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2022 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20220101) TO (20230101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2023 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20230101) TO (20240101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2024 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20240101) TO (20250101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2025 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20250101) TO (20260101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2026 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20260101) TO (20270101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2027 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20270101) TO (20280101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2028 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20280101) TO (20290101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2029 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20290101) TO (20300101);
CREATE TABLE IF NOT EXISTS dwh_facts.fait_factures_2030 PARTITION OF dwh_facts.fait_factures_partitioned FOR VALUES FROM (20300101) TO (20310101);

-- Index sur chaque partition
CREATE INDEX IF NOT EXISTS idx_fact_2024_entreprise ON dwh_facts.fait_factures_2024(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_fact_2025_entreprise ON dwh_facts.fait_factures_2025(entreprise_key);
CREATE INDEX IF NOT EXISTS idx_fact_2026_entreprise ON dwh_facts.fait_factures_2026(entreprise_key);

-- Migrer données si nécessaire
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'dwh_facts' AND tablename = 'fait_factures') THEN
        INSERT INTO dwh_facts.fait_factures_partitioned SELECT * FROM dwh_facts.fait_factures ON CONFLICT DO NOTHING;
        ALTER TABLE dwh_facts.fait_factures RENAME TO fait_factures_old_backup;
        ALTER TABLE dwh_facts.fait_factures_partitioned RENAME TO fait_factures;
        RAISE NOTICE '✅ fait_factures migré vers table partitionnée';
    ELSE
        ALTER TABLE dwh_facts.fait_factures_partitioned RENAME TO fait_factures;
        RAISE NOTICE '✅ fait_factures partitionné créé';
    END IF;
END $$;

COMMIT;

-- =====================================================================
-- Afficher résumé
-- =====================================================================
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('dwh_facts.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'dwh_facts' 
  AND tablename LIKE 'fait_%'
ORDER BY tablename;

-- ✅ Partitions créées avec succès!
-- 💡 Les nouvelles partitions seront créées automatiquement par le flow quotidien
