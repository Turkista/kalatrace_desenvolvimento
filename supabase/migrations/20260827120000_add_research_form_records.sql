-- KALATRACE: persistent research forms and audit events.
-- Transactional/raw research records live in Supabase PostgreSQL.
-- Only semantically relevant entities/relationships are promoted to Neo4j.

create table if not exists public.research_form_records (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  form_type text not null check (form_type in ('lote','dose','celular','bruta','toxico','clinica','naoconf','relatorio')),
  status text not null default 'draft' check (status in ('draft','submitted','reviewed','archived')),
  data jsonb not null default '{}'::jsonb,
  source text not null default 'frontend',
  iec_id uuid null references public.iecs(id) on delete set null,
  knowledge_node_id uuid null references public.knowledge_nodes(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists research_form_records_owner_idx on public.research_form_records(owner_id);
create index if not exists research_form_records_type_idx on public.research_form_records(form_type);
create index if not exists research_form_records_iec_idx on public.research_form_records(iec_id);
create index if not exists research_form_records_node_idx on public.research_form_records(knowledge_node_id);

create table if not exists public.research_form_record_events (
  id uuid primary key default gen_random_uuid(),
  record_id uuid not null references public.research_form_records(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists research_form_record_events_record_idx on public.research_form_record_events(record_id);
create index if not exists research_form_record_events_owner_idx on public.research_form_record_events(owner_id);

alter table public.research_form_records enable row level security;
alter table public.research_form_record_events enable row level security;

drop policy if exists research_form_records_all_own on public.research_form_records;
create policy research_form_records_all_own on public.research_form_records for all to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);

drop policy if exists research_form_record_events_all_own on public.research_form_record_events;
create policy research_form_record_events_all_own on public.research_form_record_events for all to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);

grant select, insert, update, delete on public.research_form_records to authenticated;
grant select, insert, update, delete on public.research_form_record_events to authenticated;

create or replace function public.set_research_form_records_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;
drop trigger if exists research_form_records_updated_at on public.research_form_records;
create trigger research_form_records_updated_at before update on public.research_form_records
for each row execute function public.set_research_form_records_updated_at();
