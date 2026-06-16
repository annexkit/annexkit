"""leads table — captured emails from public free tools

Revision ID: 0005_leads
Revises: 0004_provider_info
Create Date: 2026-05-23 17:30:00.000000

Public no-auth free tools (Annex IV generator, classifier flowchart,
etc.) capture an email per generation as marketing lead. The lead is
stored separately from tenants/api_keys — these users have no AnnexKit
account yet. A future workflow may upgrade a lead to a tenant when
they sign up; for now leads is a write-mostly table with read access
limited to admin scripts.

Schema is intentionally minimal: just enough to follow up on the
prospect (email + which tool + what they were trying to classify).
Plaintext personal data minimisation: we do NOT store the full form
content — only the purpose and resolved tier, which is what a sales
follow-up actually uses.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET, JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_leads"
down_revision: str | Sequence[str] | None = "0004_provider_info"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"
    json_type = JSONB() if is_postgres else sa.JSON()
    inet_type = INET() if is_postgres else sa.String(45)

    op.create_table(
        "leads",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        # Email is the only required identifying field. Length 255 is the
        # de-facto maximum across MTAs (RFC-compliant local-part 64 +
        # @ + domain 253 = 318, but real-world MTAs cap at 254-255).
        sa.Column("email", sa.String(255), nullable=False),
        # Which tool captured the lead. Indexed because we'll want
        # "show me everyone who tried the Annex IV generator last week".
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column(
            "captured_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        # The system the user was classifying — used for sales follow-up
        # ("you tried our HR-screener Annex IV generator, here's how a
        # Pro tier handles 50 systems"). Text not String() because
        # there's no good cap and we don't index on it.
        sa.Column("system_purpose", sa.Text(), nullable=True),
        # Tier resolved by the classifier ("high" / "limited" etc.).
        # Useful for segmenting outreach by buyer urgency.
        sa.Column("system_tier", sa.String(20), nullable=True),
        # The Annex III / prohibited / transparency ids the user picked.
        # JSONB so we can later "show me leads who tried §4 employment".
        sa.Column(
            "declared_categories",
            json_type,
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        # Optional IP for fraud/abuse review. Forwarded-For trust set
        # at the reverse proxy layer; here it's just the value the auth
        # dep saw.
        sa.Column("ip_address", inet_type, nullable=True),
    )
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_index("ix_leads_source", "leads", ["source"])
    op.create_index(
        "ix_leads_source_captured_at",
        "leads",
        ["source", "captured_at"],
    )


def downgrade() -> None:
    op.drop_table("leads")
