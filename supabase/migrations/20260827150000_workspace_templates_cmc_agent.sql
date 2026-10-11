-- KALATRACE: workspace governance, project templates, durable CMC artifacts and agent registration.

create table if not exists public.workspace_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  full_name text,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.workspace_profiles enable row level security;
grant select on public.workspace_profiles to authenticated;
drop policy if exists workspace_profiles_select on public.workspace_profiles;
create policy workspace_profiles_select on public.workspace_profiles for select to authenticated using (
  id = (select auth.uid()) or exists (
    select 1 from public.project_memberships pm
    join public.projects p on p.id = pm.project_id
    where pm.user_id = workspace_profiles.id
      and (p.owner_id = (select auth.uid()) or exists (
        select 1 from public.project_memberships me where me.project_id=p.id and me.user_id=(select auth.uid()) and me.role in ('owner','administrator')
      ))
  )
);

create or replace function public.handle_new_workspace_profile()
returns trigger language plpgsql security definer set search_path = ''
as $$
begin
  insert into public.workspace_profiles(id,email,full_name,avatar_url)
  values (new.id, coalesce(new.email,''), new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'avatar_url')
  on conflict (id) do update set email=excluded.email, full_name=coalesce(excluded.full_name,public.public.workspace_profiles.full_name), avatar_url=coalesce(excluded.avatar_url,public.workspace_profiles.avatar_url), updated_at=pg_catalog.now();
  return new;
end;
$$;
drop trigger if exists on_auth_user_workspace_profile on auth.users;
create trigger on_auth_user_workspace_profile after insert or update of email, raw_user_meta_data on auth.users
for each row execute function public.handle_new_workspace_profile();
revoke all on function public.handle_new_workspace_profile() from public, anon, authenticated;
insert into public.workspace_profiles(id,email,full_name,avatar_url)
select id,coalesce(email,''),raw_user_meta_data->>'full_name',raw_user_meta_data->>'avatar_url' from auth.users
on conflict (id) do update set email=excluded.email, full_name=coalesce(excluded.full_name,public.workspace_profiles.full_name), avatar_url=coalesce(excluded.avatar_url,public.workspace_profiles.avatar_url), updated_at=pg_catalog.now();

