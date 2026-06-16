"""Append-only audit service — a CLAUDE.md non-negotiable.

LANDS HERE (Step 3): the superset audit_service (record() + record_for_actor()
for consultancy multi-client). There is NO code path that UPDATEs or DELETEs
audit_logs. Migrations touching this table must be additive only."""
