"""Span ORM model — one row per LLM invocation tracked by the SDK.

Mirrors ``annexkit.schema.Span`` field-for-field, with three additions:
  * ``tenant_id``       — server-side ownership.
  * ``received_at``     — server-side ingest timestamp (independent of
                          the SDK's ``started_at`` to detect clock skew).
  * ``extras``          — Python attribute name for the ``metadata`` field
                          on the wire / DB column. Renamed because
                          ``metadata`` collides with SQLAlchemy's
                          ``Base.metadata`` class attribute.

Idempotency contract: ``(tenant_id, trace_id, span_id)`` is unique. The
SDK retries duplicate spans on transient failures; the collector
returns the existing row rather than creating duplicates. The unique
index serves both as a fast lookup for the dedup check in
``span_service.ingest`` and as a hard backstop for concurrent
inserts.

Spans are insert-mostly: they're written once on ingest and never
mutated. We don't put them under the same APPEND-ONLY trigger as
``audit_logs`` because legitimate operational reasons exist to delete
old spans (retention, GDPR erasure). The audit log keeps the trail of
deletions when those happen.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import created_at_column, uuid_pk


class Span(Base):
    """One AI-Act-tracked LLM invocation."""

    __tablename__ = "spans"

    # Server-side primary key (different from the SDK's span_id, which
    # is the OTel-style identifier the user-side trace lives under).
    id: Mapped[uuid.UUID] = uuid_pk()

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ---- SDK-provided identity ------------------------------------------
    # Hex strings (32 chars for trace_id, 16 for span_id) — keep as
    # ``String`` rather than ``UUID`` because the SDK might generate them
    # via OTel libraries that produce non-UUID hex tokens.
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    span_id: Mapped[str] = mapped_column(String(32), nullable=False)
    parent_span_id: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # ---- System ---------------------------------------------------------
    system_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    deployment: Mapped[str] = mapped_column(
        String(50), nullable=False, default="prod"
    )

    # ---- AI Act metadata ------------------------------------------------
    risk_tier: Mapped[str] = mapped_column(
        String(20), nullable=False, default="auto"
    )
    purpose: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ---- Timing ---------------------------------------------------------
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ---- Model ----------------------------------------------------------
    model_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ---- Privacy-preserving I/O ----------------------------------------
    input_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_chars: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_chars: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ---- Sources (RAG provenance) --------------------------------------
    # List of {uri, hash, version} dicts. JSONB on Postgres for indexing
    # ("show me all spans citing kb://policy/x"); JSON on SQLite for tests.
    sources: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=list,
    )

    # ---- User context ---------------------------------------------------
    user_role: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ---- Result ---------------------------------------------------------
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ---- Free-form extras ----------------------------------------------
    # The wire-format field is ``metadata``; the ORM attribute is
    # ``extras`` because ``metadata`` collides with ``Base.metadata``.
    # The DB column name is also ``extras`` — translation happens in
    # ``span_service.ingest`` so the API contract stays
    # ``{"metadata": ...}`` (matching the SDK).
    extras: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=False,
        default=dict,
    )

    # ---- SDK provenance ------------------------------------------------
    sdk_version: Mapped[str] = mapped_column(String(20), nullable=False)
    sdk_lang: Mapped[str] = mapped_column(
        String(20), nullable=False, default="python"
    )

    # ---- Server-side ----------------------------------------------------
    received_at: Mapped[datetime] = created_at_column()

    __table_args__ = (
        # Idempotency: at-least-once delivery from the SDK means the same
        # logical span can be POSTed twice. The unique key lets us dedupe
        # cheaply at the service layer AND provides a hard backstop for
        # concurrent inserts (second one raises IntegrityError).
        UniqueConstraint(
            "tenant_id",
            "trace_id",
            "span_id",
            name="uq_spans_tenant_trace_span",
        ),
        # The most common query: "show me tenant X's spans for system Y
        # over the last hour" — composite index covers it without a
        # full scan.
        Index(
            "ix_spans_tenant_system_received",
            "tenant_id",
            "system_id",
            "received_at",
        ),
        # And: "show me all spans in this trace" for distributed-trace
        # reconstruction.
        Index("ix_spans_tenant_trace", "tenant_id", "trace_id"),
    )
