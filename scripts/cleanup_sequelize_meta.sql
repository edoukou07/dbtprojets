-- =====================================================================
-- Script de nettoyage du backup SIGETI
-- Supprime la table SequelizeMeta qui cause des erreurs d'import
-- =====================================================================

-- Cette table contient uniquement l'historique des migrations Sequelize
-- Elle n'est pas nécessaire pour le DWH

-- Si vous devez absolument l'importer, utilisez plutôt :
-- COPY public."SequelizeMeta" (name) FROM stdin WITH (FORMAT text);

-- Exécutez ce script AVANT d'importer le backup complet :
-- psql -U votre_user -d sigeti_node_db -f cleanup_sequelize_meta.sql

-- Ensuite, importez le backup en excluant cette table :
-- pg_restore --exclude-table="SequelizeMeta" -U votre_user -d sigeti_node_db backup.dump

-- OU utilisez le script PowerShell : .\scripts\import_source_db.ps1
