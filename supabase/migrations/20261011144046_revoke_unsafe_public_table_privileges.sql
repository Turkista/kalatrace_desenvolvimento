-- KALATRACE security hardening.
-- Applied to Supabase project kedyzontvnailtwpacvz as migration
-- 20261011144046_revoke_unsafe_public_table_privileges.
-- RLS does not protect TRUNCATE, so API roles must not have that privilege.

REVOKE TRUNCATE, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA public FROM anon, authenticated;
REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM anon;

-- Prevent the postgres role's future public tables from inheriting unsafe API grants.
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE DELETE ON TABLES FROM anon;
