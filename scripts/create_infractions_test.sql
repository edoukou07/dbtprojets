-- Script de création de données de test pour infractions
-- À exécuter une seule fois

INSERT INTO public.infractions (
    id,
    zone_id,
    type_infraction,
    gravite,
    date_detection,
    date_resolution,
    est_resolue,
    jours_resolution,
    description,
    severite_score,
    convention_id,
    infraction_id
) VALUES
    (1, 1, 'Non-conformité Structure', 'mineure', '2025-01-15', '2025-01-20', TRUE, 5, 'Toit endommagé', 1, NULL, 1),
    (2, 1, 'Pollution Eau', 'moderee', '2025-02-10', '2025-02-28', TRUE, 18, 'Déversement accidentel', 2, NULL, 2),
    (3, 2, 'Déchet Dangereux', 'majeure', '2025-03-05', NULL, FALSE, NULL, 'Gestion inadéquate', 3, NULL, 3),
    (4, 2, 'Violation Permis', 'critique', '2025-01-01', '2025-01-10', TRUE, 9, 'Opération hors licence', 4, NULL, 4),
    (5, 3, 'Non-conformité Structure', 'mineure', '2025-03-20', '2025-03-22', TRUE, 2, 'Signalétique manquante', 1, NULL, 5),
    (6, 3, 'Pollution Air', 'moderee', '2025-02-15', '2025-03-15', TRUE, 28, 'Émissions excessives', 2, NULL, 6),
    (7, 1, 'Violation Permis', 'majeure', '2025-03-01', NULL, FALSE, NULL, 'Extension non autorisée', 3, NULL, 7),
    (8, 4, 'Déchet Dangereux', 'critique', '2025-01-25', '2025-02-08', TRUE, 14, 'Stockage illégal', 4, NULL, 8),
    (9, 4, 'Pollution Eau', 'mineure', '2025-02-20', '2025-02-25', TRUE, 5, 'Petit déversement', 1, NULL, 9),
    (10, 5, 'Non-conformité Structure', 'moderee', '2025-03-10', '2025-03-25', TRUE, 15, 'Maintenance insuffisante', 2, NULL, 10),
    (11, 5, 'Violation Permis', 'mineure', '2025-01-30', '2025-02-05', TRUE, 6, 'Horaires non respectés', 1, NULL, 11),
    (12, 1, 'Pollution Air', 'majeure', '2025-02-01', NULL, FALSE, NULL, 'Fumées excessives', 3, NULL, 12),
    (13, 2, 'Non-conformité Structure', 'critique', '2024-12-20', '2025-01-15', TRUE, 26, 'Danger structural', 4, NULL, 13),
    (14, 3, 'Déchet Dangereux', 'moderee', '2025-01-10', '2025-02-01', TRUE, 22, 'Classification incorrecte', 2, NULL, 14),
    (15, 4, 'Violation Permis', 'mineure', '2025-03-15', '2025-03-18', TRUE, 3, 'Petit dépassement', 1, NULL, 15),
    (16, 5, 'Pollution Eau', 'majeure', '2025-02-05', NULL, FALSE, NULL, 'Contamination', 3, NULL, 16),
    (17, 1, 'Déchet Dangereux', 'mineure', '2025-03-08', '2025-03-10', TRUE, 2, 'Petit déversement', 1, NULL, 17),
    (18, 2, 'Violation Permis', 'moderee', '2025-01-20', '2025-02-10', TRUE, 21, 'Zone restreinte', 2, NULL, 18),
    (19, 3, 'Pollution Air', 'mineure', '2025-03-18', '2025-03-20', TRUE, 2, 'Fumée léger', 1, NULL, 19),
    (20, 4, 'Non-conformité Structure', 'majeure', '2025-02-28', NULL, FALSE, NULL, 'Murs fissurés', 3, NULL, 20);
