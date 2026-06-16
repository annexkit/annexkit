"""Canonical ORM model — the one data contract both apps store against.

LANDS HERE (Step 3): System (registry record) + Classification (verdict) +
Evidence (AnnexKit Span) + AuditLog + common. Tenancy is org_id/Organization
(AnnexKit tenant_id maps onto it). ORM models never leave the service layer."""
