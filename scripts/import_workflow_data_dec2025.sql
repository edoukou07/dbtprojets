-- =============================================================================
-- SCRIPT D'IMPORT DES DONNÉES WORKFLOW DU DUMP DU 18 DÉCEMBRE 2025
-- =============================================================================
-- Ce script importe les données manquantes de workflow_historiques et impenses
-- depuis le dump sigeti_db_18_decembre_2025.sql vers la base locale
-- 
-- Exécution: psql -U postgres -d sigeti_node_db -f scripts/import_workflow_data_dec2025.sql
-- =============================================================================

BEGIN;

-- ============================================================================
-- PARTIE 1: VÉRIFICATION DE L'ÉTAT ACTUEL
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'ÉTAT AVANT IMPORT:';
    RAISE NOTICE '========================================';
END $$;

SELECT 'Impenses actuelles:' as info, COUNT(*) as total FROM impenses;
SELECT 'Workflow_historiques actuelles:' as info, COUNT(*) as total FROM workflow_historiques;

-- ============================================================================
-- PARTIE 2: IMPORT DES IMPENSES MANQUANTES (IDs 4-49)
-- ============================================================================

-- Désactivation temporaire des contraintes FK pour l'import
SET CONSTRAINTS ALL DEFERRED;

-- IMPENSES avec workflow_historiques (IDs 34-47)
-- Ces impenses ont des données de workflow complètes dans le dump
-- Structure: id, numero_dossier, statut, etape_actuelle, etapes_completees, historique_etapes, 
--            lot_id, lot_numero, lot_ilot, entreprise_id, nom_operateur, date_emission, motif_cession, created_at, updated_at

