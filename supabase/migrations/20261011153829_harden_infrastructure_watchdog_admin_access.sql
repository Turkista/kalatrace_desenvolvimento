-- Restrict infrastructure telemetry and watchdog mutations to an explicit admin allowlist.
-- The current project owner is seeded as the initial infrastructure admin.
-- This migration intentionally does not grant broad table UPDATE privileges to authenticated users.

CREATE SCHEMA IF NOT EXISTS private;

CREATE TABLE IF NOT EXISTS private.infrastructure_admins (
  user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT pg_catalog.now()
);

REVOKE ALL ON TABLE private.infrastructure_admins FROM PUBLIC, anon, authenticated;

INSERT INTO private.infrastructure_admins (user_id)
SELECT id
FROM auth.users
WHERE id = 'ebdbbfcf-9f0c-4083-bd8b-eb3cd9f85c4f'::uuid
ON CONFLICT (user_id) DO NOTHING;

CREATE OR REPLACE FUNCTION public.is_kalatrace_infrastructure_admin()
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $function$
  SELECT EXISTS (
    SELECT 1
    FROM private.infrastructure_admins AS admins
    WHERE admins.user_id = (SELECT auth.uid())
  );
$function$;

REVOKE ALL ON FUNCTION public.is_kalatrace_infrastructure_admin() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.is_kalatrace_infrastructure_admin() TO authenticated;

-- Infrastructure snapshots and events contain project-wide operational metadata.
DROP POLICY IF EXISTS "authenticated can read watchdog snapshots"
  ON public.infrastructure_usage_snapshots;
CREATE POLICY "infrastructure admins can read watchdog snapshots"
  ON public.infrastructure_usage_snapshots
  FOR SELECT TO authenticated
  USING ((SELECT public.is_kalatrace_infrastructure_admin()));

DROP POLICY IF EXISTS "authenticated can read watchdog events"
  ON public.infrastructure_watchdog_events;
CREATE POLICY "infrastructure admins can read watchdog events"
  ON public.infrastructure_watchdog_events
  FOR SELECT TO authenticated
  USING ((SELECT public.is_kalatrace_infrastructure_admin()));

DROP POLICY IF EXISTS "watchdog runtime checks select authenticated"
  ON public.infrastructure_watchdog_runtime_checks;
CREATE POLICY "infrastructure admins can read watchdog runtime checks"
  ON public.infrastructure_watchdog_runtime_checks
  FOR SELECT TO authenticated
  USING ((SELECT public.is_kalatrace_infrastructure_admin()));

DROP POLICY IF EXISTS "watchdog runtime checks insert authenticated"
  ON public.infrastructure_watchdog_runtime_checks;
CREATE POLICY "infrastructure admins can insert watchdog runtime checks"
  ON public.infrastructure_watchdog_runtime_checks
  FOR INSERT TO authenticated
  WITH CHECK (
    (SELECT public.is_kalatrace_infrastructure_admin())
    AND created_by = (SELECT auth.uid())
  );

-- SECURITY DEFINER wrappers are safe here only because every entry point checks the
-- explicit administrator allowlist and fixes search_path to the empty path.
CREATE OR REPLACE FUNCTION public.get_kalatrace_infrastructure_usage()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
BEGIN
  IF NOT (SELECT public.is_kalatrace_infrastructure_admin()) THEN
    RAISE EXCEPTION 'Infrastructure administrator access required'
      USING ERRCODE = '42501';
  END IF;

  RETURN private.collect_kalatrace_infrastructure_usage();
END;
$function$;

REVOKE ALL ON FUNCTION public.get_kalatrace_infrastructure_usage() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.get_kalatrace_infrastructure_usage() TO authenticated;

CREATE OR REPLACE FUNCTION public.run_kalatrace_watchdog()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
BEGIN
  IF NOT (SELECT public.is_kalatrace_infrastructure_admin()) THEN
    RAISE EXCEPTION 'Infrastructure administrator access required'
      USING ERRCODE = '42501';
  END IF;

  RETURN private.run_kalatrace_watchdog();
END;
$function$;

REVOKE ALL ON FUNCTION public.run_kalatrace_watchdog() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.run_kalatrace_watchdog() TO authenticated;

