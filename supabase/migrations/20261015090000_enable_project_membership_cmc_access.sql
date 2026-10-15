-- Allow project sharing through project_memberships without recursive RLS.
-- The SECURITY DEFINER helpers are deliberately bound to auth.uid() so a caller
-- cannot ask about another user's membership by supplying an arbitrary user ID.

CREATE OR REPLACE FUNCTION private.has_project_role(
  p_project_id uuid,
  p_roles text[]
)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $function$
  SELECT EXISTS (
    SELECT 1
    FROM public.project_memberships AS pm
    WHERE pm.project_id = p_project_id
      AND pm.user_id = (SELECT auth.uid())
      AND pm.role = ANY(p_roles)
  );
$function$;

REVOKE ALL ON FUNCTION private.has_project_role(uuid, text[]) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION private.has_project_role(uuid, text[]) TO authenticated;

-- Project owners retain access; invited members can see only projects they join.
DROP POLICY IF EXISTS projects_select_own ON public.projects;
CREATE POLICY projects_select_own
ON public.projects
FOR SELECT
TO authenticated
USING (
  owner_id IS NULL
  OR owner_id = (SELECT auth.uid())
  OR private.has_project_role(id, ARRAY['owner','administrator','developer','researcher','operator','viewer']::text[])
);

-- CMC mission reads follow project membership; personal missions remain owner-only.
DROP POLICY IF EXISTS cmc_missions_select_own ON public.cmc_missions;
CREATE POLICY cmc_missions_select_own
ON public.cmc_missions
FOR SELECT
TO authenticated
USING (
  owner_id = (SELECT auth.uid())
  OR (
    project_id IS NOT NULL
    AND private.has_project_role(project_id, ARRAY['owner','administrator','developer','researcher','operator','viewer']::text[])
  )
);

-- New project missions must be owned by the caller and the caller must have a
-- role that can contribute to the project. Personal missions remain supported.
DROP POLICY IF EXISTS cmc_missions_insert_own ON public.cmc_missions;
CREATE POLICY cmc_missions_insert_own
ON public.cmc_missions
FOR INSERT
TO authenticated
WITH CHECK (
  owner_id = (SELECT auth.uid())
  AND (
    project_id IS NULL
    OR private.has_project_role(project_id, ARRAY['owner','administrator','developer','researcher','operator']::text[])
  )
);

-- Only project owners/admins/developers/operators may change shared missions.
DROP POLICY IF EXISTS cmc_missions_update_own ON public.cmc_missions;
CREATE POLICY cmc_missions_update_own
ON public.cmc_missions
FOR UPDATE
TO authenticated
USING (
  owner_id = (SELECT auth.uid())
  OR (
    project_id IS NOT NULL
    AND private.has_project_role(project_id, ARRAY['owner','administrator','developer','operator']::text[])
  )
)
WITH CHECK (
  owner_id = (SELECT auth.uid())
  OR (
    project_id IS NOT NULL
    AND private.has_project_role(project_id, ARRAY['owner','administrator','developer','operator']::text[])
  )
);

DROP POLICY IF EXISTS cmc_missions_delete_own ON public.cmc_missions;
CREATE POLICY cmc_missions_delete_own
ON public.cmc_missions
FOR DELETE
TO authenticated
USING (
  owner_id = (SELECT auth.uid())
  OR (
    project_id IS NOT NULL
    AND private.has_project_role(project_id, ARRAY['owner','administrator','developer','operator']::text[])
  )
);
