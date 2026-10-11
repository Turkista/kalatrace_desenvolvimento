DROP POLICY IF EXISTS local_agent_instances_write ON public.local_agent_instances;
DROP POLICY IF EXISTS local_agent_instances_insert ON public.local_agent_instances;
DROP POLICY IF EXISTS local_agent_instances_update ON public.local_agent_instances;
CREATE POLICY local_agent_instances_insert ON public.local_agent_instances
  FOR INSERT TO authenticated WITH CHECK (owner_id = (SELECT auth.uid()));
CREATE POLICY local_agent_instances_update ON public.local_agent_instances
  FOR UPDATE TO authenticated
  USING (owner_id = (SELECT auth.uid()))
  WITH CHECK (owner_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS project_invitations_select ON public.project_invitations;
CREATE POLICY project_invitations_select ON public.project_invitations
  FOR SELECT TO authenticated
  USING (
    invited_by = (SELECT auth.uid())
    OR private.can_manage_project(project_id, (SELECT auth.uid()))
    OR lower(email) = (SELECT lower(auth.jwt()->>'email'))
  );