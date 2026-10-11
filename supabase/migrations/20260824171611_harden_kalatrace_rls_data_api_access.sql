-- RECONSTRUCTED from the live Supabase catalog for remote version 20260824171611.
-- Original source was absent from Git history. Policies mirror the observed ownership model.

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.iecs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.iec_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.simulations ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.profiles, public.iecs, public.knowledge_nodes,
  public.knowledge_edges, public.iec_nodes, public.predictions, public.simulations
  FROM anon;

GRANT SELECT, INSERT, UPDATE, DELETE ON public.profiles, public.iecs,
  public.knowledge_nodes, public.knowledge_edges, public.iec_nodes,
  public.predictions, public.simulations TO authenticated;

DROP POLICY IF EXISTS profiles_select_own ON public.profiles;
CREATE POLICY profiles_select_own ON public.profiles
  FOR SELECT TO authenticated USING ((SELECT auth.uid()) = id);
DROP POLICY IF EXISTS profiles_update_own ON public.profiles;
CREATE POLICY profiles_update_own ON public.profiles
  FOR UPDATE TO authenticated
  USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);

DROP POLICY IF EXISTS iecs_all_own ON public.iecs;
CREATE POLICY iecs_all_own ON public.iecs
  FOR ALL TO authenticated
  USING ((SELECT auth.uid()) = owner_id)
  WITH CHECK ((SELECT auth.uid()) = owner_id);

DROP POLICY IF EXISTS knowledge_nodes_all_own ON public.knowledge_nodes;
CREATE POLICY knowledge_nodes_all_own ON public.knowledge_nodes
  FOR ALL TO authenticated
  USING ((SELECT auth.uid()) = owner_id)
  WITH CHECK ((SELECT auth.uid()) = owner_id);

DROP POLICY IF EXISTS knowledge_edges_all_own ON public.knowledge_edges;
CREATE POLICY knowledge_edges_all_own ON public.knowledge_edges
  FOR ALL TO authenticated
  USING ((SELECT auth.uid()) = owner_id)
  WITH CHECK ((SELECT auth.uid()) = owner_id);

DROP POLICY IF EXISTS predictions_all_own ON public.predictions;
CREATE POLICY predictions_all_own ON public.predictions
  FOR ALL TO authenticated
  USING ((SELECT auth.uid()) = owner_id)
  WITH CHECK ((SELECT auth.uid()) = owner_id);

DROP POLICY IF EXISTS simulations_all_own ON public.simulations;
CREATE POLICY simulations_all_own ON public.simulations
  FOR ALL TO authenticated
  USING ((SELECT auth.uid()) = owner_id)
  WITH CHECK ((SELECT auth.uid()) = owner_id);

DROP POLICY IF EXISTS iec_nodes_select_own ON public.iec_nodes;
CREATE POLICY iec_nodes_select_own ON public.iec_nodes
  FOR SELECT TO authenticated
  USING (EXISTS (
    SELECT 1 FROM public.iecs i
    WHERE i.id = iec_nodes.iec_id AND i.owner_id = (SELECT auth.uid())
  ));

DROP POLICY IF EXISTS iec_nodes_insert_own ON public.iec_nodes;
CREATE POLICY iec_nodes_insert_own ON public.iec_nodes
  FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.iecs i
      WHERE i.id = iec_nodes.iec_id AND i.owner_id = (SELECT auth.uid())
    )
    AND EXISTS (
      SELECT 1 FROM public.knowledge_nodes n
      WHERE n.id = iec_nodes.node_id AND n.owner_id = (SELECT auth.uid())
    )
  );

DROP POLICY IF EXISTS iec_nodes_delete_own ON public.iec_nodes;
CREATE POLICY iec_nodes_delete_own ON public.iec_nodes
  FOR DELETE TO authenticated
  USING (EXISTS (
    SELECT 1 FROM public.iecs i
    WHERE i.id = iec_nodes.iec_id AND i.owner_id = (SELECT auth.uid())
  ));

CREATE OR REPLACE FUNCTION public.rls_auto_enable()
RETURNS event_trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = 'pg_catalog'
AS $function$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN
    SELECT *
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      AND object_type IN ('table', 'partitioned table')
  LOOP
    IF cmd.schema_name IS NOT NULL
       AND cmd.schema_name IN ('public')
       AND cmd.schema_name NOT IN ('pg_catalog', 'information_schema')
       AND cmd.schema_name NOT LIKE 'pg_toast%'
       AND cmd.schema_name NOT LIKE 'pg_temp%' THEN
      BEGIN
        EXECUTE format('ALTER TABLE IF EXISTS %s ENABLE ROW LEVEL SECURITY', cmd.object_identity);
        RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      EXCEPTION WHEN OTHERS THEN
        RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      END;
    ELSE
      RAISE LOG 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)',
        cmd.object_identity, cmd.schema_name;
    END IF;
  END LOOP;
END;
$function$;

REVOKE ALL ON FUNCTION public.rls_auto_enable() FROM PUBLIC, anon, authenticated;
DROP EVENT TRIGGER IF EXISTS ensure_rls;
CREATE EVENT TRIGGER ensure_rls
  ON ddl_command_end
  EXECUTE FUNCTION public.rls_auto_enable();