CREATE OR REPLACE FUNCTION public.record_kalatrace_watchdog_runtime(
  p_snapshot_id bigint,
  p_persistence_status text,
  p_graph_status text,
  p_details jsonb DEFAULT '{}'::jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
  runtime_user uuid;
  new_status text;
  score integer;
BEGIN
  runtime_user := (SELECT auth.uid());

  IF runtime_user IS NULL THEN
    RAISE EXCEPTION 'Authentication required' USING ERRCODE = '28000';
  END IF;

  IF NOT (SELECT public.is_kalatrace_infrastructure_admin()) THEN
    RAISE EXCEPTION 'Infrastructure administrator access required'
      USING ERRCODE = '42501';
  END IF;

  IF p_persistence_status IS NULL
     OR p_persistence_status NOT IN ('HEALTHY', 'WARNING', 'CRITICAL') THEN
    RAISE EXCEPTION 'Invalid persistence status' USING ERRCODE = '22023';
  END IF;

  IF p_graph_status IS NULL
     OR p_graph_status NOT IN ('HEALTHY', 'WARNING', 'CRITICAL') THEN
    RAISE EXCEPTION 'Invalid graph status' USING ERRCODE = '22023';
  END IF;

  PERFORM 1
  FROM public.infrastructure_usage_snapshots
  WHERE id = p_snapshot_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Infrastructure snapshot not found'
      USING ERRCODE = 'P0002';
  END IF;

  UPDATE public.infrastructure_usage_snapshots
  SET
    persistence_health = p_persistence_status,
    graph_health = p_graph_status,
    integrity_issues = COALESCE(integrity_issues, '{}'::jsonb)
      || COALESCE(p_details, '{}'::jsonb),
    evaluation = COALESCE(evaluation, '{}'::jsonb) || jsonb_build_object(
      'runtime_persistence_health', p_persistence_status,
      'runtime_graph_health', p_graph_status,
      'runtime_checked_at', pg_catalog.now()
    )
  WHERE id = p_snapshot_id;

  INSERT INTO public.infrastructure_watchdog_runtime_checks
    (snapshot_id, check_type, status, duration_ms, details, created_by)
  VALUES
    (
      p_snapshot_id,
      'KEE_RECOVERY',
      p_persistence_status,
      NULL,
      COALESCE(p_details->'persistence_recovery', '{}'::jsonb),
      runtime_user
    ),
    (
      p_snapshot_id,
      'NEO4J_GRAPH',
      p_graph_status,
      NULL,
      COALESCE(p_details->'neo4j', '{}'::jsonb),
      runtime_user
    );

  SELECT GREATEST(0, LEAST(100,
    100
    - CASE WHEN database_status = 'CRITICAL' THEN 40 WHEN database_status = 'WARNING' THEN 15 ELSE 0 END
    - CASE WHEN storage_status = 'CRITICAL' THEN 40 WHEN storage_status = 'WARNING' THEN 15 ELSE 0 END
    - CASE WHEN epistemic_health = 'WARNING' THEN 15 ELSE 0 END
    - CASE WHEN p_persistence_status = 'CRITICAL' THEN 25 WHEN p_persistence_status = 'WARNING' THEN 10 ELSE 0 END
    - CASE WHEN p_graph_status = 'CRITICAL' THEN 25 WHEN p_graph_status = 'WARNING' THEN 10 ELSE 0 END
  ))
  INTO score
  FROM public.infrastructure_usage_snapshots
  WHERE id = p_snapshot_id;

  new_status := CASE
    WHEN p_persistence_status = 'CRITICAL' OR p_graph_status = 'CRITICAL' THEN 'CRITICAL'
    WHEN p_persistence_status = 'WARNING' OR p_graph_status = 'WARNING' THEN 'WARNING'
    ELSE 'HEALTHY'
  END;

  UPDATE public.infrastructure_usage_snapshots
  SET
    health_score = LEAST(health_score, score),
    overall_status = CASE
      WHEN overall_status = 'CRITICAL' OR new_status = 'CRITICAL' THEN 'CRITICAL'
      WHEN overall_status = 'WARNING' OR new_status = 'WARNING' THEN 'WARNING'
      ELSE 'HEALTHY'
    END
  WHERE id = p_snapshot_id;

  PERFORM private.sync_kalatrace_watchdog_events(p_snapshot_id);

  RETURN (
    SELECT jsonb_build_object(
      'snapshot_id', id,
      'status', overall_status,
      'health_score', health_score,
      'persistence_health', persistence_health,
      'graph_health', graph_health,
      'details', integrity_issues
    )
    FROM public.infrastructure_usage_snapshots
    WHERE id = p_snapshot_id
  );
END;
$function$;

REVOKE ALL ON FUNCTION public.record_kalatrace_watchdog_runtime(bigint, text, text, jsonb)
  FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.record_kalatrace_watchdog_runtime(bigint, text, text, jsonb)
  TO authenticated;
