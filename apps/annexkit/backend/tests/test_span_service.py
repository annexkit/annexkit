"""Unit tests for :func:`app.services.span_service.ingest`.

These tests bypass HTTP and exercise the service directly so we can
assert on the audit-log linkage and the wire-to-ORM field translation
(``metadata`` → ``extras``).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from konformia_core.schemas.evidence import IngestSource, IngestSpan
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.span import Span
from app.models.tenant import Tenant
from app.services import span_service


def _payload() -> IngestSpan:
    return IngestSpan(
        trace_id="a" * 32,
        span_id="b" * 16,
        system_id="bot",
        started_at=datetime(2026, 5, 7, 10, 0, tzinfo=UTC),
        ended_at=datetime(2026, 5, 7, 10, 0, 1, tzinfo=UTC),
        latency_ms=1000,
        sources=[IngestSource(uri="kb://x")],
        metadata={"k": "v"},
        sdk_version="0.1.0",
    )


@pytest.mark.asyncio
async def test_ingest_creates_span_and_audit_in_one_transaction(
    db_session: AsyncSession,
) -> None:
    tenant = Tenant(name="Velmara", slug="velmara")
    db_session.add(tenant)
    await db_session.flush()

    span = await span_service.ingest(db_session, tenant_id=tenant.id, payload=_payload())
    await db_session.commit()

    # Span row written.
    spans = (await db_session.execute(select(Span))).scalars().all()
    assert len(spans) == 1
    assert spans[0].id == span.id

    # ``metadata`` field on the wire was translated to ``extras`` on the ORM.
    assert spans[0].extras == {"k": "v"}

    # Audit log written with reference to the span.
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert len(audits) == 1
    assert audits[0].entity_type == "span"
    assert audits[0].entity_id == span.id
    assert audits[0].action == "span.ingested"
    assert audits[0].tenant_id == tenant.id
