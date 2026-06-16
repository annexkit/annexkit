"""initial schema — tenants, api_keys, audit_logs, spans + APPEND-ONLY trigger

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-07 12:00:00.000000

This migration ships every table the collector needs in v0.1 and
installs the Postgres ``annexkit_audit_logs_immutable`` trigger that
makes UPDATE/DELETE on ``audit_logs`` impossible at the DB layer.

For SQLite (used in unit tests) the trigger creation is skipped — the
service-level guarantee in :mod:`app.services.audit_service` is enough
because tests don't exercise raw SQL paths.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET, JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    # ----- tenants --------------------------------------------------------
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=False)

    # ----- api_keys -------------------------------------------------------
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("key_prefix", sa.String(20), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("last_used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("key_hash", name="uq_api_keys_key_hash"),
    )
    op.create_index("ix_api_keys_tenant_id", "api_keys", ["tenant_id"])
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)

    # ----- audit_logs (APPEND-ONLY) --------------------------------------
    big_int_type = sa.BigInteger() if is_postgres else sa.Integer()
    json_type = JSONB() if is_postgres else sa.JSON()
    inet_type = INET() if is_postgres else sa.String(45)

    op.create_table(
        "audit_logs",
        sa.Column("id", big_int_type, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("details", json_type, nullable=True),
        sa.Column("ip_address", inet_type, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        comment="APPEND-ONLY. Do not UPDATE or DELETE from this table.",
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index(
        "ix_audit_logs_tenant_id_created_at",
        "audit_logs",
        ["tenant_id", "created_at"],
    )

    # ----- spans ----------------------------------------------------------
    op.create_table(
        "spans",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # SDK-side identity
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("span_id", sa.String(32), nullable=False),
        sa.Column("parent_span_id", sa.String(32), nullable=True),
        # System
        sa.Column("system_id", sa.String(100), nullable=False),
        sa.Column("deployment", sa.String(50), nullable=False, server_default="prod"),
        # AI Act
        sa.Column("risk_tier", sa.String(20), nullable=False, server_default="auto"),
        sa.Column("purpose", sa.String(500), nullable=True),
        # Timing
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("ended_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        # Model
        sa.Column("model_provider", sa.String(50), nullable=True),
        sa.Column("model_name", sa.String(100), nullable=True),
        sa.Column("model_version", sa.String(100), nullable=True),
        # Hashes
        sa.Column("input_hash", sa.String(64), nullable=True),
        sa.Column("input_chars", sa.Integer(), nullable=True),
        sa.Column("output_hash", sa.String(64), nullable=True),
        sa.Column("output_chars", sa.Integer(), nullable=True),
        # Sources + extras
        sa.Column("sources", json_type, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("user_role", sa.String(50), nullable=True),
        sa.Column("error", sa.String(500), nullable=True),
        sa.Column("extras", json_type, nullable=False, server_default=sa.text("'{}'")),
        # SDK provenance
        sa.Column("sdk_version", sa.String(20), nullable=False),
        sa.Column("sdk_lang", sa.String(20), nullable=False, server_default="python"),
        # Server-side
        sa.Column(
            "received_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_spans_tenant_id", "spans", ["tenant_id"])
    op.create_index("ix_spans_trace_id", "spans", ["trace_id"])
    op.create_index("ix_spans_system_id", "spans", ["system_id"])
    op.create_index(
        "ix_spans_tenant_system_received",
        "spans",
        ["tenant_id", "system_id", "received_at"],
    )
    op.create_index(
        "ix_spans_tenant_trace",
        "spans",
        ["tenant_id", "trace_id"],
    )

    # ----- APPEND-ONLY trigger (Postgres only) ---------------------------
    if is_postgres:
        op.execute(
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
        op.execute(
            """
            CREATE TRIGGER annexkit_audit_logs_immutability
            BEFORE UPDATE OR DELETE ON audit_logs
            FOR EACH ROW EXECUTE FUNCTION annexkit_audit_logs_immutable();
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.execute("DROP TRIGGER IF EXISTS annexkit_audit_logs_immutability ON audit_logs;")
        op.execute("DROP FUNCTION IF EXISTS annexkit_audit_logs_immutable();")

    op.drop_table("spans")
    op.drop_table("audit_logs")
    op.drop_table("api_keys")
    op.drop_table("tenants")
