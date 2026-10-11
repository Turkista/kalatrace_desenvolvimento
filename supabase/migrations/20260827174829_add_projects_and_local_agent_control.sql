create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid null references auth.users(id) on delete cascade,
  slug text not null unique,
  name text not null,
  project_type text not null check (project_type in ('scientific','robotics','infrastructure')),
  domain text,
  description text,
  status text not null default 'active' check (status in ('active','development','archived')),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists projects_owner_idx on public.projects(owner_id);
create index if not exists projects_status_idx on public.projects(status);

alter table public.research_form_records add column if not exists project_id uuid references public.projects(id) on delete set null;
create index if not exists research_form_records_project_idx on public.research_form_records(project_id);

create table if not exists public.local_agent_tasks (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  title text not null,
  description text,
  status text not null default 'queued' check (status in ('queued','planning','approved','running','blocked','completed','failed','cancelled')),
  priority integer not null default 50 check (priority between 0 and 100),
  task_type text not null default 'improvement',
  requested_by text not null default 'frontend',
  result jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  started_at timestamptz,
  completed_at timestamptz
);
create index if not exists local_agent_tasks_project_idx on public.local_agent_tasks(project_id, status, priority desc, created_at desc);

alter table public.projects enable row level security;
alter table public.local_agent_tasks enable row level security;
revoke all on public.projects from anon;
revoke all on public.local_agent_tasks from anon;
grant select, insert, update, delete on public.projects to authenticated;
grant select, insert, update, delete on public.local_agent_tasks to authenticated;

drop policy if exists projects_select_own on public.projects;
drop policy if exists projects_insert_own on public.projects;
drop policy if exists projects_update_own on public.projects;
drop policy if exists projects_delete_own on public.projects;
create policy projects_select_own on public.projects for select to authenticated using (owner_id is null or owner_id = (select auth.uid()));
create policy projects_insert_own on public.projects for insert to authenticated with check (owner_id = (select auth.uid()));
create policy projects_update_own on public.projects for update to authenticated using (owner_id = (select auth.uid())) with check (owner_id = (select auth.uid()));
create policy projects_delete_own on public.projects for delete to authenticated using (owner_id = (select auth.uid()));

drop policy if exists local_agent_tasks_select_own on public.local_agent_tasks;
drop policy if exists local_agent_tasks_insert_own on public.local_agent_tasks;
drop policy if exists local_agent_tasks_update_own on public.local_agent_tasks;
drop policy if exists local_agent_tasks_delete_own on public.local_agent_tasks;
create policy local_agent_tasks_select_own on public.local_agent_tasks for select to authenticated using ((select auth.uid()) = owner_id);
create policy local_agent_tasks_insert_own on public.local_agent_tasks for insert to authenticated with check ((select auth.uid()) = owner_id);
create policy local_agent_tasks_update_own on public.local_agent_tasks for update to authenticated using ((select auth.uid()) = owner_id) with check ((select auth.uid()) = owner_id);
create policy local_agent_tasks_delete_own on public.local_agent_tasks for delete to authenticated using ((select auth.uid()) = owner_id);

revoke all on public.research_form_records from anon;
grant select, insert, update, delete on public.research_form_records to authenticated;
revoke all on public.research_form_record_events from anon;
grant select, insert, update, delete on public.research_form_record_events to authenticated;

insert into public.projects (slug,name,project_type,domain,description,status)
values
 ('medikalat','MEDIKALAT','scientific','Biomedicina','Projeto piloto/aplicação científica do KALATRACE.','active'),
 ('robotica','Robótica','robotics','Robótica','Ambiente dedicado a robótica, comandos, missões, sensores, percepção, navegação e operação.','development'),
 ('agente-local','Agente Local','infrastructure','Desenvolvimento do KALATRACE','Ambiente de controle do agente local responsável por implementar, testar e evoluir o próprio KALATRACE.','development')
on conflict (slug) do update set name=excluded.name, project_type=excluded.project_type, domain=excluded.domain, description=excluded.description, status=excluded.status, updated_at=now();

update public.projects set owner_id = (select id from auth.users order by created_at asc limit 1) where owner_id is null and exists (select 1 from auth.users);
update public.research_form_records set project_id = (select id from public.projects where slug='medikalat') where project_id is null;
