"""Pydantic schemas for AI system declarations + classification output.

The wire format mirrors the ORM. ``ProviderInfo`` is the recommended
shape for ``ai_systems.provider_info`` (free-form JSONB at the storage
layer); extra keys are accepted and round-tripped — the recommended
fields are the ones the Annex IV templates render explicitly.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

RiskTier = Literal["unacceptable", "high", "limited", "minimal"]
RuleType = Literal["prohibited", "high_risk", "transparency"]


class ProviderInfo(BaseModel):
    """Annex IV §1(b)-(d) provider/deployer information.

    All fields optional — Annex IV demands them at audit time, not at
    declaration time. The renderer marks unfilled fields as
    "Provider input required" so the gap is visible.
    """

    model_config = ConfigDict(extra="allow")  # extra keys round-trip

    legal_name: str | None = Field(
        default=None, max_length=200, description="Provider's legal entity name."
    )
    address: str | None = Field(
        default=None, max_length=500, description="Registered address."
    )
    country: str | None = Field(
        default=None,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code (e.g. 'IT').",
    )
    contact_email: str | None = Field(
        default=None,
        max_length=200,
        description="Technical / compliance contact.",
    )
    authorised_representative: str | None = Field(
        default=None,
        max_length=500,
        description=(
            "Name + address of EU authorised representative — required "
            "if the provider is established outside the EU (Art. 22)."
        ),
    )
    system_version: str | None = Field(
        default=None,
        max_length=50,
        description=(
            "The AI system's own version (e.g. 'v2.4.1'). Distinct "
            "from AnnexKit's rules_version."
        ),
    )
    software_environment: str | None = Field(
        default=None,
        max_length=500,
        description=(
            "Free-form description of runtime stack "
            "(e.g. 'Python 3.13, FastAPI 0.136, Postgres 16')."
        ),
    )
    hardware_environment: str | None = Field(
        default=None,
        max_length=500,
        description=(
            "Free-form description of intended hardware "
            "(e.g. 'AWS c7i.large, 8 vCPU, 16 GB RAM')."
        ),
    )
    validation_methods: str | None = Field(
        default=None,
        max_length=2000,
        description=(
            "Annex IV §2(e) — methodology for validation + testing. "
            "Free-form prose."
        ),
    )
    notes: str | None = Field(
        default=None,
        max_length=2000,
        description="Free-form additional context.",
    )


class AISystemDeclaration(BaseModel):
    """Wire-format declaration sent to ``PUT /api/v1/systems``."""

    model_config = ConfigDict(extra="forbid")

    # Restricted charset so ``system_id`` is safe in Content-Disposition
    # headers, URL paths (Annex IV download filename), and structured
    # logs. Permits letters, digits, dot, underscore, hyphen.
    system_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9._-]+$",
    )
    purpose: str | None = Field(default=None, max_length=500)
    annex_iii_categories: list[str] = Field(default_factory=list)
    prohibited_practices: list[str] = Field(default_factory=list)
    transparency_triggers: list[str] = Field(default_factory=list)
    is_gpai: bool = False
    provider_info: ProviderInfo = Field(default_factory=ProviderInfo)


class ReasoningEntry(BaseModel):
    """One triggered rule contributing to a verdict — mirrors
    :class:`app.services.risk_engine.ReasonEntry`."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str
    rule_type: RuleType
    article: str
    name_it: str
    name_en: str


class AISystemRead(BaseModel):
    """Returned from PUT/GET on ``/api/v1/systems``."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    system_id: str
    purpose: str | None
    annex_iii_categories: list[str]
    prohibited_practices: list[str]
    transparency_triggers: list[str]
    is_gpai: bool
    provider_info: dict[str, Any]

    risk_tier: RiskTier
    rules_version: str
    reasoning: list[ReasoningEntry]
    classified_at: datetime

    created_at: datetime
    updated_at: datetime


class AISystemListResponse(BaseModel):
    """Page of AI systems for a tenant."""

    model_config = ConfigDict(extra="forbid")

    systems: list[AISystemRead]
    total: int
