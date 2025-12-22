-- =============================================================================
-- MIGRATION INCRÉMENTALE SIGETI - Novembre 2025 → Décembre 2025
-- =============================================================================
-- Ce script applique UNIQUEMENT les changements détectés entre les deux dumps
-- Sans toucher aux tables Django ni au schema DWH
-- =============================================================================
-- Date: 2025-12-19
-- Changements détectés:
--   - Table detenteurs: 4 nouvelles colonnes
--   - Nouveaux ENUMs: enum_detenteurs_civilite
--   - Nouvelles tables: 6 (optionnel)
-- =============================================================================

BEGIN;

-- ============================================================================
-- ÉTAPE 1: Créer les nouveaux types ENUM (si n'existent pas)
-- ============================================================================

DO $$
BEGIN
    -- ENUM pour civilite dans detenteurs
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'enum_detenteurs_civilite') THEN
        CREATE TYPE enum_detenteurs_civilite AS ENUM ('M', 'Mme', 'Mlle');
        RAISE NOTICE '✓ Type enum_detenteurs_civilite créé';
    ELSE
        RAISE NOTICE '⚠ Type enum_detenteurs_civilite existe déjà';
    END IF;
END $$;

-- ============================================================================
-- ÉTAPE 2: Ajouter les nouvelles colonnes à la table detenteurs
-- ============================================================================

-- Colonne: type_document (varchar 50)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'detenteurs' AND column_name = 'type_document'
    ) THEN
        ALTER TABLE detenteurs ADD COLUMN type_document VARCHAR(50);
        RAISE NOTICE '✓ Colonne detenteurs.type_document ajoutée';
    ELSE
        RAISE NOTICE '⚠ Colonne detenteurs.type_document existe déjà';
    END IF;
END $$;

-- Colonne: document (json)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'detenteurs' AND column_name = 'document'
    ) THEN
        ALTER TABLE detenteurs ADD COLUMN document JSON;
        RAISE NOTICE '✓ Colonne detenteurs.document ajoutée';
    ELSE
        RAISE NOTICE '⚠ Colonne detenteurs.document existe déjà';
    END IF;
END $$;

-- Colonne: civilite (enum)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'detenteurs' AND column_name = 'civilite'
    ) THEN
        ALTER TABLE detenteurs ADD COLUMN civilite enum_detenteurs_civilite;
        RAISE NOTICE '✓ Colonne detenteurs.civilite ajoutée';
    ELSE
        RAISE NOTICE '⚠ Colonne detenteurs.civilite existe déjà';
    END IF;
END $$;

-- Colonne: numero_piece (varchar 100)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'detenteurs' AND column_name = 'numero_piece'
    ) THEN
        ALTER TABLE detenteurs ADD COLUMN numero_piece VARCHAR(100);
        RAISE NOTICE '✓ Colonne detenteurs.numero_piece ajoutée';
    ELSE
        RAISE NOTICE '⚠ Colonne detenteurs.numero_piece existe déjà';
    END IF;
END $$;

-- ============================================================================
-- ETAPE 3: Verification de la migration
-- ============================================================================

DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'detenteurs'
    AND column_name IN ('type_document', 'document', 'civilite', 'numero_piece');
    
    IF col_count = 4 THEN
        RAISE NOTICE '';
        RAISE NOTICE '=======================================================';
        RAISE NOTICE 'MIGRATION REUSSIE - 4/4 colonnes presentes';
        RAISE NOTICE '=======================================================';
    ELSE
        RAISE NOTICE 'ATTENTION: Seulement %/4 colonnes migrees', col_count;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- INFORMATIONS POST-MIGRATION
-- ============================================================================
-- 
-- Prochaines étapes:
-- 1. Vérifier: SELECT column_name FROM information_schema.columns 
--              WHERE table_name = 'detenteurs' ORDER BY ordinal_position;
--
-- 2. Reconstruire le DWH: dbt run
--
-- 3. Les nouvelles tables (optionnelles) peuvent être créées séparément:
--    - configuration_mfa
--    - mfa_tokens  
--    - experts
--    - detenteur_types_droits
--    - types_demande_impense
--    - workflow_historiques
--
-- ============================================================================
