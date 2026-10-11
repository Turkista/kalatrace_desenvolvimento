-- Close the INSERT path that could create already-approved tasks directly.
CREATE OR REPLACE FUNCTION public.guard_local_agent_task_mutations()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = ''
AS $function$
BEGIN
  IF TG_OP = 'INSERT' THEN
    IF NEW.status NOT IN ('queued', 'planning') THEN
      RAISE EXCEPTION 'New tasks must start queued or planning';
    END IF;
    IF NEW.approved_by IS NOT NULL OR NEW.approved_at IS NOT NULL THEN
      RAISE EXCEPTION 'New tasks cannot include approval metadata';
    END IF;
    RETURN NEW;
  END IF;

  IF NEW.owner_id IS DISTINCT FROM OLD.owner_id THEN
    RAISE EXCEPTION 'Task ownership cannot be changed';
  END IF;

  IF OLD.approved_at IS NOT NULL
     AND NEW.execution_spec IS DISTINCT FROM OLD.execution_spec THEN
    RAISE EXCEPTION 'Execution specification is immutable after approval';
  END IF;

  IF OLD.approved_at IS NOT NULL
     AND (NEW.approved_by IS DISTINCT FROM OLD.approved_by
          OR NEW.approved_at IS DISTINCT FROM OLD.approved_at) THEN
    RAISE EXCEPTION 'Approval metadata is immutable after approval';
  END IF;

  IF OLD.approved_at IS NULL AND NEW.approved_at IS NOT NULL
     AND NEW.status IS DISTINCT FROM 'approved' THEN
    RAISE EXCEPTION 'Approval metadata can only be set during approval';
  END IF;

  IF NEW.status = 'approved' AND OLD.status IS DISTINCT FROM 'approved' THEN
    IF NEW.approved_by IS DISTINCT FROM (SELECT auth.uid()) OR NEW.approved_at IS NULL THEN
      RAISE EXCEPTION 'Approval metadata must identify the approving user';
    END IF;

    IF NOT EXISTS (
      SELECT 1
      FROM public.projects p
      LEFT JOIN public.project_memberships pm
        ON pm.project_id = p.id AND pm.user_id = (SELECT auth.uid())
      WHERE p.id = NEW.project_id
        AND (
          p.owner_id = (SELECT auth.uid())
          OR pm.role IN ('owner', 'administrator', 'developer', 'operator')
        )
    ) THEN
      RAISE EXCEPTION 'Only authorized project members may approve executable tasks';
    END IF;
  END IF;

  IF NEW.status = 'running' AND OLD.status NOT IN ('approved', 'running') THEN
    RAISE EXCEPTION 'A task must be approved before it can run';
  END IF;

  RETURN NEW;
END;
$function$;

REVOKE ALL ON FUNCTION public.guard_local_agent_task_mutations() FROM PUBLIC, anon, authenticated;
DROP TRIGGER IF EXISTS guard_local_agent_task_mutations ON public.local_agent_tasks;
CREATE TRIGGER guard_local_agent_task_mutations
  BEFORE INSERT OR UPDATE ON public.local_agent_tasks
  FOR EACH ROW EXECUTE FUNCTION public.guard_local_agent_task_mutations();