-- RECONSTRUCTED baseline from the live Supabase catalog.
-- The original SQL source for remote version 20261008190604 was not present in Git history.
-- This file is intended to make clean local resets reproducible; it is not claimed to be
-- a byte-for-byte recovery of the original migration. Remote already records this version.

CREATE SCHEMA IF NOT EXISTS private;

CREATE TABLE IF NOT EXISTS public.infrastructure_usage_snapshots (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  measured_at timestamptz NOT NULL DEFAULT now(),
  database_bytes bigint NOT NULL,
  database_quota_bytes bigint NOT NULL,
  storage_bytes bigint NOT NULL,
  storage_quota_bytes bigint NOT NULL,
  storage_objects bigint NOT NULL,
  iecs bigint NOT NULL DEFAULT 0,
  evidence bigint NOT NULL DEFAULT 0,
  evidence_iec_links bigint NOT NULL DEFAULT 0,
  iec_state_history bigint NOT NULL DEFAULT 0,
  knowledge_evolution_events bigint NOT NULL DEFAULT 0,
  evidence_history bigint NOT NULL DEFAULT 0,
  database_status text NOT NULL,
  storage_status text NOT NULL,
  health_score integer NOT NULL DEFAULT 100,
  overall_status text NOT NULL DEFAULT 'HEALTHY',
  evaluation jsonb NOT NULL DEFAULT '{}'::jsonb,
  epistemic_health text NOT NULL DEFAULT 'HEALTHY',
  persistence_health text NOT NULL DEFAULT 'HEALTHY',
  graph_health text NOT NULL DEFAULT 'HEALTHY',
  integrity_issues jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS public.infrastructure_watchdog_events (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  created_at timestamptz NOT NULL DEFAULT now(),
  last_seen_at timestamptz NOT NULL DEFAULT now(),
  resolved_at timestamptz,
  category text NOT NULL,
  severity text NOT NULL,
  code text NOT NULL,
  message text NOT NULL,
  current_value numeric,
  threshold_value numeric,
  snapshot_id bigint REFERENCES public.infrastructure_usage_snapshots(id) ON DELETE SET NULL,
  details jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_infrastructure_usage_snapshots_measured_at
  ON public.infrastructure_usage_snapshots (measured_at DESC);
CREATE INDEX IF NOT EXISTS idx_infrastructure_watchdog_events_open
  ON public.infrastructure_watchdog_events (resolved_at, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_infrastructure_watchdog_events_snapshot_id
  ON public.infrastructure_watchdog_events (snapshot_id);
CREATE UNIQUE INDEX IF NOT EXISTS ux_infrastructure_watchdog_events_open_code
  ON public.infrastructure_watchdog_events (code) WHERE resolved_at IS NULL;

ALTER TABLE public.infrastructure_usage_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.infrastructure_watchdog_events ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.infrastructure_usage_snapshots, public.infrastructure_watchdog_events FROM anon;
GRANT SELECT ON public.infrastructure_usage_snapshots, public.infrastructure_watchdog_events TO authenticated;

DROP POLICY IF EXISTS "authenticated can read watchdog snapshots" ON public.infrastructure_usage_snapshots;
CREATE POLICY "authenticated can read watchdog snapshots"
  ON public.infrastructure_usage_snapshots FOR SELECT TO authenticated USING (true);
DROP POLICY IF EXISTS "authenticated can read watchdog events" ON public.infrastructure_watchdog_events;
CREATE POLICY "authenticated can read watchdog events"
  ON public.infrastructure_watchdog_events FOR SELECT TO authenticated USING (true);

CREATE OR REPLACE FUNCTION private.collect_kalatrace_infrastructure_usage()
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
declare
  db_bytes bigint;
  storage_bytes bigint;
  storage_objects bigint;
  db_quota_bytes bigint := 500 * 1024 * 1024;
  storage_quota_bytes bigint := 1 * 1024 * 1024 * 1024;
  bucket_rows jsonb;
  table_rows jsonb;
  epistemic_rows jsonb;
begin
  select pg_catalog.pg_database_size(pg_catalog.current_database()) into db_bytes;
  select
    coalesce(sum(coalesce((o.metadata->>'size')::bigint, 0)), 0),
    count(*)
  into storage_bytes, storage_objects
  from storage.objects o;

  select coalesce(jsonb_agg(jsonb_build_object(
    'bucket_id', b.bucket_id, 'bytes', b.total_bytes, 'objects', b.object_count
  ) order by b.total_bytes desc), '[]'::jsonb)
  into bucket_rows
  from (
    select bucket_id,
      coalesce(sum(coalesce((o.metadata->>'size')::bigint,0)),0) total_bytes,
      count(*) object_count
    from storage.objects o
    group by bucket_id
  ) b;

  select coalesce(jsonb_agg(jsonb_build_object(
    'schema', n.nspname, 'table', c.relname,
    'bytes', pg_catalog.pg_total_relation_size(c.oid),
    'size', pg_catalog.pg_size_pretty(pg_catalog.pg_total_relation_size(c.oid)),
    'table_bytes', pg_catalog.pg_relation_size(c.oid),
    'index_bytes', pg_catalog.pg_indexes_size(c.oid)
  ) order by pg_catalog.pg_total_relation_size(c.oid) desc), '[]'::jsonb)
  into table_rows
  from pg_catalog.pg_class c
  join pg_catalog.pg_namespace n on n.oid = c.relnamespace
  where c.relkind = 'r' and n.nspname = 'public';

  select jsonb_build_object(
    'iecs', (select count(*) from public.iecs),
    'evidence', (select count(*) from public.evidence),
    'evidence_iec_links', (select count(*) from public.evidence_iec_links),
    'iec_state_history', (select count(*) from public.iec_state_history),
    'knowledge_evolution_events', (select count(*) from public.knowledge_evolution_events),
    'evidence_history', (select count(*) from public.evidence_history)
  ) into epistemic_rows;

  return jsonb_build_object(
    'project','Kalatrace',
    'database', jsonb_build_object(
      'bytes',db_bytes,'quota_bytes',db_quota_bytes,
      'available_bytes',greatest(db_quota_bytes-db_bytes,0),
      'usage_percent',round((db_bytes::numeric/db_quota_bytes)*100,2),
      'status',case when db_bytes>=db_quota_bytes then 'critical'
                    when db_bytes>=db_quota_bytes*0.9 then 'warning' else 'healthy' end
    ),
    'storage', jsonb_build_object(
      'bytes',storage_bytes,'quota_bytes',storage_quota_bytes,
      'available_bytes',greatest(storage_quota_bytes-storage_bytes,0),
      'usage_percent',round((storage_bytes::numeric/storage_quota_bytes)*100,2),
      'objects',storage_objects,
      'status',case when storage_bytes>=storage_quota_bytes then 'critical'
                    when storage_bytes>=storage_quota_bytes*0.9 then 'warning' else 'healthy' end,
      'buckets',bucket_rows
    ),
    'epistemic',epistemic_rows,'tables',table_rows,
    'database_name',pg_catalog.current_database(),'measured_at',now()
  );
end;
$function$;


CREATE OR REPLACE FUNCTION private.sync_kalatrace_watchdog_events(p_snapshot_id bigint)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
declare
  s record; item record; existing_id bigint; active boolean; severity_value text; cur_value numeric; thresh_value numeric; details_value jsonb;
begin
  select * into s from public.infrastructure_usage_snapshots where id=p_snapshot_id;
  if s.id is null then return; end if;
  for item in select * from (values
    ('INFRASTRUCTURE','DATABASE_CAPACITY','Database usage is approaching or exceeding quota',s.database_status,(s.database_bytes::numeric/nullif(s.database_quota_bytes,0))*100,90::numeric),
    ('INFRASTRUCTURE','STORAGE_CAPACITY','Storage usage is approaching or exceeding quota',s.storage_status,(s.storage_bytes::numeric/nullif(s.storage_quota_bytes,0))*100,90::numeric),
    ('INFRASTRUCTURE','DATABASE_GROWTH','Database growth is unusually high',case when coalesce((s.evaluation->>'database_growth_percent')::numeric,0)>=40 then 'CRITICAL' when coalesce((s.evaluation->>'database_growth_percent')::numeric,0)>=20 then 'WARNING' else 'HEALTHY' end,(s.evaluation->>'database_growth_percent')::numeric,20::numeric),
    ('INFRASTRUCTURE','STORAGE_GROWTH','Storage growth is unusually high',case when coalesce((s.evaluation->>'storage_growth_percent')::numeric,0)>=40 then 'CRITICAL' when coalesce((s.evaluation->>'storage_growth_percent')::numeric,0)>=20 then 'WARNING' else 'HEALTHY' end,(s.evaluation->>'storage_growth_percent')::numeric,20::numeric),
    ('EPISTEMIC','EPISTEMIC_INTEGRITY','Epistemic integrity checks found orphan records',s.epistemic_health,null,null),
    ('PERSISTENCE','PERSISTENCE_INTEGRITY','Persistence integrity checks found inconsistencies',s.persistence_health,null,null),
    ('GRAPH','GRAPH_INTEGRITY','Knowledge Graph integrity checks found orphan edges',s.graph_health,null,null)
  ) as v(category,code,message,status,current_value,threshold_value)
  loop
    active := item.status in ('WARNING','CRITICAL');
    severity_value := case when item.status='CRITICAL' then 'CRITICAL' else 'WARNING' end;
    cur_value := item.current_value;
    thresh_value := item.threshold_value;
    details_value := coalesce(s.evaluation,'{}'::jsonb) || jsonb_build_object('integrity',coalesce(s.integrity_issues,'{}'::jsonb));
    if active then
      select id into existing_id from public.infrastructure_watchdog_events where code=item.code and resolved_at is null order by created_at desc limit 1;
      if existing_id is null then
        insert into public.infrastructure_watchdog_events(category,severity,code,message,current_value,threshold_value,snapshot_id,details)
        values(item.category,severity_value,item.code,item.message,cur_value,thresh_value,s.id,details_value);
      else
        update public.infrastructure_watchdog_events
        set last_seen_at=now(), severity=severity_value, current_value=cur_value, threshold_value=thresh_value, snapshot_id=s.id, details=details_value
        where id=existing_id;
      end if;
    else
      update public.infrastructure_watchdog_events
      set resolved_at=coalesce(resolved_at,now()), last_seen_at=now(), snapshot_id=s.id
      where code=item.code and resolved_at is null;
    end if;
  end loop;
end;
$function$;


CREATE OR REPLACE FUNCTION private.run_kalatrace_watchdog()
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
declare
  usage jsonb;
  previous record;
  snapshot_id bigint;
  db_pct numeric;
  storage_pct numeric;
  db_growth_pct numeric;
  storage_growth_pct numeric;
  score integer := 100;
  overall text := 'HEALTHY';
  db_status text;
  storage_status text;
  epistemic_status text := 'HEALTHY';
  persistence_status text := 'HEALTHY';
  graph_status text := 'HEALTHY';
  evaluation jsonb;
  integrity jsonb;
  orphan_links bigint := 0;
  orphan_state_history bigint := 0;
  orphan_evidence_history bigint := 0;
  orphan_evolution_events bigint := 0;
  orphan_graph_edges bigint := 0;
  graph_nodes bigint := 0;
  graph_edges bigint := 0;
begin
  usage := private.collect_kalatrace_infrastructure_usage();
  db_pct := ((usage->'database'->>'bytes')::numeric / nullif((usage->'database'->>'quota_bytes')::numeric,0))*100;
  storage_pct := ((usage->'storage'->>'bytes')::numeric / nullif((usage->'storage'->>'quota_bytes')::numeric,0))*100;

  select * into previous from public.infrastructure_usage_snapshots order by measured_at desc limit 1;
  if previous.id is not null and previous.database_bytes > 0 then
    db_growth_pct := (((usage->'database'->>'bytes')::numeric-previous.database_bytes)/previous.database_bytes)*100;
  end if;
  if previous.id is not null and previous.storage_bytes > 0 then
    storage_growth_pct := (((usage->'storage'->>'bytes')::numeric-previous.storage_bytes)/previous.storage_bytes)*100;
  end if;

  select count(*) into orphan_links
  from public.evidence_iec_links l
  left join public.evidence e on e.id=l.evidence_id
  left join public.iecs i on i.id=l.iec_id
  where e.id is null or i.id is null;

  select count(*) into orphan_state_history
  from public.iec_state_history h
  left join public.iecs i on i.id=h.iec_id
  where i.id is null;

  select count(*) into orphan_evidence_history
  from public.evidence_history h
  left join public.evidence e on e.id=h.evidence_id
  where e.id is null;

  select count(*) into orphan_evolution_events
  from public.knowledge_evolution_events e
  left join public.iecs i on i.id=e.iec_id
  where e.iec_id is not null and i.id is null;

  select count(*) into graph_nodes from public.knowledge_nodes;
  select count(*) into graph_edges from public.knowledge_edges;
  select count(*) into orphan_graph_edges
  from public.knowledge_edges e
  left join public.knowledge_nodes s on s.id=e.source_node_id
  left join public.knowledge_nodes t on t.id=e.target_node_id
  where s.id is null or t.id is null;

  if orphan_links > 0 or orphan_state_history > 0 or orphan_evidence_history > 0 or orphan_evolution_events > 0 then
    epistemic_status := 'WARNING';
  end if;

  if orphan_links > 0 or orphan_state_history > 0 or orphan_evidence_history > 0 or orphan_evolution_events > 0 then
    persistence_status := 'WARNING';
  end if;

  if orphan_graph_edges > 0 then
    graph_status := 'CRITICAL';
  elsif graph_nodes > 0 and graph_edges = 0 then
    graph_status := 'WARNING';
  end if;

  db_status := case when db_pct >= 100 then 'CRITICAL' when db_pct >= 90 then 'WARNING' else 'HEALTHY' end;
  storage_status := case when storage_pct >= 100 then 'CRITICAL' when storage_pct >= 90 then 'WARNING' else 'HEALTHY' end;

  if db_status='CRITICAL' then score:=score-40; elsif db_status='WARNING' then score:=score-15; end if;
  if storage_status='CRITICAL' then score:=score-40; elsif storage_status='WARNING' then score:=score-15; end if;
  if coalesce(db_growth_pct,0)>=40 then score:=score-25; elsif coalesce(db_growth_pct,0)>=20 then score:=score-10; end if;
  if coalesce(storage_growth_pct,0)>=40 then score:=score-25; elsif coalesce(storage_growth_pct,0)>=20 then score:=score-10; end if;
  if epistemic_status='WARNING' then score:=score-15; end if;
  if persistence_status='WARNING' then score:=score-10; end if;
  if graph_status='CRITICAL' then score:=score-25; elsif graph_status='WARNING' then score:=score-10; end if;
  score:=greatest(0,score);

  if db_status='CRITICAL' or storage_status='CRITICAL' or graph_status='CRITICAL'
     or coalesce(db_growth_pct,0)>=40 or coalesce(storage_growth_pct,0)>=40 then
    overall:='CRITICAL';
  elsif db_status='WARNING' or storage_status='WARNING' or epistemic_status='WARNING'
     or persistence_status='WARNING' or graph_status='WARNING'
     or coalesce(db_growth_pct,0)>=20 or coalesce(storage_growth_pct,0)>=20 then
    overall:='WARNING';
  end if;

  integrity := jsonb_build_object(
    'orphan_evidence_iec_links',orphan_links,
    'orphan_iec_state_history',orphan_state_history,
    'orphan_evidence_history',orphan_evidence_history,
    'orphan_knowledge_evolution_events',orphan_evolution_events,
    'orphan_knowledge_graph_edges',orphan_graph_edges,
    'knowledge_nodes',graph_nodes,
    'knowledge_edges',graph_edges
  );

  evaluation := jsonb_build_object(
    'database_usage_percent',round(db_pct,2),
    'storage_usage_percent',round(storage_pct,2),
    'database_growth_percent',case when db_growth_pct is null then null else round(db_growth_pct,2) end,
    'storage_growth_percent',case when storage_growth_pct is null then null else round(storage_growth_pct,2) end,
    'history_available',previous.id is not null,
    'epistemic_health',epistemic_status,
    'persistence_health',persistence_status,
    'graph_health',graph_status,
    'integrity',integrity
  );

  insert into public.infrastructure_usage_snapshots (
    database_bytes,database_quota_bytes,storage_bytes,storage_quota_bytes,storage_objects,
    iecs,evidence,evidence_iec_links,iec_state_history,knowledge_evolution_events,evidence_history,
    database_status,storage_status,health_score,overall_status,evaluation,
    epistemic_health,persistence_health,graph_health,integrity_issues
  ) values (
    (usage->'database'->>'bytes')::bigint,(usage->'database'->>'quota_bytes')::bigint,
    (usage->'storage'->>'bytes')::bigint,(usage->'storage'->>'quota_bytes')::bigint,
    (usage->'storage'->>'objects')::bigint,
    coalesce((usage->'epistemic'->>'iecs')::bigint,0),coalesce((usage->'epistemic'->>'evidence')::bigint,0),
    coalesce((usage->'epistemic'->>'evidence_iec_links')::bigint,0),coalesce((usage->'epistemic'->>'iec_state_history')::bigint,0),
    coalesce((usage->'epistemic'->>'knowledge_evolution_events')::bigint,0),coalesce((usage->'epistemic'->>'evidence_history')::bigint,0),
    db_status,storage_status,score,overall,evaluation,epistemic_status,persistence_status,graph_status,integrity
  ) returning id into snapshot_id;

  return jsonb_build_object('snapshot_id',snapshot_id,'status',overall,'health_score',score,'evaluation',evaluation,'measured_at',now());
end;
$function$;


CREATE OR REPLACE FUNCTION public.trg_sync_kalatrace_watchdog_events()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
begin
  perform private.sync_kalatrace_watchdog_events(new.id);
  return new;
end;
$function$;


DROP TRIGGER IF EXISTS trg_sync_kalatrace_watchdog_events
  ON public.infrastructure_usage_snapshots;
CREATE TRIGGER trg_sync_kalatrace_watchdog_events
  AFTER INSERT OR UPDATE ON public.infrastructure_usage_snapshots
  FOR EACH ROW EXECUTE FUNCTION public.trg_sync_kalatrace_watchdog_events();

-- Transitional wrappers are tightened to the infrastructure-admin allowlist
-- by migration 20261011153829_harden_infrastructure_watchdog_admin_access.sql.
CREATE OR REPLACE FUNCTION public.get_kalatrace_infrastructure_usage()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
BEGIN
  IF (SELECT auth.uid()) IS NULL THEN
    RAISE EXCEPTION 'authentication required' USING ERRCODE = '28000';
  END IF;
  RETURN private.collect_kalatrace_infrastructure_usage();
END;
$function$;

CREATE OR REPLACE FUNCTION public.run_kalatrace_watchdog()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
BEGIN
  IF (SELECT auth.uid()) IS NULL THEN
    RAISE EXCEPTION 'authentication required' USING ERRCODE = '28000';
  END IF;
  RETURN private.run_kalatrace_watchdog();
END;
$function$;

REVOKE ALL ON FUNCTION private.collect_kalatrace_infrastructure_usage() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION private.sync_kalatrace_watchdog_events(bigint) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION private.run_kalatrace_watchdog() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.trg_sync_kalatrace_watchdog_events() FROM PUBLIC, anon, authenticated;

REVOKE ALL ON FUNCTION public.get_kalatrace_infrastructure_usage() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.get_kalatrace_infrastructure_usage() TO authenticated;
REVOKE ALL ON FUNCTION public.run_kalatrace_watchdog() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.run_kalatrace_watchdog() TO authenticated;
