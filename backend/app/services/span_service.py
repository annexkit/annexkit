"""Span ingest service.

Single public function: :func:`ingest`. Given a validated ingest
payload + tenant id, it:

  1. Checks for an existing span with the same
     ``(tenant_id, trace_id, span_id)`` — at-least-once delivery from
     the SDK means duplicate POSTs are normal under network turbulence.
     Idempotent: returns the existing row with no audit-log
     duplication.
  2. Otherwise INSERTs the span row.
  3. INSERTs one ``audit_logs`` row via :func:`audit_service.record` —
     so we have a tamper-evident trail of every span we accepted.

Both writes happen in the same SQLAlchemy session (= transaction). If
anything fails, both roll back together — we never leave half-written
audit trails.

The wire-format ``metadata`` field is renamed to ``extras`` on the ORM
to dodge the ``Base.metadata`` SQLAlchemy collision.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_system import AISystem
from app.models.span import Span
from app.schemas.span import IngestSpan
from app.services import audit_service

logger = logging.getLogger("annexkit.ingest")


async def ingest(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    payload: IngestSpan,
) -> Span:
    """Persist a validated span + write the matching audit log entry.

    Idempotent on ``(tenant_id, trace_id, span_id)`` — a duplicate
    POST returns the original row without writing a second audit log.
    The unique index on those three columns also serves as a hard
    backstop for concurrent inserts.
    """
    existing = (
        await session.execute(
            select(Span)
            .where(Span.tenant_id == tenant_id)
            .where(Span.trace_id == payload.trace_id)
            .where(Span.span_id == payload.span_id)
        )
    ).scalar_one_or_none()
    if existing is not None:
        logger.info(
            "duplicate span ignored: tenant_id=%s trace_id=%s system_id=%s",
            tenant_id,
            payload.trace_id,
            payload.system_id,
        )
        return existing

    # Resolve risk_tier when SDK sent "auto": look up the tenant's
    # AI system declaration. If none exists yet, persist the span as
    # "auto" — it'll be recoverable later by re-running classification
    # against any future ai_systems row (M2 backfill job).
    effective_risk_tier = payload.risk_tier
    if effective_risk_tier == "auto":
        ai_system = (
            await session.execute(
                select(AISystem)
                .where(AISystem.tenant_id == tenant_id)
                .where(AISystem.system_id == payload.system_id)
            )
        ).scalar_one_or_none()
        if ai_system is not None:
            effective_risk_tier = ai_system.risk_tier

    span = Span(
        tenant_id=tenant_id,
        trace_id=payload.trace_id,
        span_id=payload.span_id,
        parent_span_id=payload.parent_span_id,
        system_id=payload.system_id,
        deployment=payload.deployment,
        risk_tier=effective_risk_tier,
        purpose=payload.purpose,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
        latency_ms=payload.latency_ms,
        model_provider=payload.model_provider,
        model_name=payload.model_name,
        model_version=payload.model_version,
        input_hash=payload.input_hash,
        input_chars=payload.input_chars,
        output_hash=payload.output_hash,
        output_chars=payload.output_chars,
        sources=[s.model_dump() for s in payload.sources],
        user_role=payload.user_role,
        error=payload.error,
        extras=payload.metadata,  # wire ``metadata`` → ORM ``extras``
        sdk_version=payload.sdk_version,
        sdk_lang=payload.sdk_lang,
    )
    session.add(span)
    try:
        await session.flush()  # populates ``span.id`` for the audit log
    except IntegrityError:
        # TOCTOU race: another concurrent request inserted the same
        # ``(tenant_id, trace_id, span_id)`` between our SELECT above
        # and this INSERT. The unique constraint
        # ``uq_spans_tenant_trace_span`` is the backstop. Roll back the
        # transaction state, re-fetch the row that won, and treat this
        # POST as the duplicate it now is — same idempotent contract.
        await session.rollback()
        existing_after_race = (
            await session.execute(
                select(Span)
                .where(Span.tenant_id == tenant_id)
                .where(Span.trace_id == payload.trace_id)
                .where(Span.span_id == payload.span_id)
            )
        ).scalar_one()
        logger.info(
            "concurrent duplicate span resolved via unique constraint: "
            "tenant_id=%s trace_id=%s system_id=%s",
            tenant_id,
            payload.trace_id,
            payload.system_id,
        )
        return existing_after_race

    await audit_service.record(
        session,
        tenant_id=tenant_id,
        action="span.ingested",
        entity_type="span",
        entity_id=span.id,
        details={
            "system_id": span.system_id,
            "trace_id": span.trace_id,
            "deployment": span.deployment,
            "risk_tier": span.risk_tier,
            "sdk_version": span.sdk_version,
        },
    )

    logger.info(
        "ingested span: tenant_id=%s system_id=%s trace_id=%s "
        "deployment=%s risk_tier=%s latency_ms=%s",
        tenant_id,
        span.system_id,
        span.trace_id,
        span.deployment,
        span.risk_tier,
        span.latency_ms,
    )

    return span
