"""Internal data context for Annex IV rendering.

Not part of the wire format — these are the structured types
``annex_iv_aggregator.gather`` produces and ``annex_iv_renderer``
consumes. Pydantic + ``StrictUndefined`` (in the Jinja env) means a
typo on ``{{ ctx.systme.purpose }}`` blows up cleanly instead of
rendering an empty string.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

GapStatus = Literal["auto", "partial", "manual"]


class TenantSnapshot(BaseModel):
    """Minimal tenant identity baked into every Annex IV."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    name: str
    slug: str


class ReasoningSnapshot(BaseModel):
    """One triggered rule from the classifier."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str
    rule_type: str
    article: str
    name_it: str
    name_en: str


class ProviderInfoSnapshot(BaseModel):
    """Frozen view of ``ai_systems.provider_info`` at render time.

    All fields nullable: the Annex IV template surfaces missing fields
    as "Provider input required" callouts (and they show up in the gap
    analysis section).
    """

    model_config = ConfigDict(extra="allow")

    legal_name: str | None = None
    address: str | None = None
    country: str | None = None
    contact_email: str | None = None
    authorised_representative: str | None = None
    system_version: str | None = None
    software_environment: str | None = None
    hardware_environment: str | None = None
    validation_methods: str | None = None
    notes: str | None = None


class AISystemSnapshot(BaseModel):
    """Frozen snapshot of an AI system declaration at render time."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    system_id: str
    purpose: str | None
    annex_iii_categories: list[str]
    prohibited_practices: list[str]
    transparency_triggers: list[str]
    is_gpai: bool
    provider_info: ProviderInfoSnapshot

    risk_tier: str
    rules_version: str
    reasoning: list[ReasoningSnapshot]
    classified_at: datetime
    created_at: datetime
    updated_at: datetime


class ModelUsage(BaseModel):
    """Aggregated stats for one (provider, name, version) tuple."""

    model_config = ConfigDict(extra="forbid")

    provider: str | None
    name: str | None
    version: str | None
    invocations: int
    first_seen: datetime | None
    last_seen: datetime | None


class SourceUsage(BaseModel):
    """Aggregated stats for one retrieval-source URI."""

    model_config = ConfigDict(extra="forbid")

    uri: str
    citations: int
    versions: list[str]


class ChangeEvent(BaseModel):
    """One row in the §5 changes table — derived from audit_logs."""

    model_config = ConfigDict(extra="forbid")

    occurred_at: datetime
    action: str
    details: dict[str, object]


class LatencyStats(BaseModel):
    """Latency percentiles in milliseconds."""

    model_config = ConfigDict(extra="forbid")

    sample_size: int = 0
    p50_ms: int | None = None
    p95_ms: int | None = None
    p99_ms: int | None = None
    mean_ms: int | None = None
    max_ms: int | None = None


class WindowStats(BaseModel):
    """Aggregations restricted to a time window (24h, 7d, 30d, all_time)."""

    model_config = ConfigDict(extra="forbid")

    window: Literal["24h", "7d", "30d", "all_time"]
    total: int
    error_count: int
    error_rate_pct: float | None = None
    latency: LatencyStats


class ErrorBreakdownEntry(BaseModel):
    """Count of spans per error class."""

    model_config = ConfigDict(extra="forbid")

    error_class: str
    count: int


class SpanAggregations(BaseModel):
    """All server-side computed stats over the system's span inventory."""

    model_config = ConfigDict(extra="forbid")

    total: int
    error_count: int
    first_span_at: datetime | None
    last_span_at: datetime | None
    is_active: bool = Field(
        default=False,
        description="True if last_span_at is within 7 days of generated_at.",
    )

    models: list[ModelUsage] = Field(default_factory=list)
    sources: list[SourceUsage] = Field(default_factory=list)
    sdk_versions: list[str] = Field(default_factory=list)
    deployments: list[str] = Field(default_factory=list)
    user_roles: list[str] = Field(default_factory=list)

    error_breakdown: list[ErrorBreakdownEntry] = Field(default_factory=list)
    windows: list[WindowStats] = Field(default_factory=list)


class GapItem(BaseModel):
    """One Annex IV requirement and how complete its evidence is."""

    model_config = ConfigDict(extra="forbid")

    section: str = Field(
        ...,
        description="Annex IV section reference (e.g. '§1.1', '§2.4').",
    )
    requirement_en: str
    requirement_it: str
    status: GapStatus = Field(
        ...,
        description=(
            "auto = fully populated from runtime evidence; "
            "partial = some data, more needed; "
            "manual = provider input required."
        ),
    )
    note: str | None = None


class SampleSpanRef(BaseModel):
    """One span included in the appendix as evidence anchor."""

    model_config = ConfigDict(extra="forbid")

    trace_id: str
    span_id: str
    started_at: datetime
    risk_tier: str
    model: str | None = None
    error: str | None = None


class AnnexIVContext(BaseModel):
    """Full data context for the Annex IV templates."""

    model_config = ConfigDict(extra="forbid")

    document_id: uuid.UUID
    generated_at: datetime
    annexkit_version: str

    tenant: TenantSnapshot
    system: AISystemSnapshot
    aggregations: SpanAggregations
    changes: list[ChangeEvent]
    gap_analysis: list[GapItem]
    sample_spans: list[SampleSpanRef]

    executive_summary: str = Field(
        default="",
        description=(
            "Auto-generated 2-3 sentence summary that opens the document."
        ),
    )
