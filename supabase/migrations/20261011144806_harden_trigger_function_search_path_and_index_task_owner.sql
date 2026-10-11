-- Harden trigger functions and index the local agent task owner foreign key.
-- Applied to Supabase project kedyzontvnailtwpacvz as migration
-- 20261011144806_harden_trigger_function_search_path_and_index_task_owner.
-- Function bodies intentionally preserve their existing behavior.

CREATE OR REPLACE FUNCTION public.set_evidence_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = ''
AS $function$
BEGIN
  NEW.updated_at = pg_catalog.now();
  RETURN NEW;
END;
$function$;

CREATE OR REPLACE FUNCTION public.set_research_form_records_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = ''
AS $function$
BEGIN
  NEW.updated_at = pg_catalog.now();
  RETURN NEW;
END;
$function$;

CREATE INDEX IF NOT EXISTS local_agent_tasks_owner_id_idx
  ON public.local_agent_tasks (owner_id);
