-- Remove the legacy duplicate permissive evidence policy.
-- Canonical policy: evidence_own.
drop policy if exists evidence_all_own on public.evidence;
