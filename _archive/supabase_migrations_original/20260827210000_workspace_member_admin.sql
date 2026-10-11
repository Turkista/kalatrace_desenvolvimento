-- Workspace administration: role changes and member removal are restricted by
-- project owner/administrator RLS. A member cannot elevate its own role.
drop policy if exists project_memberships_update_managed on public.project_memberships;
create policy project_memberships_update_managed on public.project_memberships for update to authenticated
using (can_manage_project(project_id,(select auth.uid())))
with check (
  can_manage_project(project_id,(select auth.uid()))
  and role in ('owner','administrator','developer','researcher','operator','viewer')
);

create or replace function public.update_project_member_role(
  p_project_id uuid,
  p_user_id uuid,
  p_role text
)
returns jsonb
language plpgsql
security definer
set search_path=public
as $$
declare v_row jsonb;
begin
  if not can_manage_project(p_project_id, auth.uid()) then
    raise exception 'Not authorized to manage project members';
  end if;
  if p_role not in ('administrator','developer','researcher','operator','viewer') then
    raise exception 'Invalid project role';
  end if;
  update project_memberships
  set role=p_role, updated_at=now()
  where project_id=p_project_id and user_id=p_user_id
  returning to_jsonb(project_memberships.*) into v_row;
  if v_row is null then raise exception 'Project member not found'; end if;
  return v_row;
end;
$$;
revoke all on function public.update_project_member_role(uuid,uuid,text) from public;
grant execute on function public.update_project_member_role(uuid,uuid,text) to authenticated;
