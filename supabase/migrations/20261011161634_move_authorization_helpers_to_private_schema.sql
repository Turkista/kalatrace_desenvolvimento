-- Move authorization-only helpers out of the exposed public API schema and
-- remove accidental direct execution grants from private implementation functions.

CREATE OR REPLACE FUNCTION private.can_manage_project(p_project_id uuid, p_user_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $function$
  SELECT p_user_id = (SELECT auth.uid()) AND (
    EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.id = p_project_id AND p.owner_id = p_user_id
    )
    OR EXISTS (
      SELECT 1 FROM public.project_memberships pm
      WHERE pm.project_id = p_project_id
        AND pm.user_id = p_user_id
        AND pm.role IN ('owner', 'administrator')
    )
  );
$function$;

CREATE OR REPLACE FUNCTION private.is_kalatrace_infrastructure_admin()
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

REVOKE ALL ON SCHEMA private FROM PUBLIC, anon;
GRANT USAGE ON SCHEMA private TO authenticated;

REVOKE ALL ON FUNCTION private.collect_kalatrace_infrastructure_usage() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION private.run_kalatrace_watchdog() FROM PUBLIC, anon, authenticated;
DO $migration$
BEGIN
  IF pg_catalog.to_regprocedure('private.run_kalatrace_watchdog_legacy()') IS NOT NULL THEN
    EXECUTE 'REVOKE ALL ON FUNCTION private.run_kalatrace_watchdog_legacy() FROM PUBLIC, anon, authenticated';
  END IF;
END;
$migration$;
REVOKE ALL ON FUNCTION private.sync_kalatrace_watchdog_events(bigint) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION private.can_manage_project(uuid, uuid) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION private.is_kalatrace_infrastructure_admin() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION private.can_manage_project(uuid, uuid) TO authenticated;
GRANT EXECUTE ON FUNCTION private.is_kalatrace_infrastructure_admin() TO authenticated;

DROP POLICY IF EXISTS "infrastructure admins can read watchdog snapshots" ON public.infrastructure_usage_snapshots;
CREATE POLICY "infrastructure admins can read watchdog snapshots"
  ON public.infrastructure_usage_snapshots FOR SELECT TO authenticated
  USING ((SELECT private.is_kalatrace_infrastructure_admin()));

DROP POLICY IF EXISTS "infrastructure admins can read watchdog events" ON public.infrastructure_watchdog_events;
CREATE POLICY "infrastructure admins can read watchdog events"
  ON public.infrastructure_watchdog_events FOR SELECT TO authenticated
  USING ((SELECT private.is_kalatrace_infrastructure_admin()));

DROP POLICY IF EXISTS "infrastructure admins can read watchdog runtime checks" ON public.infrastructure_watchdog_runtime_checks;
CREATE POLICY "infrastructure admins can read watchdog runtime checks"
  ON public.infrastructure_watchdog_runtime_checks FOR SELECT TO authenticated
  USING ((SELECT private.is_kalatrace_infrastructure_admin()));

DROP POLICY IF EXISTS "infrastructure admins can insert watchdog runtime checks" ON public.infrastructure_watchdog_runtime_checks;
CREATE POLICY "infrastructure admins can insert watchdog runtime checks"
  ON public.infrastructure_watchdog_runtime_checks FOR INSERT TO authenticated
  WITH CHECK (
    (SELECT private.is_kalatrace_infrastructure_admin())
    AND created_by = (SELECT auth.uid())
  );

DROP POLICY IF EXISTS project_memberships_select_own ON public.project_memberships;
CREATE POLICY project_memberships_select_own ON public.project_memberships
  FOR SELECT TO authenticated
  USING (user_id = (SELECT auth.uid()) OR private.can_manage_project(project_id, (SELECT auth.uid())));

DROP POLICY IF EXISTS project_memberships_update_managed ON public.project_memberships;
CREATE POLICY project_memberships_update_managed ON public.project_memberships
  FOR UPDATE TO authenticated
  USING (private.can_manage_project(project_id, (SELECT auth.uid())))
  WITH CHECK (
    private.can_manage_project(project_id, (SELECT auth.uid()))
    AND role IN ('administrator','developer','researcher','operator','viewer')
  );

DROP POLICY IF EXISTS project_memberships_delete_managed ON public.project_memberships;
CREATE POLICY project_memberships_delete_managed ON public.project_memberships
  FOR DELETE TO authenticated
  USING (
    private.can_manage_project(project_id, (SELECT auth.uid()))
    AND NOT EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.id = project_memberships.project_id
        AND p.owner_id = project_memberships.user_id
    )
  );

