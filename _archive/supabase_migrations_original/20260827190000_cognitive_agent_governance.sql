-- KALATRACE v7: durable bridge from CMC missions to governed coding tasks.
alter table public.local_agent_tasks add column if not exists mission_id uuid references public.cmc_missions(id) on delete set null;
alter table public.local_agent_tasks add column if not exists plan jsonb not null default '{}'::jsonb;
alter table public.local_agent_tasks add column if not exists validation jsonb not null default '{}'::jsonb;
alter table public.local_agent_tasks add column if not exists evidence jsonb not null default '[]'::jsonb;
create index if not exists local_agent_tasks_mission_idx on public.local_agent_tasks(mission_id, created_at desc);

-- Only mission owners may attach tasks to their mission through RLS.
drop policy if exists local_agent_tasks_insert_workspace on public.local_agent_tasks;
create policy local_agent_tasks_insert_workspace on public.local_agent_tasks for insert to authenticated with check (
  owner_id = (select auth.uid())
  and exists (
    select 1 from public.project_memberships pm
    where pm.project_id = local_agent_tasks.project_id
      and pm.user_id = (select auth.uid())
  )
  and (
    mission_id is null
    or exists (
      select 1 from public.cmc_missions m
      where m.id = local_agent_tasks.mission_id
        and m.owner_id = (select auth.uid())
    )
  )
);

comment on column public.local_agent_tasks.plan is 'Planner output. Informational until a separate approval transition accepts an explicit execution_spec.';
comment on column public.local_agent_tasks.execution_spec is 'The only executable contract. Must contain explicit allowlisted operations and is immutable by the runtime after approval.';
