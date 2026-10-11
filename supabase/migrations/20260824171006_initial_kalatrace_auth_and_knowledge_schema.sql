-- RECONSTRUCTED baseline from the live Supabase catalog.
-- The original SQL source for remote version 20260824171006 was not present in Git history.
-- This reconstruction captures the current baseline table shapes needed by later migrations;
-- it is not claimed to be a byte-for-byte recovery of the original SQL.

CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name text,
  role text NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'agent')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.iecs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name text NOT NULL,
  statement text NOT NULL,
  methodology jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.knowledge_nodes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  node_type text NOT NULL,
  label text NOT NULL,
  description text,
  properties jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.knowledge_edges (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  source_node_id uuid NOT NULL REFERENCES public.knowledge_nodes(id) ON DELETE CASCADE,
  target_node_id uuid NOT NULL REFERENCES public.knowledge_nodes(id) ON DELETE CASCADE,
  edge_type text NOT NULL,
  properties jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT knowledge_edges_no_self_loop CHECK (source_node_id <> target_node_id)
);

CREATE TABLE IF NOT EXISTS public.iec_nodes (
  iec_id uuid NOT NULL REFERENCES public.iecs(id) ON DELETE CASCADE,
  node_id uuid NOT NULL REFERENCES public.knowledge_nodes(id) ON DELETE CASCADE,
  relation_type text NOT NULL DEFAULT 'derived_from',
  PRIMARY KEY (iec_id, node_id, relation_type)
);

CREATE TABLE IF NOT EXISTS public.predictions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  model_name text,
  input_data jsonb NOT NULL DEFAULT '{}'::jsonb,
  prediction jsonb NOT NULL DEFAULT '{}'::jsonb,
  confidence numeric,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.simulations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name text NOT NULL,
  parameters jsonb NOT NULL DEFAULT '{}'::jsonb,
  results jsonb NOT NULL DEFAULT '{}'::jsonb,
  status text NOT NULL DEFAULT 'created',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS iecs_owner_idx ON public.iecs(owner_id);
CREATE INDEX IF NOT EXISTS knowledge_nodes_owner_idx ON public.knowledge_nodes(owner_id);
CREATE INDEX IF NOT EXISTS knowledge_edges_owner_idx ON public.knowledge_edges(owner_id);
CREATE INDEX IF NOT EXISTS knowledge_edges_source_idx ON public.knowledge_edges(source_node_id);
CREATE INDEX IF NOT EXISTS knowledge_edges_target_idx ON public.knowledge_edges(target_node_id);
CREATE INDEX IF NOT EXISTS predictions_owner_idx ON public.predictions(owner_id);
CREATE INDEX IF NOT EXISTS simulations_owner_idx ON public.simulations(owner_id);

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
BEGIN
  INSERT INTO public.profiles (id, display_name)
  VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data ->> 'full_name', NEW.email));
  RETURN NEW;
END;
$function$;

REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
