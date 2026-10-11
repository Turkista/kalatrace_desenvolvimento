-- RECONSTRUCTED from the live Supabase catalog for remote version 20260824234247.
-- Original source was absent from Git history. The trigger function is hardened further
-- than the observed historical version by using an empty search_path and qualified names.

CREATE INDEX IF NOT EXISTS iec_nodes_node_id_idx ON public.iec_nodes(node_id);

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
