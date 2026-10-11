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
    select 1 from public.project_memberships pm where pm.project_id = local_agent_tasks.project_id and pm.user_id = (select auth.uid()) and pm.role in ('owner','administrator','developer','operator')
  )
) with check (
  owner_id = (SELECT auth.uid()) OR EXISTS (
    SELECT 1 FROM public.project_memberships pm
    WHERE pm.project_id = local_agent_tasks.project_id
      AND pm.user_id = (SELECT auth.uid())
      AND pm.role IN ('owner', 'administrator', 'developer', 'operator')
  )
);

-- Enforce approval and execution invariants at the database boundary.
CREATE OR REPLACE FUNCTION public.guard_local_agent_task_mutations()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = ''
AS $function$
BEGIN
  IF NEW.owner_id IS DISTINCT FROM OLD.owner_id THEN
    RAISE EXCEPTION 'Task ownership cannot be changed';
  END IF;

  IF OLD.approved_at IS NOT NULL
     AND NEW.execution_spec IS DISTINCT FROM OLD.execution_spec THEN
    RAISE EXCEPTION 'Execution specification is immutable after approval';
  END IF;

  IF OLD.approved_at IS NOT NULL
     AND (NEW.approved_by IS DISTINCT FROM OLD.approved_by
          OR NEW.approved_at IS DISTINCT FROM OLD.approved_at) THEN
    RAISE EXCEPTION 'Approval metadata is immutable after approval';
  END IF;

  IF OLD.approved_at IS NULL AND NEW.approved_at IS NOT NULL
     AND NEW.status IS DISTINCT FROM 'approved' THEN
    RAISE EXCEPTION 'Approval metadata can only be set during approval';
  END IF;

  IF NEW.status = 'approved' AND OLD.status IS DISTINCT FROM 'approved' THEN
    IF NEW.approved_by IS DISTINCT FROM (SELECT auth.uid()) OR NEW.approved_at IS NULL THEN
      RAISE EXCEPTION 'Approval metadata must identify the approving user';
    END IF;

    IF NOT EXISTS (
      SELECT 1
      FROM public.projects p
      LEFT JOIN public.project_memberships pm
        ON pm.project_id = p.id AND pm.user_id = (SELECT auth.uid())
      WHERE p.id = NEW.project_id
        AND (
          p.owner_id = (SELECT auth.uid())
          OR pm.role IN ('owner', 'administrator', 'developer', 'operator')
        )
    ) THEN
      RAISE EXCEPTION 'Only authorized project members may approve executable tasks';
    END IF;
  END IF;

  IF NEW.status = 'running' AND OLD.status NOT IN ('approved', 'running') THEN
    RAISE EXCEPTION 'A task must be approved before it can run';
  END IF;

  RETURN NEW;
END;
$function$;

REVOKE ALL ON FUNCTION public.guard_local_agent_task_mutations() FROM PUBLIC, anon, authenticated;
DROP TRIGGER IF EXISTS guard_local_agent_task_mutations ON public.local_agent_tasks;
CREATE TRIGGER guard_local_agent_task_mutations
  BEFORE UPDATE ON public.local_agent_tasks
  FOR EACH ROW EXECUTE FUNCTION public.guard_local_agent_task_mutations();

-- Atomic task claim prevents two Local Agent instances from taking the same task.
create or replace function public.claim_next_local_agent_task(p_instance_name text)
returns jsonb
language plpgsql
security definer
set search_path = ''
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
          and pm.user_id = (SELECT auth.uid())
          and pm.role in ('owner','administrator','developer','operator')
      ))
    order by priority desc, created_at asc
    for update skip locked
    limit 1
  )
  update public.local_agent_tasks t
  set status = 'running', claimed_by = v_instance, started_at = coalesce(started_at, pg_catalog.now()), updated_at = pg_catalog.now()
  from candidate
  where t.id = candidate.id
  returning to_jsonb(t) into v_task;

  return coalesce(v_task, 'null'::jsonb);
end;
$$;
revoke all on function public.claim_next_local_agent_task(text) from public, anon;
grant execute on function public.claim_next_local_agent_task(text) to authenticated;
