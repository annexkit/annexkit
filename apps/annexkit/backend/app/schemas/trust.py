"""Public-facing schemas for the trust center.

These are the shapes a fully-public page at
``https://<slug>.annexkit.eu/trust`` consumes — no auth, accessible
to prospects, auditors, customers comparing vendors.

The wire format is intentionally a SUBSET of the authenticated
``AISystemRead`` schema. Redaction happens at the service layer:

  * ``provider_info``: whitelist of public-safe keys (legal_name,
    address, country, authorised_representative, system_version,
    software_environment, hardware_environment). Sensitive fields
    (``contact_email``, ``validation_methods``, ``notes``) are
    stripped — those belong to the gated Annex IV PDF.
  * Operational telemetry (latency, error counts, span aggregations)
    is **not** exposed publicly. Customers can choose to share their
    Annex IV PDF (which contains those) directly with prospects;
    we don't make it part of the trust page surface.

The trust page is opt-in by virtue of being slug-addressable: any
tenant gets a slug at creation, and someone has to know the slug to
load the page. We do NOT enumerate tenants. Search engines indexing
slugs is an acceptable consequence — that is the point.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PublicRiskTier = Literal["unacceptable", "high", "limited", "minimal", "auto"]


class PublicTenant(BaseModel):
    """Identity block included on every trust response."""

    model_config = ConfigDict(extra="forbid")

    name: str
    slug: str


class PublicProviderInfo(BaseModel):
    """Whitelist of provider_info fields safe to publish.

    Sensitive fields (``contact_email``, ``validation_methods``,
    ``notes``) are intentionally absent here — see module docstring.
    """

    model_config = ConfigDict(extra="forbid")

    legal_name: str | None = None
    address: str | None = None
    country: str | None = None
    authorised_representative: str | None = None
    system_version: str | None = None
    software_environment: str | None = None
    hardware_environment: str | None = None


class PublicReasoningEntry(BaseModel):
    """Same shape as the authenticated reasoning entry — fully public."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str
    rule_type: str
    article: str
    name_it: str
    name_en: str


class PublicSystemSummary(BaseModel):
    """List-view of one AI system on a tenant's trust page."""

    model_config = ConfigDict(extra="forbid")

    system_id: str
    purpose: str | None
    risk_tier: PublicRiskTier
    annex_iii_categories: list[str]
    transparency_triggers: list[str]
    is_gpai: bool
    rules_version: str
    classified_at: datetime


class PublicSystemDetail(BaseModel):
    """Detail-view of one AI system on a tenant's trust page."""

    model_config = ConfigDict(extra="forbid")

    system_id: str
    purpose: str | None
    risk_tier: PublicRiskTier
    annex_iii_categories: list[str]
    prohibited_practices: list[str]
    transparency_triggers: list[str]
    is_gpai: bool
    rules_version: str
    reasoning: list[PublicReasoningEntry]
    classified_at: datetime
    created_at: datetime
    updated_at: datetime
    provider_info: PublicProviderInfo


class TierBreakdown(BaseModel):
    """Counts of AI systems by risk tier."""

    model_config = ConfigDict(extra="forbid")

    unacceptable: int = 0
    high: int = 0
    limited: int = 0
    minimal: int = 0
    # ``auto`` is shown so users can see how many systems are still
    # awaiting classification (e.g. spans arrived for an undeclared
    # system).
    auto: int = 0


class TrustOverview(BaseModel):
    """``GET /api/v1/trust/{slug}`` response."""

    model_config = ConfigDict(extra="forbid")

    tenant: PublicTenant
    total_systems: int
    by_tier: TierBreakdown
    annexkit_version: str
    as_of: datetime = Field(
        ...,
        description="Server-side timestamp the overview was computed.",
    )


class TrustSystemsResponse(BaseModel):
    """``GET /api/v1/trust/{slug}/systems`` response."""

    model_config = ConfigDict(extra="forbid")

    tenant: PublicTenant
    systems: list[PublicSystemSummary]
    annexkit_version: str
    as_of: datetime


class TrustSystemDetailResponse(BaseModel):
    """``GET /api/v1/trust/{slug}/systems/{system_id}`` response."""

    model_config = ConfigDict(extra="forbid")

    tenant: PublicTenant
    system: PublicSystemDetail
    annexkit_version: str
    as_of: datetime
