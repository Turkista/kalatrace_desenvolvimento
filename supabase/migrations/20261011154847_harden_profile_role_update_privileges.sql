-- Prevent self-service profile updates from changing authorization fields.
REVOKE UPDATE ON TABLE public.profiles FROM PUBLIC, anon, authenticated;
REVOKE UPDATE (id, display_name, role, created_at, updated_at)
  ON TABLE public.profiles FROM PUBLIC, anon, authenticated;
GRANT UPDATE (display_name) ON TABLE public.profiles TO authenticated;
