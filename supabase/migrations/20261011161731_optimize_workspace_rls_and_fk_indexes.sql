-- Keep auth lookups outside per-row policy helper execution and index the
-- foreign-key columns identified by the Supabase performance advisor.

CREATE OR REPLACE FUNCTION private.can_manage_project(p_project_id uuid, p_user_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $function$
  SELECT
    EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.id = p_project_id AND p.owner_id = p_user_id
    )
    OR EXISTS (
      SELECT 1 FROM public.project_memberships pm
      WHERE pm.project_id = p_project_id
        AND pm.user_id = p_user_id
        AND pm.role IN ('owner', 'administrator')
    );
$function$;

REVOKE ALL ON FUNCTION private.can_manage_project(uuid, uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION private.can_manage_project(uuid, uuid) TO authenticated;

CREATE INDEX IF NOT EXISTS cmc_commands_owner_id_idx
  ON public.cmc_commands(owner_id);
CREATE INDEX IF NOT EXISTS cmc_decisions_owner_id_idx
  ON public.cmc_decisions(owner_id);
CREATE INDEX IF NOT EXISTS cmc_events_owner_id_idx
  ON public.cmc_events(owner_id);
CREATE INDEX IF NOT EXISTS cmc_missions_owner_id_idx
  ON public.cmc_missions(owner_id);
CREATE INDEX IF NOT EXISTS cmc_resource_allocations_mission_id_idx
  ON public.cmc_resource_allocations(mission_id);
CREATE INDEX IF NOT EXISTS cmc_resource_allocations_owner_id_idx
  ON public.cmc_resource_allocations(owner_id);
CREATE INDEX IF NOT EXISTS local_agent_tasks_approved_by_idx
  ON public.local_agent_tasks(approved_by);
CREATE INDEX IF NOT EXISTS project_invitations_invited_by_idx
  ON public.project_invitations(invited_by);