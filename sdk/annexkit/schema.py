"""Pydantic span schema — the wire format between SDK and collector.

Aligned with OpenTelemetry GenAI Semantic Conventions where applicable
(https://opentelemetry.io/docs/specs/semconv/gen-ai/), extended with
EU AI Act-specific fields (``risk_tier``, ``purpose``, retrieval
``sources``, ``user_role``).

The collector treats every field as untrusted input — schema-validate
on ingest, never deserialise blindly. The corresponding Pydantic model
on the backend is intentionally a copy, not an import, so SDK and
collector can version independently.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# AI Act risk tiers, plus "auto" letting the collector classify from
# Annex III categories. "Unacceptable" is included because the collector
# echoes it back when the user-declared system maps to a prohibited
# practice — the SDK never sets it on its own.
RiskTier = Literal["auto", "unacceptable", "high", "limited", "minimal"]


class Source(BaseModel):
    """One retrieval source attached to a span (RAG document, KB entry).

    ``hash`` + ``version`` make the source verifiable: an auditor can
    reproduce the exact retrieval state at the time of inference.
    """

    model_config = ConfigDict(extra="forbid")

    uri: str = Field(
        ...,
        description="Source URI, e.g. 'kb://policies/credit-001' or 'https://...'.",
    )
    hash: str | None = Field(default=None, description="SHA-256 (or other) of the source content.")
    version: str | None = Field(
        default=None, description="Version tag, commit hash, or document revision."
    )


class Span(BaseModel):
    """One AI-Act-tracked LLM invocation.

    Every field except ``system_id`` and ``started_at`` is optional so
    minimal spans are valid. Auto-generated ``trace_id``/``span_id``
    free the user from worrying about tracing infrastructure unless they
    explicitly want to wire OpenTelemetry.
    """

    model_config = ConfigDict(extra="forbid")

    # ---- Identity --------------------------------------------------------
    trace_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    span_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_span_id: str | None = None

    # ---- System ----------------------------------------------------------
    system_id: str = Field(
        ...,
        description="Stable id of the AI system (e.g. 'loan-screener').",
    )
    deployment: str = Field(
        default="prod",
        description="Environment label ('prod', 'staging', etc.).",
    )

    # ---- AI Act metadata -------------------------------------------------
    risk_tier: RiskTier = Field(
        default="auto",
        description="AI Act risk tier. 'auto' = let the collector classify.",
    )
    purpose: str | None = Field(
        default=None,
        description="Human-readable purpose (Annex IV §1 input).",
    )

    # ---- Timing (always UTC) ---------------------------------------------
    started_at: datetime
    ended_at: datetime | None = None
    latency_ms: int | None = None

    # ---- Model -----------------------------------------------------------
    model_provider: str | None = Field(
        default=None,
        description="LLM provider: 'openai', 'anthropic', 'mistral', ...",
    )
    model_name: str | None = None
    model_version: str | None = None

    # ---- Privacy-preserving I/O -----------------------------------------
    input_hash: str | None = Field(default=None, description="SHA-256 hex of serialised input.")
    input_chars: int | None = None
    output_hash: str | None = Field(default=None, description="SHA-256 hex of serialised output.")
    output_chars: int | None = None

    # ---- Retrieval grounding --------------------------------------------
    sources: list[Source] = Field(default_factory=list)

    # ---- User context ----------------------------------------------------
    user_role: str | None = Field(
        default=None,
        description="Role of the user invoking the system (Article 13/14).",
    )

    # ---- Result ----------------------------------------------------------
    error: str | None = Field(
        default=None,
        description="'<module>.<class>: <message>' on exception.",
    )

    # ---- Free-form -------------------------------------------------------
    metadata: dict[str, Any] = Field(default_factory=dict)

    # ---- SDK provenance --------------------------------------------------
    sdk_version: str
    sdk_lang: str = "python"
