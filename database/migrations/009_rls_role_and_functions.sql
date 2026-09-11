-- ============================================================================
-- CodeAcademy Pro — RLS Foundation: Role & Helper Functions
-- Must run AFTER all schema migrations (001–008).
-- ============================================================================

-- 1. Create application role (idempotent)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'academy_app') THEN
        CREATE ROLE academy_app LOGIN PASSWORD 'academy_app_secure_pwd'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
        RAISE NOTICE 'Created role academy_app';
    END IF;
END $$;

-- 2. Grant schema and table privileges to academy_app
GRANT USAGE ON SCHEMA public TO academy_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO academy_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO academy_app;

-- Grant sequence usage (for any serial/identity columns or gen_random_uuid)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO academy_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO academy_app;

-- 3. Helper functions for RLS policies
-- These read transaction-local variables set by the application via SET LOCAL.

CREATE OR REPLACE FUNCTION app_user_id() RETURNS UUID AS $$
    SELECT NULLIF(current_setting('app.current_user_id', true), '')::UUID;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION app_user_role() RETURNS TEXT AS $$
    SELECT COALESCE(NULLIF(current_setting('app.current_user_role', true), ''), '');
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION is_admin() RETURNS BOOLEAN AS $$
    SELECT app_user_role() = 'admin';
$$ LANGUAGE sql STABLE;

-- Allow academy_app to execute these functions
GRANT EXECUTE ON FUNCTION app_user_id() TO academy_app;
GRANT EXECUTE ON FUNCTION app_user_role() TO academy_app;
GRANT EXECUTE ON FUNCTION is_admin() TO academy_app;

-- Allow academy_app to use SET LOCAL for app.* variables
-- (GUC custom variables are allowed by default for any role)
