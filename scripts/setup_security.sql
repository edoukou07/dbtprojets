-- =====================================================================
-- SÉCURITÉ AU NIVEAU DES LIGNES (RLS)
-- Restreint l'accès aux données selon les rôles utilisateurs
-- =====================================================================

-- 1. Créer des rôles utilisateurs
CREATE ROLE dwh_analyst;
CREATE ROLE dwh_manager;
CREATE ROLE dwh_admin;

-- 2. Politique RLS pour fait_attributions
-- Les analystes ne voient que les données publiques
ALTER TABLE dwh_facts.fait_attributions ENABLE ROW LEVEL SECURITY;

CREATE POLICY analyst_view ON dwh_facts.fait_attributions
    FOR SELECT
    TO dwh_analyst
    USING (statut IN ('approuve', 'attribue'));

-- Les managers voient toutes les données sauf brouillons
CREATE POLICY manager_view ON dwh_facts.fait_attributions
    FOR SELECT
    TO dwh_manager
    USING (statut != 'brouillon');

-- Les admins voient tout
CREATE POLICY admin_view ON dwh_facts.fait_attributions
    FOR ALL
    TO dwh_admin
    USING (true);

-- 3. Permissions sur les schémas
GRANT USAGE ON SCHEMA dwh_staging TO dwh_analyst, dwh_manager, dwh_admin;
GRANT USAGE ON SCHEMA dwh_dimensions TO dwh_analyst, dwh_manager, dwh_admin;
GRANT USAGE ON SCHEMA dwh_facts TO dwh_analyst, dwh_manager, dwh_admin;
GRANT USAGE ON SCHEMA dwh_marts_clients TO dwh_analyst, dwh_manager, dwh_admin;
GRANT USAGE ON SCHEMA dwh_marts_financier TO dwh_manager, dwh_admin;
GRANT USAGE ON SCHEMA dwh_marts_operationnel TO dwh_manager, dwh_admin;

-- 4. Permissions en lecture seule pour analystes
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_staging TO dwh_analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_dimensions TO dwh_analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_facts TO dwh_analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_marts_clients TO dwh_analyst;

-- 5. Permissions complètes pour managers
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_staging TO dwh_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_dimensions TO dwh_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_facts TO dwh_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_marts_clients TO dwh_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_marts_financier TO dwh_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh_marts_operationnel TO dwh_manager;

-- 6. Permissions totales pour admins
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dwh_staging TO dwh_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dwh_dimensions TO dwh_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dwh_facts TO dwh_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dwh_marts_clients TO dwh_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dwh_marts_financier TO dwh_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dwh_marts_operationnel TO dwh_admin;

-- 7. Créer des utilisateurs exemples
-- CREATE USER analyst_user WITH PASSWORD 'secure_password' IN ROLE dwh_analyst;
-- CREATE USER manager_user WITH PASSWORD 'secure_password' IN ROLE dwh_manager;
-- CREATE USER admin_user WITH PASSWORD 'secure_password' IN ROLE dwh_admin;

-- 8. Audit des accès
CREATE TABLE IF NOT EXISTS dwh.audit_log (
    audit_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100),
    schema_name VARCHAR(100),
    table_name VARCHAR(100),
    action VARCHAR(50),
    query_text TEXT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fonction trigger pour auditer les SELECT
CREATE OR REPLACE FUNCTION dwh.audit_select()
RETURNS event_trigger AS $$
BEGIN
    -- Log les requêtes sensibles
    INSERT INTO dwh.audit_log (user_name, query_text)
    VALUES (current_user, current_query());
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE dwh.audit_log IS 'Journalisation des accès aux données sensibles';
