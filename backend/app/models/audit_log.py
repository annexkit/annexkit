"""AuditLog — the immutable audit trail.

**This table is append-only.** No code path anywhere in the application
may DELETE or UPDATE rows. This is the evidence trail shown to
regulators during an AI Act audit. Mutability would invalidate the
whole premise.

Enforcement layers (defence in depth):
    1. The service layer (`app/services/audit_service.py`) only INSERTs.
    2. No repository/service exposes delete/update methods.
    3. A Postgres trigger (installed in the initial migration) raises on
       any DELETE/UPDATE against this table at the DB level.

Cardinality: this table grows fast. Every domain event writes a row.
Use BIGSERIAL (monotonically increasing integer) for the PK — cheaper
than UUIDs for append-only logs, and we never need to expose the id.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, BigInteger, Index, Integer, String, Uuid, text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import created_at_column


class AuditLog(Base):
    """One event = one row. Never updated, never deleted."""

    __tablename__ = "audit_logs"

    # BIGSERIAL — monotonic across the whole DB. Cheaper than UUID for
    # a write-heavy log and keeps events naturally ordered.
    #
    # Dialect variant: BigInteger in Postgres, plain Integer on SQLite.
    # SQLite reserves autoincrement semantics for the literal type
    # `INTEGER PRIMARY KEY` (rowid alias) — `BIGINT` disables it. Tests
    # run on SQLite, so we downgrade there. Still 32-bit signed (~2.1B
    # rows); tests never come close.
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer(), "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    # Tenant that owns the event. Not a FK because we want the log to
    # survive even if a tenant row is (in theory) deleted. Index for
    # per-tenant queries.
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False, index=True
    )

    # Actor — also not a FK for the same survivability reason. Currently
    # always None for SDK-driven spans (the actor is "tenant API key");
    # populated once dashboard auth lands in M4.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )

    # Dotted-string convention: `<resource>.<verb>` e.g.
    # ``span.ingested``, ``api_key.revoked``, ``annex_iv.generated``.
    # Kept as a plain string so we don't need a migration every time we
    # add a new event.
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Polymorphic subject: action acts on an entity of `entity_type` with
    # primary key `entity_id`. Allows joining to any of our domain tables.
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )

    # Full payload of the change. Serialises whatever the service wrote:
    # the create payload, the diff on update, the whole classification
    # response, etc. JSONB in Postgres (indexable); plain JSON on SQLite.
    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), nullable=True
    )

    # Source IP of the request that triggered the event. Hardened against
    # forged X-Forwarded-For via trusted proxy config (future).
    # INET in Postgres (validates the format), plain string elsewhere.
    ip_address: Mapped[str | None] = mapped_column(
        String(45).with_variant(INET(), "postgresql"), nullable=True
    )

    created_at: Mapped[datetime] = created_at_column()

    # Composite index to make "show me tenant X's activity in the last
    # hour" fast without a full scan.
    __table_args__ = (
        Index("ix_audit_logs_tenant_id_created_at", "tenant_id", "created_at"),
        {"comment": "APPEND-ONLY. Do not UPDATE or DELETE from this table."},
    )


# --- Defence-in-depth DDL (applied in the initial migration) ---------------
# A plain SQLAlchemy event listener isn't enough because raw SQL from a
# psql shell would bypass it. The real enforcement is a BEFORE UPDATE OR
# DELETE trigger at the Postgres level. The initial migration installs it;
# see ``alembic/versions/*_initial.py``.
AUDIT_LOG_IMMUTABILITY_FN_SQL = text(
    """
    CREATE OR REPLACE FUNCTION annexkit_audit_logs_immutable()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'audit_logs is append-only; % is not allowed',
            TG_OP;
    END;
    $$ LANGUAGE plpgsql;
    """
)

AUDIT_LOG_IMMUTABILITY_TRIGGER_SQL = text(
    """
    CREATE TRIGGER annexkit_audit_logs_immutability
    BEFORE UPDATE OR DELETE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION annexkit_audit_logs_immutable();
    """
)
