-- Allow generic/custom projects required by the template system.
alter table public.projects drop constraint if exists projects_project_type_check;
alter table public.projects add constraint projects_project_type_check check (project_type in ('scientific','robotics','infrastructure','custom','simulation','research','ai'));

alter table public.local_agent_tasks add column if not exists execution_spec jsonb not null default '{}'::jsonb;
alter table public.local_agent_tasks add column if not exists claimed_by uuid references public.local_agent_instances(id) on delete set null;
alter table public.local_agent_tasks add column if not exists approved_by uuid references auth.users(id) on delete set null;
alter table public.local_agent_tasks add column if not exists approved_at timestamptz;
alter table public.local_agent_tasks add column if not exists execution_log jsonb not null default '[]'::jsonb;
create index if not exists local_agent_tasks_claimed_idx on public.local_agent_tasks(claimed_by, status, updated_at desc);

alter table public.cmc_missions add column if not exists timeline jsonb not null default '[]'::jsonb;
alter table public.cmc_missions add column if not exists payload jsonb not null default '{}'::jsonb;

-- Project-scoped access for agent tasks: owners and project administrators can manage them.
drop policy if exists local_agent_tasks_select_own on public.local_agent_tasks;
drop policy if exists local_agent_tasks_insert_own on public.local_agent_tasks;
drop policy if exists local_agent_tasks_update_own on public.local_agent_tasks;
drop policy if exists local_agent_tasks_delete_own on public.local_agent_tasks;
create policy local_agent_tasks_select_workspace on public.local_agent_tasks for select to authenticated using (
  owner_id = (select auth.uid()) or exists (
    select 1 from public.project_memberships pm where pm.project_id = local_agent_tasks.project_id and pm.user_id = (select auth.uid())
  )
);
create policy local_agent_tasks_insert_workspace on public.local_agent_tasks for insert to authenticated with check (
  owner_id = (select auth.uid()) and exists (
    select 1 from public.project_memberships pm where pm.project_id = local_agent_tasks.project_id and pm.user_id = (select auth.uid())
  )
);
create policy local_agent_tasks_update_workspace on public.local_agent_tasks for update to authenticated using (
  owner_id = (select auth.uid()) or exists (
    select 1 from public.project_memberships pm where pm.project_id = local_agent_tasks.project_id and pm.user_id = (select auth.uid()) and pm.role in ('owner','administrator','developer')
  )
) with check (owner_id = owner_id);

-- Atomic task claim prevents two Local Agent instances from taking the same task.
create or replace function public.claim_next_local_agent_task(p_instance_name text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_instance uuid;
  v_task jsonb;
begin
  select id into v_instance
  from public.local_agent_instances
  where instance_name = p_instance_name
    and owner_id = auth.uid()
  limit 1;

  if v_instance is null then
    raise exception 'Local agent instance not found or not owned by current user';
  end if;

  with candidate as (
    select id
    from public.local_agent_tasks
    where status = 'approved'
      and (owner_id = auth.uid() or exists (
        select 1 from public.project_memberships pm
        where pm.project_id = local_agent_tasks.project_id
          and pm.user_id = auth.uid()
      ))
    order by priority desc, created_at asc
    for update skip locked
    limit 1
  )
  update public.local_agent_tasks t
  set status = 'running', claimed_by = v_instance, started_at = coalesce(started_at, now()), updated_at = now()
  from candidate
  where t.id = candidate.id
  returning to_jsonb(t) into v_task;

  return coalesce(v_task, 'null'::jsonb);
end;
$$;
revoke all on function public.claim_next_local_agent_task(text) from public;
grant execute on function public.claim_next_local_agent_task(text) to authenticated;