INSERT INTO "public"."impenses" (id, numero_dossier, statut, etape_actuelle, etapes_completees, historique_etapes, lot_id, lot_numero, lot_ilot, entreprise_id, nom_operateur, date_emission, motif_cession, created_at, updated_at)
VALUES 
(34, 'IMP-20251209-3JQXY', 'en cours', 1, '[]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T09:38:06.791Z","donnees":{"numero_dossier":"IMP-20251209-3JQXY","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'À définir', '2025-12-09 09:38:06.791+00', NULL, '2025-12-09 09:38:06.791+00', '2025-12-09 09:38:06.791+00'),
(35, 'IMP-20251209-6OE2A', 'en cours', 2, '[1]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T09:58:00.404Z","donnees":{"numero_dossier":"IMP-20251209-6OE2A","statut":"en cours"}}]', 55, 'Commodi sint quia e', 'Possimus beatae qua', 40, 'Nouvelle entreprise 1', '2025-12-09 09:58:00.404+00', NULL, '2025-12-09 09:58:00.404+00', '2025-12-09 09:58:00.404+00'),
(36, 'IMP-20251209-3R3XG', 'en cours', 2, '[1]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T10:09:19.619Z","donnees":{"numero_dossier":"IMP-20251209-3R3XG","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-09 10:09:19.619+00', 'Nam veritatis sit au', '2025-12-09 10:09:19.619+00', '2025-12-09 10:09:19.619+00'),
(37, 'IMP-20251209-Z1YI2', 'en cours', 2, '[1]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T10:26:43.599Z","donnees":{"numero_dossier":"IMP-20251209-Z1YI2","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-09 10:26:43.599+00', 'Temporibus quia maxi', '2025-12-09 10:26:43.599+00', '2025-12-09 10:26:43.599+00'),
(38, 'IMP-20251209-G8308', 'en cours', 2, '[1]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T10:35:04.756Z","donnees":{"numero_dossier":"IMP-20251209-G8308","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-09 10:35:04.756+00', 'Ut aute sed dolores', '2025-12-09 10:35:04.756+00', '2025-12-09 10:35:04.756+00'),
(39, 'IMP-20251209-RZR87', 'en cours', 2, '[1]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T10:38:59.539Z","donnees":{"numero_dossier":"IMP-20251209-RZR87","statut":"en cours"}}]', 54, 'Debitis quis pariatu', 'Commodi nobis eum au', 39, 'Dolore accusamus min', '2025-12-09 10:38:59.539+00', NULL, '2025-12-09 10:38:59.539+00', '2025-12-09 10:38:59.539+00'),
(40, 'IMP-20251209-TVWO8', 'en cours', 2, '[1]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T10:52:09.452Z","donnees":{"numero_dossier":"IMP-20251209-TVWO8","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-09 10:52:09.452+00', 'Commodo illum porro', '2025-12-09 10:52:09.452+00', '2025-12-09 10:52:09.452+00'),
(41, 'IMP-20251209-6PWAZ', 'en cours', 2, '[1]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T10:56:27.678Z","donnees":{"numero_dossier":"IMP-20251209-6PWAZ","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-09 10:56:27.678+00', 'Aliquid omnis tempor', '2025-12-09 10:56:27.678+00', '2025-12-09 10:56:27.678+00'),
(42, 'IMP-20251209-ZGGKI', 'en cours', 2, '[1]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T11:18:27.340Z","donnees":{"numero_dossier":"IMP-20251209-ZGGKI","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-09 11:18:27.341+00', 'Voluptatem rerum adi', '2025-12-09 11:18:27.341+00', '2025-12-09 11:18:27.341+00'),
(43, 'IMP-20251209-YQDKJ', 'en cours', 1, '[]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T15:22:31.190Z","donnees":{"numero_dossier":"IMP-20251209-YQDKJ","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-09 15:22:31.19+00', 'Harum totam reprehen', '2025-12-09 15:22:31.19+00', '2025-12-09 15:22:31.19+00'),
(44, 'IMP-20251209-WS6RC', 'en cours', 2, '[1,2,3,4]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-09T15:25:22.610Z","donnees":{"numero_dossier":"IMP-20251209-WS6RC","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-09 15:25:22.611+00', 'Sint aspernatur opti', '2025-12-09 15:25:22.611+00', '2025-12-15 15:58:06.751+00'),
(45, 'IMP-20251211-BRJ69', 'en cours', 6, '[1,3,4,5,6]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-11T13:49:11.136Z","donnees":{"numero_dossier":"IMP-20251211-BRJ69","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-11 13:49:11.136+00', NULL, '2025-12-11 13:49:11.136+00', '2025-12-15 15:39:00.094+00'),
(46, 'IMP-20251211-KE799', 'en cours', 7, '[1,6,3,4]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-11T14:18:06.844Z","donnees":{"numero_dossier":"IMP-20251211-KE799","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-11 14:18:06.844+00', 'Veniam dolorum exer', '2025-12-11 14:18:06.844+00', '2025-12-11 18:11:00.117+00'),
(47, 'IMP-20251212-4CT6V', 'en cours', 6, '[1,3,4,5,6]', '[{"etape":0,"nom":"Création du dossier","date_completion":"2025-12-12T14:58:41.810Z","donnees":{"numero_dossier":"IMP-20251212-4CT6V","statut":"en cours"}}]', 9, ' LOT-006', 'B3', 39, 'Dolore accusamus min', '2025-12-12 14:58:41.81+00', 'Sit sit aliquip plac', '2025-12-12 14:58:41.81+00', '2025-12-15 15:02:06.082+00')
ON CONFLICT (id) DO UPDATE SET
    statut = EXCLUDED.statut,
    etape_actuelle = EXCLUDED.etape_actuelle,
    updated_at = EXCLUDED.updated_at;

-- ============================================================================
-- PARTIE 3: IMPORT DES WORKFLOW_HISTORIQUES
-- ============================================================================

-- Tous les enregistrements de workflow_historiques du dump
INSERT INTO "public"."workflow_historiques" (id, impense_id, etape, phase, action, statut_avant, statut_apres, user_id, user_role, description, donnees_avant, donnees_apres, metadata, ip_address, user_agent, date_action, created_at, updated_at)
VALUES 
-- CREATION actions
(1, 34, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "À définir", "numero_dossier": "IMP-20251209-3JQXY"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 09:38:06.9+00', '2025-12-09 09:38:06.903+00', '2025-12-09 09:38:06.903+00'),
(2, 35, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 55, "statut": "en cours", "entreprise_id": 40, "nom_operateur": "Nouvelle entreprise 1", "numero_dossier": "IMP-20251209-6OE2A"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 09:58:00.499+00', '2025-12-09 09:58:00.5+00', '2025-12-09 09:58:00.5+00'),
(3, 36, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251209-3R3XG"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 10:09:19.704+00', '2025-12-09 10:09:19.705+00', '2025-12-09 10:09:19.705+00'),
(4, 37, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251209-Z1YI2"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 10:26:43.682+00', '2025-12-09 10:26:43.684+00', '2025-12-09 10:26:43.684+00'),
(5, 38, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251209-G8308"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 10:35:04.839+00', '2025-12-09 10:35:04.839+00', '2025-12-09 10:35:04.839+00'),
(6, 39, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 54, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251209-RZR87"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 10:38:59.629+00', '2025-12-09 10:38:59.631+00', '2025-12-09 10:38:59.631+00'),
(7, 40, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251209-TVWO8"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 10:52:09.554+00', '2025-12-09 10:52:09.555+00', '2025-12-09 10:52:09.555+00'),
(8, 41, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251209-6PWAZ"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 10:56:27.782+00', '2025-12-09 10:56:27.783+00', '2025-12-09 10:56:27.783+00'),
(9, 42, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251209-ZGGKI"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 11:18:27.446+00', '2025-12-09 11:18:27.447+00', '2025-12-09 11:18:27.447+00'),
(10, 43, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251209-YQDKJ"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 15:22:31.305+00', '2025-12-09 15:22:31.306+00', '2025-12-09 15:22:31.306+00'),
(11, 44, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251209-WS6RC"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0', '2025-12-09 15:25:22.694+00', '2025-12-09 15:25:22.695+00', '2025-12-09 15:25:22.695+00'),

-- VALIDATION actions for impense 44
(12, 44, 1, 1, 'VALIDATION', NULL, NULL, 1, 'admin', 'Validation de l''étape 1', NULL, '{"lot_id": 9, "entreprise_id": 39, "etape_actuelle": 1, "commentaires_DG": "ttreee test eeee"}', NULL, '127.0.0.1', 'Mozilla/5.0', '2025-12-09 15:26:00+00', '2025-12-09 15:26:00+00', '2025-12-09 15:26:00+00'),
(13, 44, 1, 1, 'VALIDATION', NULL, NULL, 1, 'admin', 'Validation de l''étape 1', NULL, '{"lot_id": 9, "entreprise_id": 39, "etape_actuelle": 1, "commentaires_DG": "ttreee test eeee", "commentaires_di": "mmppp"}', NULL, '127.0.0.1', 'Mozilla/5.0', '2025-12-09 15:27:00+00', '2025-12-09 15:27:00+00', '2025-12-09 15:27:00+00'),

-- Impense 45 workflow
(40, 45, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251211-BRJ69"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-11 13:49:11.198+00', '2025-12-11 13:49:11.198+00', '2025-12-11 13:49:11.198+00'),
(41, 45, 2, 1, 'SOUMISSION', NULL, NULL, 1, 'admin', 'Soumission de la demande par l''opérateur', NULL, NULL, '{"filesUploaded": 0, "numero_dossier": "IMP-20251211-BRJ69"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0', '2025-12-11 13:49:57.188+00', '2025-12-11 13:49:57.189+00', '2025-12-11 13:49:57.189+00'),

-- Impense 46 workflow
(42, 46, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251211-KE799"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-11 14:18:06.865+00', '2025-12-11 14:18:06.866+00', '2025-12-11 14:18:06.866+00'),
(43, 46, 1, 1, 'RETOUR', 'en cours', 'en cours', 1, 'admin', 'Dossier renvoyé pour complément. Commentaire DG: cccvvv', NULL, '{"lot_id": 9, "entreprise_id": 39, "etape_actuelle": 1, "commentaires_DG": "cccvvv"}', NULL, '127.0.0.1', 'Mozilla/5.0', '2025-12-11 14:20:00+00', '2025-12-11 14:20:00+00', '2025-12-11 14:20:00+00'),
(44, 46, 2, 1, 'SOUMISSION', NULL, NULL, 29, 'operateur', 'Soumission de la demande par l''opérateur', NULL, NULL, '{"filesUploaded": 0, "numero_dossier": "IMP-20251211-KE799"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-12-11 14:32:43.705+00', '2025-12-11 14:32:43.705+00', '2025-12-11 14:32:43.705+00'),
(51, 46, 2, 1, 'VALIDATION', 'en cours', 'en cours', 1, 'admin', 'Validation de la complétude du dossier par le Directeur Général', NULL, '{"lot_id": 9, "entreprise_id": 39}', NULL, '127.0.0.1', 'Mozilla/5.0', '2025-12-11 15:25:10+00', '2025-12-11 15:25:10+00', '2025-12-11 15:25:10+00'),
(52, 46, 3, 1, 'VALIDATION', 'en cours', 'en cours', 1, 'admin', 'Validation complète du dossier par DG et Direction Impenses. Passage à l''étape Recevabilité. Référence: REF-2025-0001, Code matrice: MAT-202512-0001', NULL, '{"lot_id": 9, "code_matrice": "MAT-202512-0001", "entreprise_id": 39}', NULL, '127.0.0.1', 'Mozilla/5.0', '2025-12-11 15:30:00+00', '2025-12-11 15:30:00+00', '2025-12-11 15:30:00+00'),
(72, 46, 3, 2, 'INVALIDATION_RECEVABILITE', 'invalide', 'invalide', 1, 'utilisateur', 'Recevabilité invalidée: cccccv fddd', '{"etape_avant": 3, "statut_recevabilite_avant": "invalide"}', '{"etape_nouvelle": 3, "statut_recevabilite": "invalide", "commentaire_invalidation_recevabilite": "cccccv fddd"}', '{"source": "phase2_recevabilite", "etape_nouvelle": 3, "numero_dossier": "IMP-20251211-KE799", "etape_precedente": 3}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0', '2025-12-11 17:50:00+00', '2025-12-11 17:50:00+00', '2025-12-11 17:50:00+00'),
(74, 46, 3, 2, 'VALIDATION_RECEVABILITE', 'valide', 'valide', 1, 'admin', 'Recevabilité validée - passage à l''étape 4', '{"etape_avant": 4, "statut_recevabilite_avant": "valide"}', '{"etape_nouvelle": 4, "statut_recevabilite": "valide"}', '{"source": "phase2_recevabilite", "etape_nouvelle": 4, "numero_dossier": "IMP-20251211-KE799", "etape_precedente": 4}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0', '2025-12-11 18:11:00.115+00', '2025-12-11 18:11:00.117+00', '2025-12-11 18:11:00.117+00'),

-- Impense 47 workflow
(75, 47, 1, 1, 'CREATION', NULL, 'en cours', 29, 'operateur', 'Création de la demande d''impense', NULL, '{"lot_id": 9, "statut": "en cours", "entreprise_id": 39, "nom_operateur": "Dolore accusamus min", "numero_dossier": "IMP-20251212-4CT6V"}', NULL, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2025-12-12 14:58:41.856+00', '2025-12-12 14:58:41.856+00', '2025-12-12 14:58:41.856+00'),
(76, 47, 2, 1, 'VALIDATION', 'en cours', 'en cours', 1, 'admin', 'Validation de la complétude du dossier par le Directeur Général', NULL, '{"lot_id": 9, "entreprise_id": 39}', NULL, '127.0.0.1', 'Mozilla/5.0', '2025-12-12 14:59:00+00', '2025-12-12 14:59:00+00', '2025-12-12 14:59:00+00'),
(77, 47, 3, 1, 'VALIDATION', 'en cours', 'en cours', 1, 'admin', 'Validation complète du dossier. Passage à l''étape Recevabilité. Référence: REF-2025-0002, Code matrice: MAT-202512-0002', NULL, '{"lot_id": 9, "code_matrice": "MAT-202512-0002", "entreprise_id": 39}', NULL, '127.0.0.1', 'Mozilla/5.0', '2025-12-12 15:00:00+00', '2025-12-12 15:00:00+00', '2025-12-12 15:00:00+00'),
(78, 47, 3, 2, 'UPLOAD_DOCUMENT', 'en_attente', 'en_attente', 1, 'admin', 'Document ajouté: modele-de-recu-de-paiement_x.png (matrice_impenses)', '{"etape_avant": 3, "statut_recevabilite_avant": "en_attente"}', '{"date_upload": "2025-12-12T15:00:41.713Z", "document_code": "matrice_impenses", "document_ajoute": "modele-de-recu-de-paiement_x.png", "document_taille": 63495}', '{"source": "phase2_recevabilite", "etape_nouvelle": 3, "numero_dossier": "IMP-20251212-4CT6V", "etape_precedente": 3}', '127.0.0.1', 'Mozilla/5.0', '2025-12-12 15:00:41+00', '2025-12-12 15:00:41+00', '2025-12-12 15:00:41+00'),
(79, 47, 3, 2, 'UPLOAD_DOCUMENT', 'en_attente', 'en_attente', 1, 'admin', 'Document ajouté: Invoice-7EFC90CF-0019.pdf (fiche_revue_exigences)', '{"etape_avant": 3, "statut_recevabilite_avant": "en_attente"}', '{"date_upload": "2025-12-12T15:00:56.017Z", "document_code": "fiche_revue_exigences", "document_ajoute": "Invoice-7EFC90CF-0019.pdf", "document_taille": 30478}', '{"source": "phase2_recevabilite", "etape_nouvelle": 3, "numero_dossier": "IMP-20251212-4CT6V", "etape_precedente": 3}', '127.0.0.1', 'Mozilla/5.0', '2025-12-12 15:00:56+00', '2025-12-12 15:00:56+00', '2025-12-12 15:00:56+00'),
(81, 47, 3, 2, 'INVALIDATION_RECEVABILITE', 'invalide', 'invalide', 1, 'admin', 'Recevabilité invalidée: zzzeea aaa', '{"etape_avant": 3, "statut_recevabilite_avant": "invalide"}', '{"etape_nouvelle": 3, "statut_recevabilite": "invalide", "commentaire_invalidation_recevabilite": "zzzeea aaa"}', '{"source": "phase2_recevabilite", "etape_nouvelle": 3, "numero_dossier": "IMP-20251212-4CT6V", "etape_precedente": 3}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0', '2025-12-12 15:01:30+00', '2025-12-12 15:01:30+00', '2025-12-12 15:01:30+00'),
(82, 47, 3, 2, 'VALIDATION_RECEVABILITE', 'valide', 'valide', 1, 'admin', 'Recevabilité validée - passage à l''étape 4', '{"etape_avant": 4, "statut_recevabilite_avant": "valide"}', '{"etape_nouvelle": 4, "statut_recevabilite": "valide"}', '{"source": "phase2_recevabilite", "etape_nouvelle": 4, "numero_dossier": "IMP-20251212-4CT6V", "etape_precedente": 4}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0', '2025-12-12 15:01:54.202+00', '2025-12-12 15:01:54.203+00', '2025-12-12 15:01:54.203+00'),
(90, 47, 6, 2, 'CREATION', NULL, NULL, 1, 'admin', 'Visite d''évaluation créée - Réf: VIS-IMP-2025-022-812431', NULL, '{"visite_zone": "Zone Industrielle de Vridi", "agents_visite": ["Pariatur Velit ali", "Laudantium ipsa et"], "visite_responsable": "Culpa ex iste corrup", "date_creation_visite": "2025-12-15T15:00:13.698Z", "entreprise_a_visiter": "Dolore accusamus min", "visite_evaluation_id": 27, "visite_evaluation_date": "2025-12-22"}', NULL, '127.0.0.1', 'Mozilla/5.0', '2025-12-15 15:00:13+00', '2025-12-15 15:00:13+00', '2025-12-15 15:00:13+00'),
(91, 47, 7, 2, 'CLOTURE', NULL, NULL, 1, 'admin', 'Visite d''évaluation clôturée - Réf: VIS-IMP-2025-022-812431', NULL, '{"date_cloture_visite": "2025-12-15T15:02:06.077Z", "visite_observations": "ggggff qqsaaza azaaa", "visite_evaluation_id": 27, "visite_pieces_jointes": ["modele-de-recu-de-paiement_x.png"], "visite_evaluation_statut": "Rapport validé", "visite_evaluation_reference": "VIS-IMP-2025-022-812431"}', '{"visite_id": 27, "observations": "ggggff qqsaaza azaaa"}', '127.0.0.1', 'Mozilla/5.0', '2025-12-15 15:02:06+00', '2025-12-15 15:02:06+00', '2025-12-15 15:02:06+00')
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- PARTIE 4: MISE À JOUR DE LA SÉQUENCE
-- ============================================================================

-- Réinitialiser les séquences auto-increment
SELECT setval('impenses_id_seq', COALESCE((SELECT MAX(id) FROM impenses), 1));
SELECT setval('workflow_historiques_id_seq', COALESCE((SELECT MAX(id) FROM workflow_historiques), 1));

-- ============================================================================
-- PARTIE 5: VÉRIFICATION FINALE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'ÉTAT APRÈS IMPORT:';
    RAISE NOTICE '========================================';
END $$;

SELECT 'Impenses après import:' as info, COUNT(*) as total FROM impenses;
SELECT 'Workflow_historiques après import:' as info, COUNT(*) as total FROM workflow_historiques;

-- Détails des impenses avec workflow
SELECT 
    i.id,
    i.numero_dossier,
    i.statut,
    i.etape_actuelle,
    COUNT(wh.id) as nb_workflow_actions
FROM impenses i
LEFT JOIN workflow_historiques wh ON i.id = wh.impense_id
WHERE i.id >= 34
GROUP BY i.id, i.numero_dossier, i.statut, i.etape_actuelle
ORDER BY i.id;

COMMIT;

-- ============================================================================
-- Message de fin
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'IMPORT TERMINÉ AVEC SUCCÈS!';
    RAISE NOTICE 'Exécutez maintenant: dbt run --select +mart_suivi_impenses';
    RAISE NOTICE '========================================';
END $$;
