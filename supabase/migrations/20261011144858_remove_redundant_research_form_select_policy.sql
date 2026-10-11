-- The ALL policy already permits SELECT only when owner_id = auth.uid().
-- The additional SELECT policy is a strict subset and therefore redundant
-- under PostgreSQL's permissive-policy OR semantics.
DROP POLICY IF EXISTS research_form_records_project_select
  ON public.research_form_records;
