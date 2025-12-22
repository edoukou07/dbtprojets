-- =============================================================================
-- AJOUT TABLES: types_demande_impense et experts
-- =============================================================================
-- Migration incrementale - Decembre 2025
-- =============================================================================

BEGIN;

-- ============================================================================
-- TABLE 1: types_demande_impense
-- ============================================================================

CREATE SEQUENCE IF NOT EXISTS types_demande_impense_id_seq;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'types_demande_impense') THEN
        CREATE TABLE types_demande_impense (
            id INTEGER NOT NULL DEFAULT nextval('types_demande_impense_id_seq'),
            code VARCHAR(50) NOT NULL,
            libelle VARCHAR(255) NOT NULL,
            description TEXT,
            actif BOOLEAN NOT NULL DEFAULT true,
            ordre INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        );
        
        -- Contrainte unique sur le code
        ALTER TABLE types_demande_impense ADD CONSTRAINT types_demande_impense_code_unique UNIQUE (code);
        
        RAISE NOTICE 'Table types_demande_impense creee';
    ELSE
        RAISE NOTICE 'Table types_demande_impense existe deja';
    END IF;
END $$;

-- Insertion des donnees de reference
INSERT INTO types_demande_impense (id, code, libelle, description, actif, ordre, created_at, updated_at)
VALUES 
    (1, 'depenses_maintenance', 'Depenses liees a la maintenance', 'Frais relatifs a l''entretien et la maintenance des equipements et infrastructures', false, 1, '2025-11-27 09:19:05.452+00', '2025-12-08 18:27:22.967+00'),
    (2, 'depenses_securite', 'Depenses liees a la securite', 'Frais relatifs a la securite des installations et du personnel', false, 2, '2025-11-27 09:19:05.452+00', '2025-12-08 18:27:26.847+00'),
    (3, 'depenses_production', 'Depenses liees a la production', 'Frais relatifs aux activites de production', false, 3, '2025-11-27 09:19:05.452+00', '2025-11-27 10:28:33.07+00'),
    (4, 'depenses_infrastructures', 'Depenses liees aux infrastructures', 'Frais relatifs aux infrastructures et batiments', false, 4, '2025-11-27 09:19:05.452+00', '2025-12-08 18:27:36.914+00'),
    (5, 'depenses_energie', 'Depenses liees a l''energie', 'Frais relatifs a la consommation et gestion de l''energie', false, 5, '2025-11-27 09:19:05.452+00', '2025-12-08 18:27:44.847+00'),
    (6, 'depenses_conformite', 'Depenses de conformite reglementaire', 'Frais relatifs a la mise en conformite avec les reglementations', false, 6, '2025-11-27 09:19:05.452+00', '2025-12-08 18:27:56.682+00'),
    (7, 'depenses_amelioration', 'Depenses liees a l''amelioration continue', 'Frais relatifs aux projets d''amelioration et d''optimisation', false, 7, '2025-11-27 09:19:05.452+00', '2025-12-08 18:27:48.203+00'),
    (8, 'CESSION_VOLONTAIRE', 'Cession volontaire', 'Demande de cession volontaire d''impense par l''operateur souhaitant ceder son lot', true, 1, '2025-12-08 18:25:38.183+00', '2025-12-08 18:25:38.183+00'),
    (9, 'RETRAIT_ADMINISTRATIF', 'Retrait administratif', 'Retrait administratif d''un lot pour non-conformite ou manquement aux obligations', true, 2, '2025-12-08 18:25:38.183+00', '2025-12-08 18:25:38.183+00')
ON CONFLICT (code) DO NOTHING;

-- Mettre a jour la sequence
SELECT setval('types_demande_impense_id_seq', COALESCE((SELECT MAX(id) FROM types_demande_impense), 0) + 1, false);

-- ============================================================================
-- TABLE 2: experts
-- ============================================================================

CREATE SEQUENCE IF NOT EXISTS experts_id_seq;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'experts') THEN
        CREATE TABLE experts (
            id INTEGER NOT NULL DEFAULT nextval('experts_id_seq'),
            nom VARCHAR(100) NOT NULL,
            specialite VARCHAR(200),
            telephone VARCHAR(30),
            email VARCHAR(150),
            adresse TEXT,
            numero_agrement VARCHAR(50),
            date_agrement DATE,
            organisme_agrement VARCHAR(200),
            actif BOOLEAN NOT NULL DEFAULT true,
            observations TEXT,
            created_by INTEGER,
            updated_by INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        );
        
        -- Commentaires
        COMMENT ON TABLE experts IS 'Liste des experts evaluateurs';
        COMMENT ON COLUMN experts.nom IS 'Nom complet de l''expert';
        COMMENT ON COLUMN experts.specialite IS 'Specialite / Domaine d''expertise';
        COMMENT ON COLUMN experts.telephone IS 'Numero de telephone';
        COMMENT ON COLUMN experts.email IS 'Adresse email';
        COMMENT ON COLUMN experts.adresse IS 'Adresse professionnelle';
        COMMENT ON COLUMN experts.numero_agrement IS 'Numero d''agrement / Ordre';
        COMMENT ON COLUMN experts.date_agrement IS 'Date d''obtention de l''agrement';
        COMMENT ON COLUMN experts.organisme_agrement IS 'Organisme ayant delivre l''agrement';
        COMMENT ON COLUMN experts.actif IS 'Expert actif ou non';
        COMMENT ON COLUMN experts.observations IS 'Notes et observations';
        COMMENT ON COLUMN experts.created_by IS 'ID utilisateur createur';
        COMMENT ON COLUMN experts.updated_by IS 'ID utilisateur modificateur';
        
        RAISE NOTICE 'Table experts creee';
    ELSE
        RAISE NOTICE 'Table experts existe deja';
    END IF;
END $$;

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_experts_actif ON experts(actif);
CREATE INDEX IF NOT EXISTS idx_experts_specialite ON experts(specialite);

-- ============================================================================
-- VERIFICATION FINALE
-- ============================================================================

DO $$
DECLARE
    t1_exists BOOLEAN;
    t2_exists BOOLEAN;
BEGIN
    SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'types_demande_impense') INTO t1_exists;
    SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'experts') INTO t2_exists;
    
    RAISE NOTICE '';
    RAISE NOTICE '=======================================================';
    IF t1_exists AND t2_exists THEN
        RAISE NOTICE 'MIGRATION REUSSIE - 2/2 tables creees';
    ELSE
        RAISE NOTICE 'ATTENTION: Certaines tables manquent';
    END IF;
    RAISE NOTICE '  - types_demande_impense: %', CASE WHEN t1_exists THEN 'OK' ELSE 'MANQUANTE' END;
    RAISE NOTICE '  - experts: %', CASE WHEN t2_exists THEN 'OK' ELSE 'MANQUANTE' END;
    RAISE NOTICE '=======================================================';
END $$;

COMMIT;
