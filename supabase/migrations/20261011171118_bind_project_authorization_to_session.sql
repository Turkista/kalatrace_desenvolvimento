-- Keep the authorization helper bound to the current session identity.
CREATE OR REPLACE FUNCTION private.can_manage_project(p_project_id uuid, p_user_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $function$
  SELECT p_user_id = (SELECT auth.uid())
    AND (
      EXISTS (
        SELECT 1
        FROM public.projects AS p
        WHERE p.id = p_project_id
          AND p.owner_id = p_user_id
      )
      OR EXISTS (
        SELECT 1
        FROM public.project_memberships AS pm
        WHERE pm.project_id = p_project_id
          AND pm.user_id = p_user_id
          AND pm.role IN ('owner', 'administrator')
      )
    );
$function$;

REVOKE ALL ON FUNCTION private.can_manage_project(uuid, uuid) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION private.can_manage_project(uuid, uuid) TO authenticated;

-- The auth trigger uses fully qualified objects, so it does not need public on search_path.
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
BEGIN
  INSERT INTO public.profiles (id, display_name)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data ->> 'full_name', NEW.email)
  );
  RETURN NEW;
END;
$function$;

REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated;