DROP POLICY IF EXISTS project_invitations_select ON public.project_invitations;
CREATE POLICY project_invitations_select ON public.project_invitations
  FOR SELECT TO authenticated
  USING (
    invited_by = (SELECT auth.uid())
    OR private.can_manage_project(project_id, (SELECT auth.uid()))
    OR lower(email) = lower(((SELECT auth.jwt()) ->> 'email'))
  );