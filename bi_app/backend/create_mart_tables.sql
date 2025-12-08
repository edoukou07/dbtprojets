-- Create schemas
CREATE SCHEMA IF NOT EXISTS dwh_marts_financier;
CREATE SCHEMA IF NOT EXISTS dwh_marts_occupation;
CREATE SCHEMA IF NOT EXISTS dwh_marts_portefeuille;
CREATE SCHEMA IF NOT EXISTS dwh_marts_kpi;
CREATE SCHEMA IF NOT EXISTS dwh_marts_implantation;
CREATE SCHEMA IF NOT EXISTS dwh_marts_rh;

-- Drop existing tables
DROP TABLE IF EXISTS "dwh_marts_implantation"."mart_implantation_suivi" CASCADE;
DROP TABLE IF EXISTS "dwh_marts_rh"."mart_indemnisations" CASCADE;
DROP TABLE IF EXISTS "dwh_marts_rh"."mart_emplois_crees" CASCADE;
DROP TABLE IF EXISTS "dwh_marts_financier"."mart_creances_agees" CASCADE;

-- MartImplantationSuivi table
CREATE TABLE "dwh_marts_implantation"."mart_implantation_suivi" (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL,
    annee INTEGER NOT NULL,
    mois INTEGER,
    nombre_implantations INTEGER DEFAULT 0,
    nombre_etapes INTEGER DEFAULT 0,
    etapes_terminees INTEGER DEFAULT 0,
    etapes_en_retard INTEGER DEFAULT 0,
    taux_completude_pct DECIMAL(5, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- MartIndemnisations table
CREATE TABLE "dwh_marts_rh"."mart_indemnisations" (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER,
    annee INTEGER NOT NULL,
    mois INTEGER,
    nombre_beneficiaires INTEGER DEFAULT 0,
    montant_total DECIMAL(15, 2) DEFAULT 0,
    statut VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- MartEmploisCrees table
CREATE TABLE "dwh_marts_rh"."mart_emplois_crees" (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER,
    annee INTEGER NOT NULL,
    mois INTEGER,
    nombre_emplois_crees INTEGER DEFAULT 0,
    nombre_cdi INTEGER DEFAULT 0,
    nombre_cdd INTEGER DEFAULT 0,
    montant_salaires DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- MartCreancesAgees table
CREATE TABLE "dwh_marts_financier"."mart_creances_agees" (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER,
    annee INTEGER NOT NULL,
    mois INTEGER,
    nombre_creances INTEGER DEFAULT 0,
    montant_creances DECIMAL(15, 2) DEFAULT 0,
    montant_recouvre DECIMAL(15, 2) DEFAULT 0,
    taux_recouvrement_pct DECIMAL(5, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert test data for MartImplantationSuivi
INSERT INTO "dwh_marts_implantation"."mart_implantation_suivi" 
(zone_id, annee, mois, nombre_implantations, nombre_etapes, etapes_terminees, etapes_en_retard, taux_completude_pct)
VALUES 
(1, 2025, 1, 10, 50, 45, 5, 90.0),
(1, 2025, 2, 12, 60, 55, 5, 91.7),
(2, 2025, 1, 8, 40, 35, 5, 87.5),
(2, 2025, 2, 9, 45, 40, 5, 88.9),
(3, 2025, 1, 15, 75, 70, 5, 93.3)
ON CONFLICT DO NOTHING;

-- Insert test data for MartIndemnisations
INSERT INTO "dwh_marts_rh"."mart_indemnisations"
(zone_id, annee, mois, nombre_beneficiaires, montant_total, statut)
VALUES
(1, 2025, 1, 100, 500000.00, 'PAID'),
(1, 2025, 2, 110, 550000.00, 'PAID'),
(2, 2025, 1, 80, 400000.00, 'PENDING'),
(2, 2025, 2, 90, 450000.00, 'PAID'),
(3, 2025, 1, 120, 600000.00, 'PAID')
ON CONFLICT DO NOTHING;

-- Insert test data for MartEmploisCrees
INSERT INTO "dwh_marts_rh"."mart_emplois_crees"
(zone_id, annee, mois, nombre_emplois_crees, nombre_cdi, nombre_cdd, montant_salaires)
VALUES
(1, 2025, 1, 50, 30, 20, 2500000.00),
(1, 2025, 2, 55, 33, 22, 2750000.00),
(2, 2025, 1, 40, 25, 15, 2000000.00),
(2, 2025, 2, 45, 27, 18, 2250000.00),
(3, 2025, 1, 60, 36, 24, 3000000.00)
ON CONFLICT DO NOTHING;

-- Insert test data for MartCreancesAgees
INSERT INTO "dwh_marts_financier"."mart_creances_agees"
(zone_id, annee, mois, nombre_creances, montant_creances, montant_recouvre, taux_recouvrement_pct)
VALUES
(1, 2025, 1, 25, 1000000.00, 850000.00, 85.0),
(1, 2025, 2, 28, 1100000.00, 935000.00, 85.0),
(2, 2025, 1, 20, 800000.00, 640000.00, 80.0),
(2, 2025, 2, 22, 900000.00, 720000.00, 80.0),
(3, 2025, 1, 30, 1200000.00, 1020000.00, 85.0)
ON CONFLICT DO NOTHING;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_implantation_zone_annee ON "dwh_marts_implantation"."mart_implantation_suivi" (zone_id, annee);
CREATE INDEX IF NOT EXISTS idx_indemnisations_zone_annee ON "dwh_marts_rh"."mart_indemnisations" (zone_id, annee);
CREATE INDEX IF NOT EXISTS idx_emplois_zone_annee ON "dwh_marts_rh"."mart_emplois_crees" (zone_id, annee);
CREATE INDEX IF NOT EXISTS idx_creances_zone_annee ON "dwh_marts_financier"."mart_creances_agees" (zone_id, annee);

COMMIT;
