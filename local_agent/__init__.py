"""Local Agent runtime connector for KALATRACE.

The connector is intentionally conservative: it authenticates as a normal
Supabase user, polls approved tasks, and reports lifecycle state. Code changes
must still be performed by an explicit execution handler/sandbox.
"""
