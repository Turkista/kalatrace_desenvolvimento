# Archived Supabase migration sources

These files are preserved for audit and are not executable migrations.

- The original workspace/CMC/agent SQL files are archived here because their versions were not present in the remote migration history. The corrected versions were applied and registered under new version prefixes.
- `20261008170000_add_infrastructure_usage_rpc.sql` is an older RPC implementation that did not match the live remote schema and could overwrite the hardened RPC if placed in the active migration folder.
- The unregistered legacy epistemic migration is preserved separately under `_archive/supabase_migrations/` because it could run before the `evidence` table exists in a clean reset.

Do not copy these files back into `supabase/migrations/` without reviewing version history, dependencies, and the current remote schema. Some active migration files are explicitly reconstructed from the live catalog and are not byte-for-byte originals.