DROP POLICY IF EXISTS project_invitations_select ON public.project_invitations;
CREATE POLICY project_invitations_select ON public.project_invitations
  FOR SELECT TO authenticated
  USING (
    invited_by = (SELECT auth.uid())
    OR private.can_manage_project(project_id, (SELECT auth.uid()))
    OR lower(email) = lower((SELECT auth.jwt()->>'email'))
  );

DROP POLICY IF EXISTS project_invitations_insert ON public.project_invitations;
CREATE POLICY project_invitations_insert ON public.project_invitations
  FOR INSERT TO authenticated
  WITH CHECK (
    private.can_manage_project(project_id, (SELECT auth.uid()))
    AND invited_by = (SELECT auth.uid())
  );

DROP POLICY IF EXISTS project_invitations_update ON public.project_invitations;
CREATE POLICY project_invitations_update ON public.project_invitations
  FOR UPDATE TO authenticated
  USING (private.can_manage_project(project_id, (SELECT auth.uid())))
  WITH CHECK (private.can_manage_project(project_id, (SELECT auth.uid())));

CREATE OR REPLACE FUNCTION public.get_kalatrace_infrastructure_usage()
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
BEGIN
  IF NOT (SELECT private.is_kalatrace_infrastructure_admin()) THEN
    RAISE EXCEPTION 'Infrastructure administrator access required'
      USING ERRCODE = '42501';
  END IF;
  RETURN private.collect_kalatrace_infrastructure_usage();
END;
$function$;

CREATE OR REPLACE FUNCTION public.run_kalatrace_watchdog()
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
BEGIN
  IF NOT (SELECT private.is_kalatrace_infrastructure_admin()) THEN
    RAISE EXCEPTION 'Infrastructure administrator access required'
      USING ERRCODE = '42501';
  END IF;
  RETURN private.run_kalatrace_watchdog();
END;
$function$;

CREATE OR REPLACE FUNCTION public.record_kalatrace_watchdog_runtime(p_snapshot_id bigint, p_persistence_status text, p_graph_status text, p_details jsonb DEFAULT '{}'::jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
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
  IF NOT (SELECT private.is_kalatrace_infrastructure_admin()) THEN
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

  PERFORM 1 FROM public.infrastructure_usage_snapshots WHERE id = p_snapshot_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Infrastructure snapshot not found' USING ERRCODE = 'P0002';
  END IF;

  UPDATE public.infrastructure_usage_snapshots
  SET
    persistence_health = p_persistence_status,
    graph_health = p_graph_status,
    integrity_issues = COALESCE(integrity_issues, '{}'::jsonb) || COALESCE(p_details, '{}'::jsonb),
    evaluation = COALESCE(evaluation, '{}'::jsonb) || jsonb_build_object(
      'runtime_persistence_health', p_persistence_status,
      'runtime_graph_health', p_graph_status,
      'runtime_checked_at', pg_catalog.now()
    )
  WHERE id = p_snapshot_id;

  INSERT INTO public.infrastructure_watchdog_runtime_checks
    (snapshot_id, check_type, status, duration_ms, details, created_by)
  VALUES
    (p_snapshot_id, 'KEE_RECOVERY', p_persistence_status, NULL,
      COALESCE(p_details->'persistence_recovery', '{}'::jsonb), runtime_user),
    (p_snapshot_id, 'NEO4J_GRAPH', p_graph_status, NULL,
      COALESCE(p_details->'neo4j', '{}'::jsonb), runtime_user);

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

CREATE OR REPLACE FUNCTION public.update_project_member_role(p_project_id uuid, p_user_id uuid, p_role text)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
declare v_row jsonb;
begin
  if not private.can_manage_project(p_project_id, (select auth.uid())) then
    raise exception 'Not authorized to manage project members';
  end if;
  if p_role is null or p_role not in ('administrator','developer','researcher','operator','viewer') then
    raise exception 'Invalid project role';
  end if;
  IF EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.id = p_project_id AND p.owner_id = p_user_id
  ) THEN
    RAISE EXCEPTION 'Project owner role cannot be changed through membership manager';
  END IF;

  UPDATE public.project_memberships AS pm
  SET role = p_role, updated_at = pg_catalog.now()
  WHERE pm.project_id = p_project_id AND pm.user_id = p_user_id
  RETURNING to_jsonb(pm.*) INTO v_row;
  if v_row is null then raise exception 'Project member not found'; end if;
  return v_row;
end;
$function$;

REVOKE ALL ON FUNCTION public.can_manage_project(uuid, uuid) FROM PUBLIC, anon, authenticated;
DROP FUNCTION IF EXISTS public.can_manage_project(uuid, uuid);
REVOKE ALL ON FUNCTION public.is_kalatrace_infrastructure_admin() FROM PUBLIC, anon, authenticated;
DROP FUNCTION IF EXISTS public.is_kalatrace_infrastructure_admin();
