"""Lead ORM — captured emails from public free tools.

Write-mostly table. Each public free tool (Annex IV generator,
classifier flowchart, etc.) writes one row per generation with the
prospect's email + minimal context. Reads are admin-side (export to
mailing list, segment by source/tier).

These rows are NOT tenants — the email belongs to someone without an
AnnexKit account. A future workflow may upgrade a lead to a tenant on
sign-up; until then the table stands alone.

See ``alembic/versions/2026_05_23_*_0005_leads.py`` for the schema
rationale.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, String, Text
from sqlalchemy.dialects.postgresql import INET as PG_INET
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import created_at_column, uuid_pk


class Lead(Base):
    """One prospect email captured by a public free tool."""

    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = uuid_pk()

    # Indexed so support can answer "do we have this email already?"
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Which tool captured it — e.g. ``"annex-iv-generator"``,
    # ``"classifier-flowchart"``. Indexed for segmenting outreach.
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Mirrors created_at convention from other tables.
    captured_at: Mapped[datetime] = created_at_column()

    # Free-form (the user typed it). Cap not enforced at DB layer (TEXT)
    # so we don't reject pasted long descriptions; the API schema caps
    # it at 1000 chars.
    system_purpose: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Resolved risk tier from the deterministic classifier. Useful for
    # sales segmenting ("HIGH-tier leads are the buyers").
    system_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # List of {annex_iii / prohibited / transparency} ids the user
    # declared. JSONB on Postgres for indexable queries
    # ("show me leads who picked §4 employment"); JSON on SQLite.
    declared_categories: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    # IP at request time. Behind Cloudflare + Caddy this is the value
    # observed by the app, which depends on uvicorn's
    # ``--forwarded-allow-ips`` config. Used only for abuse review.
    ip_address: Mapped[str | None] = mapped_column(
        String(45).with_variant(PG_INET(), "postgresql"),
        nullable=True,
    )

    # ORM dictionary form for API responses.
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "email": self.email,
            "source": self.source,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
            "system_purpose": self.system_purpose,
            "system_tier": self.system_tier,
            "declared_categories": list(self.declared_categories or []),
        }
