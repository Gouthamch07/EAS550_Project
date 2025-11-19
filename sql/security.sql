-- ============================================================================
-- PHASE 1 (BONUS): SECURITY SETUP (RBAC)
-- Global Food & Nutrition Explorer
-- ============================================================================

-- Best practice: Revoke default public privileges to ensure a secure-by-default setup
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE food_nutrition_db FROM PUBLIC;

-- ============================================================================
-- ROLE 1: read_only_analyst
-- For users/services that only need to read data (e.g., analytics, dashboards)
-- ============================================================================
CREATE ROLE read_only_analyst;

-- Grant basic connection and schema usage rights
GRANT CONNECT ON DATABASE food_nutrition_db TO read_only_analyst;
GRANT USAGE ON SCHEMA public TO read_only_analyst;

-- Grant SELECT (read) permissions on all current tables in the schema
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only_analyst;

-- IMPORTANT: Grant SELECT permissions on any FUTURE tables created in the schema
-- This ensures the role doesn't break if you add new tables later
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO read_only_analyst;

COMMENT ON ROLE read_only_analyst IS 'Role for read-only access to all tables for analytics and reporting.';


-- ============================================================================
-- ROLE 2: app_user
-- For the application itself to perform CRUD operations
-- ============================================================================
CREATE ROLE app_user;

-- Grant basic connection and schema usage rights
GRANT CONNECT ON DATABASE food_nutrition_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;

-- Grant CRUD (Create, Read, Update, Delete) permissions on all current tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Grant USAGE on all sequences (required for INSERTs on tables with SERIAL primary keys)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- IMPORTANT: Grant CRUD permissions on any FUTURE tables and sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO app_user;

COMMENT ON ROLE app_user IS 'Role for the application to perform all CRUD operations.';


-- ============================================================================
-- CREATE USERS AND ASSIGN ROLES
-- In a real-world scenario, use more secure, generated passwords.
-- ============================================================================

-- Create a user for an analyst and assign the read-only role
CREATE USER analyst_user WITH PASSWORD 'analyst_password';
GRANT read_only_analyst TO analyst_user;

-- Create a user for the application and assign the read-write role
CREATE USER app_service_user WITH PASSWORD 'app_password';
GRANT app_user TO app_service_user;

-- ============================================================================
-- END OF SECURITY SCRIPT
-- ============================================================================