-- Workspace administration: role changes and member removal are restricted by
-- project owner/administrator RLS. A member cannot elevate its own role.
drop policy if exists project_memberships_update_own on public.project_memberships;
drop policy if exists project_memberships_update_managed on public.project_memberships;
create policy project_memberships_update_managed on public.project_memberships for update to authenticated
using (public.can_manage_project(project_id,(select auth.uid())))
with check (
  public.can_manage_project(project_id,(select auth.uid()))
  and role in ('administrator','developer','researcher','operator','viewer')
);

create or replace function public.update_project_member_role(
  p_project_id uuid,
  p_user_id uuid,
  p_role text
)
returns jsonb
language plpgsql
security definer
set search_path=''
as $$
declare v_row jsonb;
begin
  if not public.can_manage_project(p_project_id, (select auth.uid())) then
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
$$;
revoke all on function public.update_project_member_role(uuid,uuid,text) from public, anon, authenticated;
grant execute on function public.update_project_member_role(uuid,uuid,text) to authenticated;

-- Role changes must pass through the authorization-checked RPC, not direct PATCH.
REVOKE UPDATE ON TABLE public.project_memberships FROM PUBLIC, anon, authenticated;
REVOKE UPDATE (id, project_id, user_id, role, permissions, created_at, updated_at)
  ON TABLE public.project_memberships FROM PUBLIC, anon, authenticated;

-- Project edits may change business fields, never the owner, slug, or immutable IDs.
REVOKE UPDATE ON TABLE public.projects FROM PUBLIC, anon, authenticated;
REVOKE UPDATE (id, owner_id, slug, name, project_type, domain, description, status, metadata, created_at, updated_at)
  ON TABLE public.projects FROM PUBLIC, anon, authenticated;
GRANT UPDATE (name, project_type, domain, description, status, metadata)
  ON TABLE public.projects TO authenticated;
