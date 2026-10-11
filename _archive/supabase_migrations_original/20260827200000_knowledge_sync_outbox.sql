-- Durable cross-store synchronization ledger.
create table if not exists public.knowledge_sync_status (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  iec_id text not null,
  knowledge_node_id text not null,
  target text not null default 'neo4j',
  status text not null default 'pending' check (status in ('pending','synced','failed')),
  attempts integer not null default 0,
  last_error text,
  last_synced_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(owner_id, iec_id, target)
);
alter table public.knowledge_sync_status enable row level security;
grant select, insert, update on public.knowledge_sync_status to authenticated;
drop policy if exists knowledge_sync_status_owner on public.knowledge_sync_status;
create policy knowledge_sync_status_owner on public.knowledge_sync_status for all to authenticated using(owner_id=(select auth.uid())) with check(owner_id=(select auth.uid()));
create index if not exists knowledge_sync_status_lookup_idx on public.knowledge_sync_status(owner_id,status,updated_at desc);
