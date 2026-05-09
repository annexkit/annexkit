"""AISystem ORM — per-tenant declaration of an AI system + classified tier.

A row in this table is a tenant's *declaration* about one AI system
(uniquely identified by ``system_id`` within their tenancy):

  * What the system does (``purpose``).
  * Which EU AI Act Annex III categories it falls under (e.g.
    ``["credit_scoring"]``).
  * Whether any prohibited Article 5 practices apply.
  * Whether any Article 50 transparency triggers apply.
  * Whether it's a GPAI (general-purpose AI) model.

On insert/update, the deterministic risk engine
(:mod:`app.services.risk_engine`) computes:

  * ``risk_tier`` — one of ``unacceptable | high | limited | minimal``.
  * ``reasoning`` — the list of triggered rules with their Article refs.
  * ``rules_version`` — the version stamp from ``annex_iii.json`` so an
    auditor can pin "what ruleset said this was high-risk?".

When a span arrives with ``risk_tier="auto"``,
``span_service.ingest`` looks up the AI system by
``(tenant_id, system_id)`` and copies the resolved tier onto the span.
That makes the span row a complete audit artefact — no joins required
to know how the system was classified at the time of inference.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import created_at_column, updated_at_column, uuid_pk


class AISystem(Base):
    """A tenant's declaration of one AI system + its classified tier."""

    __tablename__ = "ai_systems"

    id: Mapped[uuid.UUID] = uuid_pk()

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The SDK-side identifier. Stable across deploys — must match the
    # ``system_id`` the SDK sends in span payloads.
    system_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # ---- User declarations ---------------------------------------------
    purpose: Mapped[str | None] = mapped_column(String(500), nullable=True)

    annex_iii_categories: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )
    prohibited_practices: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )
    transparency_triggers: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )
    is_gpai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ---- Provider information (Annex IV §1(b)-(d)) ---------------------
    # Free-form JSON because the shape varies wildly across providers.
    # See :class:`app.schemas.ai_system.ProviderInfo` for the recommended
    # keys (legal_name, address, country, contact_email,
    # authorised_representative, system_version, software_environment,
    # hardware_environment, validation_methods, notes). Extra keys are
    # accepted and round-tripped.
    provider_info: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    # ---- Resolved (classifier output) ----------------------------------
    risk_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    rules_version: Mapped[str] = mapped_column(String(20), nullable=False)
    reasoning: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )
    classified_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "system_id",
            name="uq_ai_systems_tenant_system",
        ),
    )
