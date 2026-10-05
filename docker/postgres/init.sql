-- PostgreSQL initialization script
-- Runs once when the container is first created

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- trigram for fuzzy search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- GIN index support

-- Create a dedicated schema for future multi-tenant support
-- All application tables will live in the public schema for now
COMMENT ON SCHEMA public IS 'Grocery POS main application schema';