create table if not exists public.project_invitations (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  email text not null,
  role text not null default 'viewer' check (role in ('administrator','developer','researcher','operator','viewer')),
  invited_by uuid not null references auth.users(id) on delete cascade,
  status text not null default 'pending' check (status in ('pending','accepted','revoked','expired')),
  expires_at timestamptz not null default (now() + interval '7 days'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create unique index if not exists project_invitations_pending_idx on public.project_invitations(project_id,email) where status='pending';
alter table public.project_invitations enable row level security;
grant select,insert,update,delete on public.project_invitations to authenticated;
create or replace function public.can_manage_project(p_project_id uuid, p_user_id uuid)
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $function$
 SELECT p_user_id = (SELECT auth.uid()) AND (
   EXISTS (SELECT 1 FROM public.projects p WHERE p.id = p_project_id AND p.owner_id = p_user_id)
   OR EXISTS (
     SELECT 1 FROM public.project_memberships pm
     WHERE pm.project_id = p_project_id AND pm.user_id = p_user_id
       AND pm.role IN ('owner', 'administrator')
   )
 );
$function$;
REVOKE ALL ON FUNCTION public.can_manage_project(uuid, uuid) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.can_manage_project(uuid, uuid) TO authenticated;

DROP POLICY IF EXISTS project_memberships_select_own ON public.project_memberships;
CREATE POLICY project_memberships_select_own ON public.project_memberships
  FOR SELECT TO authenticated
  USING (user_id = (SELECT auth.uid()) OR public.can_manage_project(project_id, (SELECT auth.uid())));
drop policy if exists project_invitations_select on public.project_invitations;
drop policy if exists project_invitations_insert on public.project_invitations;
drop policy if exists project_invitations_update on public.project_invitations;
create policy project_invitations_select on public.project_invitations for select to authenticated using (
 invited_by=(select auth.uid()) or public.can_manage_project(project_id,(select auth.uid())) or lower(email)=lower((select email from auth.users where id=(select auth.uid())))
);
create policy project_invitations_insert on public.project_invitations for insert to authenticated with check (public.can_manage_project(project_id,(select auth.uid())) and invited_by=(select auth.uid()));
create policy project_invitations_update on public.project_invitations for update to authenticated using (public.can_manage_project(project_id,(select auth.uid()))) with check (public.can_manage_project(project_id,(select auth.uid())));
create or replace function public.accept_pending_project_invitations()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = ''
AS $function$
BEGIN
  IF NEW.email_confirmed_at IS NULL OR NEW.email IS NULL THEN
    RETURN NEW;
  END IF;

  INSERT INTO public.project_memberships(project_id, user_id, role)
  SELECT i.project_id, NEW.id, i.role
  FROM public.project_invitations AS i
  WHERE lower(i.email) = lower(NEW.email)
    AND i.status = 'pending'
    AND i.expires_at > pg_catalog.now()
  ON CONFLICT (project_id, user_id) DO UPDATE
    SET role = EXCLUDED.role, updated_at = pg_catalog.now()
    WHERE public.project_memberships.role <> 'owner';

  UPDATE public.project_invitations AS i
  SET status = 'accepted', updated_at = pg_catalog.now()
  WHERE lower(i.email) = lower(NEW.email)
    AND i.status = 'pending'
    AND i.expires_at > pg_catalog.now();

  RETURN NEW;
END;
$function$;
REVOKE ALL ON FUNCTION public.accept_pending_project_invitations() FROM PUBLIC, anon, authenticated;
drop trigger if exists on_auth_user_accept_project_invitations on auth.users;
create trigger on_auth_user_accept_project_invitations after insert or update of email, email_confirmed_at on auth.users for each row execute function public.accept_pending_project_invitations();

create table if not exists public.project_templates (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  description text,
  project_type text not null default 'custom',
  configuration jsonb not null default '{}'::jsonb,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.project_templates enable row level security;
grant select on public.project_templates to authenticated;
drop policy if exists project_templates_select on public.project_templates;
create policy project_templates_select on public.project_templates for select to authenticated using (active=true);
insert into public.project_templates(slug,name,description,project_type,configuration) values
('empty','Projeto vazio','Estrutura mínima para um novo projeto.','custom','{"modules":[],"engines":[],"skills":[],"cmc":false,"knowledge_graph":false}'::jsonb),
('scientific','Projeto científico','Base para pesquisa e evidência.','scientific','{"modules":["evidence","validation"],"engines":["research_strategy","reasoning"],"skills":[],"cmc":true,"knowledge_graph":true}'),
('robotics','Projeto de robótica','Base para ativos robóticos e missões.','robotics','{"modules":["cmc","robotics"],"engines":["prediction","simulation"],"skills":["robotics"],"cmc":true,"knowledge_graph":true}'),
('simulation','Projeto de simulação','Ambiente para cenários e execução simulada.','custom','{"modules":["simulation","cmc"],"engines":["simulation","prediction"],"skills":[],"cmc":true,"knowledge_graph":true}'),
('knowledge-graph','Projeto Knowledge Graph','Projeto centrado em conhecimento estruturado.','custom','{"modules":["knowledge_graph","evidence","validation"],"engines":["reasoning","knowledge_evolution"],"skills":[],"cmc":false,"knowledge_graph":true}')
on conflict(slug) do update set configuration=excluded.configuration,updated_at=pg_catalog.now();

create table if not exists public.cmc_commands (
 id uuid primary key default gen_random_uuid(), mission_id uuid not null references public.cmc_missions(id) on delete cascade,
 owner_id uuid not null references auth.users(id) on delete cascade, name text not null, objective text not null,
 priority text not null default 'NORMAL', status text not null default 'CREATED', executor text, result jsonb not null default '{}'::jsonb,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.cmc_decisions (
 id uuid primary key default gen_random_uuid(), mission_id uuid not null references public.cmc_missions(id) on delete cascade,
 owner_id uuid not null references auth.users(id) on delete cascade, action text not null, reason text not null,
 confidence numeric not null default 0 check(confidence between 0 and 1), evidence jsonb not null default '[]'::jsonb,
 alternatives jsonb not null default '[]'::jsonb, status text not null default 'PROPOSED', created_at timestamptz not null default now()
);
create table if not exists public.cmc_resource_allocations (
 id uuid primary key default gen_random_uuid(), mission_id uuid not null references public.cmc_missions(id) on delete cascade,
 owner_id uuid not null references auth.users(id) on delete cascade, resource_id text not null, amount numeric not null,
 status text not null default 'ALLOCATED', created_at timestamptz not null default now(), released_at timestamptz
);
create table if not exists public.cmc_events (
 id uuid primary key default gen_random_uuid(), mission_id uuid not null references public.cmc_missions(id) on delete cascade,
 owner_id uuid not null references auth.users(id) on delete cascade, event_type text not null, payload jsonb not null default '{}'::jsonb,
 created_at timestamptz not null default now()
);
create index if not exists cmc_commands_mission_idx on public.cmc_commands(mission_id,created_at desc);
create index if not exists cmc_decisions_mission_idx on public.cmc_decisions(mission_id,created_at desc);
create index if not exists cmc_events_mission_idx on public.cmc_events(mission_id,created_at desc);

create table if not exists public.local_agent_instances (
 id uuid primary key default gen_random_uuid(), owner_id uuid not null references auth.users(id) on delete cascade, instance_name text not null unique, status text not null default 'offline' check(status in ('online','offline','busy','degraded')),
 capabilities jsonb not null default '[]'::jsonb, last_heartbeat_at timestamptz, metadata jsonb not null default '{}'::jsonb,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);

alter table public.cmc_commands enable row level security; alter table public.cmc_decisions enable row level security; alter table public.cmc_resource_allocations enable row level security; alter table public.cmc_events enable row level security; alter table public.local_agent_instances enable row level security;
grant select,insert,update,delete on public.cmc_commands,public.cmc_decisions,public.cmc_resource_allocations,public.cmc_events to authenticated;
grant select,insert,update on public.local_agent_instances to authenticated;

create policy cmc_commands_owner on public.cmc_commands for all to authenticated using(owner_id=(select auth.uid())) with check(owner_id=(select auth.uid()));
create policy cmc_decisions_owner on public.cmc_decisions for all to authenticated using(owner_id=(select auth.uid())) with check(owner_id=(select auth.uid()));
create policy cmc_resources_owner on public.cmc_resource_allocations for all to authenticated using(owner_id=(select auth.uid())) with check(owner_id=(select auth.uid()));
create policy cmc_events_owner on public.cmc_events for all to authenticated using(owner_id=(select auth.uid())) with check(owner_id=(select auth.uid()));
create policy local_agent_instances_read on public.local_agent_instances for select to authenticated using(owner_id=(select auth.uid()));

-- Expand project RLS to project members and administrators.
drop policy if exists projects_select_own on public.projects;
drop policy if exists projects_update_own on public.projects;
drop policy if exists projects_delete_own on public.projects;
create policy projects_select_workspace on public.projects for select to authenticated using (
 owner_id=(select auth.uid()) or exists(select 1 from public.project_memberships pm where pm.project_id=projects.id and pm.user_id=(select auth.uid()))
);
create policy projects_update_workspace on public.projects for update to authenticated using (
 owner_id=(select auth.uid()) or exists(select 1 from public.project_memberships pm where pm.project_id=projects.id and pm.user_id=(select auth.uid()) and pm.role in ('owner','administrator'))
) with check (
 owner_id=(select auth.uid()) or exists(select 1 from public.project_memberships pm where pm.project_id=projects.id and pm.user_id=(select auth.uid()) and pm.role in ('owner','administrator'))
);
create policy projects_delete_workspace on public.projects for delete to authenticated using (owner_id=(select auth.uid()));

drop policy if exists project_memberships_insert_own on public.project_memberships;
drop policy if exists project_memberships_update_own on public.project_memberships;
drop policy if exists project_memberships_delete_own on public.project_memberships;
create policy project_memberships_insert_managed on public.project_memberships for insert to authenticated with check (public.can_manage_project(project_id,(select auth.uid())) and role in ('administrator','developer','researcher','operator','viewer'));
create policy project_memberships_update_managed on public.project_memberships for update to authenticated using (public.can_manage_project(project_id,(select auth.uid()))) with check (public.can_manage_project(project_id,(select auth.uid())) and role in ('administrator','developer','researcher','operator','viewer'));
create policy project_memberships_delete_managed on public.project_memberships for delete to authenticated using (
  public.can_manage_project(project_id,(select auth.uid()))
  AND NOT EXISTS (
    SELECT 1 FROM public.projects p
    WHERE p.id = project_memberships.project_id
      AND p.owner_id = project_memberships.user_id
  )
);

-- Mission artifacts are visible to the mission owner. Project-level expansion can be added later.

alter table public.local_agent_instances add column if not exists owner_id uuid references auth.users(id) on delete cascade;
create index if not exists local_agent_instances_owner_idx on public.local_agent_instances(owner_id);
grant insert,update on public.local_agent_instances to authenticated;
drop policy if exists local_agent_instances_read on public.local_agent_instances;
create policy local_agent_instances_read on public.local_agent_instances for select to authenticated using(owner_id=(select auth.uid()));
drop policy if exists local_agent_instances_write on public.local_agent_instances;
create policy local_agent_instances_write on public.local_agent_instances for all to authenticated using(owner_id=(select auth.uid())) with check(owner_id=(select auth.uid()));

-- Runtime CMC entities use the same UUIDs as the in-process entities, so the
-- database can become the durable source of mission history without a second ID map.
