-- KALATRACE Workspace / Project governance / generic CMC persistence
-- Keeps secrets out of SQL and uses Supabase Auth + RLS.

-- Projects must support arbitrary future domains.
alter table public.projects drop constraint if exists projects_project_type_check;

create table if not exists public.project_memberships (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null default 'viewer' check (role in ('owner','administrator','developer','researcher','operator','viewer')),
  permissions jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(project_id,user_id)
);
create index if not exists project_memberships_user_idx on public.project_memberships(user_id);
create index if not exists project_memberships_project_idx on public.project_memberships(project_id);
alter table public.project_memberships enable row level security;
grant select, insert, update, delete on public.project_memberships to authenticated;
drop policy if exists project_memberships_select_own on public.project_memberships;
drop policy if exists project_memberships_insert_own on public.project_memberships;
drop policy if exists project_memberships_update_own on public.project_memberships;
drop policy if exists project_memberships_delete_own on public.project_memberships;
create policy project_memberships_select_own on public.project_memberships for select to authenticated using (user_id=(select auth.uid()) or exists (select 1 from public.projects p where p.id=project_id and p.owner_id=(select auth.uid())));
create policy project_memberships_insert_own on public.project_memberships for insert to authenticated with check (exists (select 1 from public.projects p where p.id=project_id and p.owner_id=(select auth.uid())));
-- Membership role updates are intentionally deferred to the authorized RPC in migration 20260827210000.
create policy project_memberships_delete_own on public.project_memberships for delete to authenticated using (user_id=(select auth.uid()) or exists (select 1 from public.projects p where p.id=project_id and p.owner_id=(select auth.uid())));

-- Automatically make project owners members.
insert into public.project_memberships(project_id,user_id,role)
select p.id,p.owner_id,'owner' from public.projects p where p.owner_id is not null
on conflict (project_id,user_id) do update set role='owner', updated_at=now();

create table if not exists public.cmc_missions (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  project_id uuid references public.projects(id) on delete set null,
  name text not null,
  objective text not null,
  priority text not null default 'NORMAL',
  status text not null default 'CREATED',
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists cmc_missions_project_idx on public.cmc_missions(project_id,status,created_at desc);
alter table public.cmc_missions enable row level security;
grant select,insert,update,delete on public.cmc_missions to authenticated;
drop policy if exists cmc_missions_select_own on public.cmc_missions;
drop policy if exists cmc_missions_insert_own on public.cmc_missions;
drop policy if exists cmc_missions_update_own on public.cmc_missions;
drop policy if exists cmc_missions_delete_own on public.cmc_missions;
create policy cmc_missions_select_own on public.cmc_missions for select to authenticated using (owner_id=(select auth.uid()));
create policy cmc_missions_insert_own on public.cmc_missions for insert to authenticated with check (owner_id=(select auth.uid()));
create policy cmc_missions_update_own on public.cmc_missions for update to authenticated using (owner_id=(select auth.uid())) with check (owner_id=(select auth.uid()));
create policy cmc_missions_delete_own on public.cmc_missions for delete to authenticated using (owner_id=(select auth.uid()));
