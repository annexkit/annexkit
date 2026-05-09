"""Span ingest idempotency tests.

The SDK retries on transient failures, so the same logical span can be
POSTed twice. The service must:

  1. Return the same id (the original row) on the duplicate POST.
  2. Not write a second ``audit_logs`` entry.

Backstop: the unique constraint on
``spans(tenant_id, trace_id, span_id)`` prevents concurrent inserts
from creating duplicates even if they both pass the SELECT-then-INSERT
race window.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.span import Span
from app.models.tenant import Tenant


def _payload() -> dict:
    return {
        "trace_id": "deadbeef" * 4,  # 32 chars
        "span_id": "cafebabe12345678",  # 16 chars
        "system_id": "loan-screener",
        "deployment": "prod",
        "risk_tier": "auto",
        "started_at": datetime(2026, 5, 7, 10, 0, tzinfo=UTC).isoformat(),
        "ended_at": datetime(2026, 5, 7, 10, 0, 1, tzinfo=UTC).isoformat(),
        "latency_ms": 1000,
        "input_hash": "f" * 64,
        "input_chars": 100,
        "output_hash": "e" * 64,
        "output_chars": 50,
        "sources": [],
        "metadata": {"channel": "test"},
        "sdk_version": "0.1.0",
        "sdk_lang": "python",
    }


@pytest.mark.asyncio
async def test_duplicate_post_is_idempotent(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}

    first = await client.post("/api/v1/spans", json=_payload(), headers=headers)
    assert first.status_code == 202, first.text
    first_id = first.json()["id"]

    # Second POST with identical (trace_id, span_id) — should return
    # the same id.
    second = await client.post("/api/v1/spans", json=_payload(), headers=headers)
    assert second.status_code == 202
    assert second.json()["id"] == first_id

    # Only one span row in DB.
    spans = (await db_session.execute(select(Span))).scalars().all()
    assert len(spans) == 1

    # Only ONE audit log entry — the dup ingest must not pollute the trail.
    audits = (
        await db_session.execute(
            select(AuditLog).where(AuditLog.action == "span.ingested")
        )
    ).scalars().all()
    assert len(audits) == 1
