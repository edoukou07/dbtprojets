-- =============================================================================
-- AJOUT TABLE workflow_historiques
-- =============================================================================
-- Cette table trace toutes les actions effectuees sur les impenses
-- =============================================================================

BEGIN;

-- ============================================================================
-- ETAPE 1: Creer l'ENUM pour les types d'action
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'enum_workflow_historiques_action') THEN
        CREATE TYPE enum_workflow_historiques_action AS ENUM (
            'CREATION',
            'SOUMISSION',
            'MODIFICATION',
            'VALIDATION',
            'REJET',
            'RETOUR',
            'UPLOAD_DOCUMENT',
            'SUPPRESSION_DOCUMENT',
            'TRANSMISSION',
            'NOTIFICATION',
            'COMMENTAIRE',
            'CLOTURE',
            'SUSPENSION',
            'REPRISE',
            'ANNULATION',
            'VALIDATION_DG',
            'VALIDATION_DI',
            'VALIDATION_RECEVABILITE',
            'INVALIDATION_RECEVABILITE',
            'VERIFICATION_COMPLETUDE'
        );
        RAISE NOTICE 'Type enum_workflow_historiques_action cree';
    ELSE
        RAISE NOTICE 'Type enum_workflow_historiques_action existe deja';
    END IF;
END $$;

-- ============================================================================
-- ETAPE 2: Creer la sequence
-- ============================================================================

CREATE SEQUENCE IF NOT EXISTS workflow_historiques_id_seq;

-- ============================================================================
-- ETAPE 3: Creer la table workflow_historiques
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'workflow_historiques') THEN
        CREATE TABLE workflow_historiques (
            id INTEGER NOT NULL DEFAULT nextval('workflow_historiques_id_seq'),
            impense_id INTEGER NOT NULL,
            etape INTEGER NOT NULL,
            phase INTEGER,
            action enum_workflow_historiques_action NOT NULL,
            statut_avant VARCHAR(50),
            statut_apres VARCHAR(50),
            user_id INTEGER,
            user_role VARCHAR(100),
            description TEXT,
            donnees_avant JSONB,
            donnees_apres JSONB,
            metadata JSONB,
            ip_address VARCHAR(45),
            user_agent VARCHAR(500),
            date_action TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            PRIMARY KEY (id)
        );
        
        -- Commentaires sur les colonnes
        COMMENT ON TABLE workflow_historiques IS 'Historique des actions sur les impenses';
        COMMENT ON COLUMN workflow_historiques.id IS 'Identifiant unique';
        COMMENT ON COLUMN workflow_historiques.impense_id IS 'ID de l''impense concernee';
        COMMENT ON COLUMN workflow_historiques.etape IS 'Numero de l''etape V1 (1-28)';
        COMMENT ON COLUMN workflow_historiques.phase IS 'Numero de la phase V2 (1-6)';
        COMMENT ON COLUMN workflow_historiques.action IS 'Type d''action effectuee';
        COMMENT ON COLUMN workflow_historiques.statut_avant IS 'Statut avant l''action';
        COMMENT ON COLUMN workflow_historiques.statut_apres IS 'Statut apres l''action';
        COMMENT ON COLUMN workflow_historiques.user_id IS 'ID de l''utilisateur';
        COMMENT ON COLUMN workflow_historiques.user_role IS 'Role de l''utilisateur';
        COMMENT ON COLUMN workflow_historiques.description IS 'Description de l''action';
        COMMENT ON COLUMN workflow_historiques.donnees_avant IS 'Donnees avant modification (JSON)';
        COMMENT ON COLUMN workflow_historiques.donnees_apres IS 'Donnees apres modification (JSON)';
        COMMENT ON COLUMN workflow_historiques.metadata IS 'Metadonnees additionnelles';
        COMMENT ON COLUMN workflow_historiques.ip_address IS 'Adresse IP';
        COMMENT ON COLUMN workflow_historiques.user_agent IS 'User-Agent du navigateur';
        COMMENT ON COLUMN workflow_historiques.date_action IS 'Date et heure de l''action';
        
        RAISE NOTICE 'Table workflow_historiques creee avec succes';
    ELSE
        RAISE NOTICE 'Table workflow_historiques existe deja';
    END IF;
END $$;

-- ============================================================================
-- ETAPE 4: Creer les index pour les performances
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_workflow_historiques_impense_id 
    ON workflow_historiques(impense_id);

CREATE INDEX IF NOT EXISTS idx_workflow_historiques_user_id 
    ON workflow_historiques(user_id);

CREATE INDEX IF NOT EXISTS idx_workflow_historiques_date_action 
    ON workflow_historiques(date_action);

CREATE INDEX IF NOT EXISTS idx_workflow_historiques_action 
    ON workflow_historiques(action);

-- ============================================================================
-- ETAPE 5: Verification
-- ============================================================================

DO $$
DECLARE
    table_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'workflow_historiques'
    ) INTO table_exists;
    
    IF table_exists THEN
        RAISE NOTICE '=======================================================';
        RAISE NOTICE 'TABLE workflow_historiques CREEE AVEC SUCCES';
        RAISE NOTICE '=======================================================';
    ELSE
        RAISE NOTICE 'ERREUR: La table n''a pas ete creee';
    END IF;
END $$;

COMMIT;
