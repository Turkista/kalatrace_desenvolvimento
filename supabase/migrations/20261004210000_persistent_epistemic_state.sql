-- KALATRACE: persistent epistemic evidence and evolution state.
-- Supabase/PostgreSQL is the durable source for transactional epistemic state.
-- Neo4j remains the graph projection; synchronization is tracked separately.

create table if not exists public.evidence (
  id text primary key,
  owner_id uuid not null references auth.users(id) on delete cascade,
  evidence_type text not null,
  source text,
  title text not null,
  content text not null,
  confidence double precision not null default 0.50 check (confidence between 0 and 1),
  quality_score double precision not null default 0.50 check (quality_score between 0 and 1),
  evidence_level text,
  doi text,
  pmid text,
  url text,
  domain text,
  category text,
  version integer not null default 1 check (version >= 1),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists evidence_owner_idx on public.evidence(owner_id);
create index if not exists evidence_type_idx on public.evidence(evidence_type);

create table if not exists public.evidence_iec_links (
  evidence_id text not null references public.evidence(id) on delete cascade,
  iec_id text not null,
  owner_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (evidence_id, iec_id)
);

create index if not exists evidence_iec_links_iec_idx on public.evidence_iec_links(iec_id);
create index if not exists evidence_iec_links_owner_idx on public.evidence_iec_links(owner_id);

create table if not exists public.evidence_history (
  id uuid primary key default gen_random_uuid(),
  evidence_id text not null references public.evidence(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  event_type text not null,
  previous_confidence double precision,
  new_confidence double precision,
  reason text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists evidence_history_evidence_idx on public.evidence_history(evidence_id, created_at desc);
create index if not exists evidence_history_owner_idx on public.evidence_history(owner_id);

create table if not exists public.iec_state_history (
  id uuid primary key default gen_random_uuid(),
  iec_id text not null,
  owner_id uuid not null references auth.users(id) on delete cascade,
  from_state text,
  to_state text not null,
  reason text not null,
  created_at timestamptz not null default now()
);

create index if not exists iec_state_history_iec_idx on public.iec_state_history(iec_id, created_at desc);
create index if not exists iec_state_history_owner_idx on public.iec_state_history(owner_id);

create table if not exists public.knowledge_evolution_events (
  id uuid primary key default gen_random_uuid(),
  iec_id text,
  owner_id uuid not null references auth.users(id) on delete cascade,
  event_type text not null,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists knowledge_evolution_events_iec_idx on public.knowledge_evolution_events(iec_id, created_at desc);
create index if not exists knowledge_evolution_events_owner_idx on public.knowledge_evolution_events(owner_id);

alter table public.evidence enable row level security;
alter table public.evidence_iec_links enable row level security;
alter table public.evidence_history enable row level security;
alter table public.iec_state_history enable row level security;
alter table public.knowledge_evolution_events enable row level security;

revoke all on public.evidence from anon;
revoke all on public.evidence_iec_links from anon;
revoke all on public.evidence_history from anon;
revoke all on public.iec_state_history from anon;
revoke all on public.knowledge_evolution_events from anon;

grant select, insert, update, delete on public.evidence to authenticated;
grant select, insert, update, delete on public.evidence_iec_links to authenticated;
grant select, insert, update, delete on public.evidence_history to authenticated;
grant select, insert, update, delete on public.iec_state_history to authenticated;
grant select, insert, update, delete on public.knowledge_evolution_events to authenticated;

create policy evidence_own on public.evidence for all to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);

create policy evidence_iec_links_own on public.evidence_iec_links for all to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);

create policy evidence_history_own on public.evidence_history for all to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);

create policy iec_state_history_own on public.iec_state_history for all to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);

create policy knowledge_evolution_events_own on public.knowledge_evolution_events for all to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);

create or replace function public.set_evidence_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;

drop trigger if exists evidence_updated_at on public.evidence;
create trigger evidence_updated_at before update on public.evidence
for each row execute function public.set_evidence_updated_at();
