-- =============================================================================
-- Supabase Row Level Security (RLS) lockdown for SymptomAI
-- =============================================================================
-- Purpose: clear the Supabase advisor warning "RLS not enabled on public
-- tables" by enabling RLS on every table in the public schema and denying all
-- access through the Supabase REST API (PostgREST).
--
-- Why this does NOT affect the app:
--   * Django connects via DATABASE_URL as the `postgres` role, which OWNS these
--     tables. With plain ENABLE (not FORCE) ROW LEVEL SECURITY, the table owner
--     bypasses RLS, so Django keeps full read/write access.
--   * The deny policy is scoped to `anon` and `authenticated` -- the roles the
--     Supabase REST API uses via the anon/public API keys. The app never uses
--     those roles (it talks to PostgreSQL directly via psycopg2), so the REST
--     API is locked down while Django is untouched.
--   * IMPORTANT: use ENABLE, never FORCE. FORCE would apply RLS to the owner
--     too and would break Django.
--
-- Run manually in the Supabase SQL Editor. Idempotent (safe to re-run).
-- =============================================================================


-- 1. Enable RLS + add a deny-all REST policy on EVERY public table -------------
--    Covers the Django tables not listed individually below (auth_group,
--    auth_permission, auth_group_permissions, auth_user_groups,
--    auth_user_user_permissions, django_admin_log, django_content_type, ...).
DO $$
DECLARE
  t record;
BEGIN
  FOR t IN
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  LOOP
    -- ENABLE (not FORCE) so the table owner / Django's connection bypasses RLS.
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', t.tablename);

    -- Idempotent: drop then recreate the deny-all policy.
    EXECUTE format('DROP POLICY IF EXISTS deny_all_rest ON public.%I;', t.tablename);

    -- RESTRICTIVE + USING(false)/WITH CHECK(false) = no SELECT/INSERT/UPDATE/
    -- DELETE for the REST API roles, even if a permissive policy is added later.
    EXECUTE format(
      'CREATE POLICY deny_all_rest ON public.%I '
      'AS RESTRICTIVE TO anon, authenticated '
      'USING (false) WITH CHECK (false);',
      t.tablename
    );
  END LOOP;
END $$;


-- 2. Explicit equivalent for the core tables (for reference / transparency) ----
--    The block above already covers these; kept here to document intent.

-- Enable RLS (owner / Django connection still bypasses it).
ALTER TABLE public.checker_symptomcheck ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback_feedback    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth_user            ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.django_session       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.django_migrations    ENABLE ROW LEVEL SECURITY;

-- Deny ALL access via the REST API (anon + authenticated roles).
DROP POLICY IF EXISTS deny_all_rest ON public.checker_symptomcheck;
CREATE POLICY deny_all_rest ON public.checker_symptomcheck
  AS RESTRICTIVE TO anon, authenticated USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS deny_all_rest ON public.feedback_feedback;
CREATE POLICY deny_all_rest ON public.feedback_feedback
  AS RESTRICTIVE TO anon, authenticated USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS deny_all_rest ON public.auth_user;
CREATE POLICY deny_all_rest ON public.auth_user
  AS RESTRICTIVE TO anon, authenticated USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS deny_all_rest ON public.django_session;
CREATE POLICY deny_all_rest ON public.django_session
  AS RESTRICTIVE TO anon, authenticated USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS deny_all_rest ON public.django_migrations;
CREATE POLICY deny_all_rest ON public.django_migrations
  AS RESTRICTIVE TO anon, authenticated USING (false) WITH CHECK (false);


-- 3. Verification --------------------------------------------------------------

-- All public tables should show rowsecurity = true.
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- The deny policy should exist on each table.
SELECT tablename, policyname, permissive, roles, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename;

-- Owner should be `postgres` (the role in DATABASE_URL) so the owner bypasses
-- RLS and Django keeps full access. If the owner differs from the role Django
-- connects as, ENABLE could block Django -- not the standard Supabase setup.
SELECT tablename, tableowner
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
