-- Controlled coding-agent metadata and atomic CMC timeline append.
-- No secrets are stored here.

create or replace function public.append_cmc_mission_timeline(
  p_mission_id uuid,
  p_event jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_row public.cmc_missions%rowtype;
  v_timeline jsonb;
begin
  select * into v_row
  from public.cmc_missions
  where id = p_mission_id
    and owner_id = (SELECT auth.uid())
  for update;

  if not found then
    raise exception 'Mission not found or not owned by current user';
  end if;

  v_timeline := coalesce(v_row.timeline, '[]'::jsonb) || jsonb_build_array(p_event);

  update public.cmc_missions
  set timeline = v_timeline,
      updated_at = pg_catalog.now()
  where id = p_mission_id;

  return v_timeline;
end;
$$;

revoke all on function public.append_cmc_mission_timeline(uuid,jsonb) from public, anon;
grant execute on function public.append_cmc_mission_timeline(uuid,jsonb) to authenticated;

-- Explicitly document the controlled code operation family at the database level.
comment on column public.local_agent_tasks.execution_spec is
  'Approved execution specification. Supported runtime operations are allowlisted by the Local Agent sandbox; code changes use code_apply with explicit file operations.';
