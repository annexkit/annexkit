"""ai_systems table — per-tenant declaration + classified tier

Revision ID: 0003_ai_systems
Revises: 0002_span_idempotency
Create Date: 2026-05-07 14:00:00.000000

Stores one row per (tenant_id, system_id) describing what an AI system
does + which Annex III categories / Article 5 prohibited practices /
Article 50 transparency triggers apply, and the resolved risk tier
computed by :mod:`app.services.risk_engine`.

Span ingest joins this table when the SDK sends ``risk_tier="auto"`` to
populate the span's effective tier.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_ai_systems"
down_revision: str | Sequence[str] | None = "0002_span_idempotency"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    json_type = JSONB() if is_postgres else sa.JSON()

    op.create_table(
        "ai_systems",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("system_id", sa.String(100), nullable=False),
        # Declarations
        sa.Column("purpose", sa.String(500), nullable=True),
        sa.Column(
            "annex_iii_categories",
            json_type,
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column(
            "prohibited_practices",
            json_type,
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column(
            "transparency_triggers",
            json_type,
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column("is_gpai", sa.Boolean(), nullable=False, server_default=sa.false()),
        # Resolved
        sa.Column("risk_tier", sa.String(20), nullable=False),
        sa.Column("rules_version", sa.String(20), nullable=False),
        sa.Column(
            "reasoning",
            json_type,
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column("classified_at", sa.TIMESTAMP(timezone=True), nullable=False),
        # Timestamps
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
        sa.UniqueConstraint(
            "tenant_id", "system_id", name="uq_ai_systems_tenant_system"
        ),
    )
    op.create_index("ix_ai_systems_tenant_id", "ai_systems", ["tenant_id"])
    op.create_index("ix_ai_systems_system_id", "ai_systems", ["system_id"])


def downgrade() -> None:
    op.drop_table("ai_systems")
