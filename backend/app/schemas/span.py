"""Pydantic schemas for the span ingest endpoint.

Wire format mirrors ``annexkit.schema.Span`` — what the SDK serialises
is what the collector validates. We intentionally don't import the
SDK's Pydantic class because:

  1. The SDK runs in customer environments and we don't want to drag
     unrelated server-side deps into theirs.
  2. SDK and collector should version independently; a wire-format
     additive change should land on the collector first, then the SDK.

Fields prefixed with ``__`` in the SDK (none today) are intentionally
not duplicated here.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# Mirror of ``annexkit.schema.RiskTier``. Don't import — see module docstring.
RiskTier = Literal["auto", "unacceptable", "high", "limited", "minimal"]


class IngestSource(BaseModel):
    """Mirror of SDK ``Source``."""

    model_config = ConfigDict(extra="forbid")

    uri: str
    hash: str | None = None
    version: str | None = None


class IngestSpan(BaseModel):
    """Wire-format span — what the SDK POSTs to ``/api/v1/spans``."""

    model_config = ConfigDict(extra="forbid")

    # Identity — hex-shaped tokens (the SDK generates them via
    # ``uuid.uuid4().hex``). Pattern enforces shape so a bogus client
    # can't inject control chars or weird unicode into the audit trail.
    trace_id: str = Field(
        ..., min_length=1, max_length=64, pattern=r"^[A-Za-z0-9]+$"
    )
    span_id: str = Field(
        ..., min_length=1, max_length=32, pattern=r"^[A-Za-z0-9]+$"
    )
    parent_span_id: str | None = Field(
        default=None, max_length=32, pattern=r"^[A-Za-z0-9]+$"
    )

    # System
    # Restricted charset so ``system_id`` is safe in Content-Disposition
    # headers, URL paths (the Annex IV download filename), and structured
    # logs. Permits letters, digits, dot, underscore, hyphen.
    system_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9._-]+$",
    )
    deployment: str = Field(
        default="prod", max_length=50, pattern=r"^[A-Za-z0-9._-]+$"
    )

    # AI Act
    risk_tier: RiskTier = "auto"
    purpose: str | None = Field(default=None, max_length=500)

    # Timing — UTC
    started_at: datetime
    ended_at: datetime | None = None
    latency_ms: int | None = Field(default=None, ge=0)

    # Model
    model_provider: str | None = Field(default=None, max_length=50)
    model_name: str | None = Field(default=None, max_length=100)
    model_version: str | None = Field(default=None, max_length=100)

    # Privacy-preserving I/O — these are SHA-256 hex digests (64 chars)
    # but we don't enforce length here so future hash schemes don't
    # require a wire-format break.
    input_hash: str | None = Field(default=None, max_length=128)
    input_chars: int | None = Field(default=None, ge=0)
    output_hash: str | None = Field(default=None, max_length=128)
    output_chars: int | None = Field(default=None, ge=0)

    # Retrieval grounding
    sources: list[IngestSource] = Field(default_factory=list)

    # User context
    user_role: str | None = Field(default=None, max_length=50)

    # Result
    error: str | None = Field(default=None, max_length=500)

    # Free-form (SDK calls this ``metadata`` on the wire)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # SDK provenance
    sdk_version: str = Field(..., max_length=20)
    sdk_lang: str = Field(default="python", max_length=20)


class IngestResponse(BaseModel):
    """Returned from a successful ``POST /api/v1/spans``."""

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID = Field(..., description="Server-side primary key of the persisted span.")
    received_at: datetime = Field(..., description="UTC timestamp when the collector received the span.")
