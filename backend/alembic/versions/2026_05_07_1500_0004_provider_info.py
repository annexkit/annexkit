"""ai_systems.provider_info — JSONB for Annex IV §1(b)-(d) provider details

Revision ID: 0004_provider_info
Revises: 0003_ai_systems
Create Date: 2026-05-07 15:00:00.000000

The EU AI Act Annex IV §1 requires the technical documentation to
include "the persons responsible" (sub-clause b), the "version of the
system" (c), and the software/hardware environment in which the system
is intended to run (d).

These are free-form, provider-specific, and rarely structured the same
way across providers. A single ``provider_info`` JSONB column gives us
flexibility without committing to a brittle schema. The Pydantic
``ProviderInfo`` model in ``schemas/ai_system.py`` defines the
recommended shape — additional keys are accepted and round-tripped.

Backfill: existing rows get an empty ``{}`` so the column is
non-nullable (cleaner queries downstream).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_provider_info"
down_revision: str | Sequence[str] | None = "0003_ai_systems"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    json_type = JSONB() if is_postgres else sa.JSON()

    op.add_column(
        "ai_systems",
        sa.Column(
            "provider_info",
            json_type,
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("ai_systems", "provider_info")
