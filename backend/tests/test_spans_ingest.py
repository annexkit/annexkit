"""Integration tests for ``POST /api/v1/spans``.

These tests run against an in-memory SQLite DB (no Docker required) and
exercise the full request path: auth → schema validation → service →
audit log. Postgres-only features (the APPEND-ONLY trigger, JSONB ops)
are deliberately not tested here — the migration installs them; the
service-level guarantee in :mod:`app.services.audit_service` is what
the test layer pins.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.span import Span
from app.models.tenant import ApiKey, Tenant


def _valid_payload(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "trace_id": "a" * 32,
        "span_id": "b" * 16,
        "system_id": "loan-screener",
        "deployment": "prod",
        "risk_tier": "auto",
        "purpose": "pre-screen credit applications",
        "started_at": datetime(2026, 5, 7, 10, 0, tzinfo=UTC).isoformat(),
        "ended_at": datetime(2026, 5, 7, 10, 0, 1, tzinfo=UTC).isoformat(),
        "latency_ms": 1000,
        "model_provider": "openai",
        "model_name": "gpt-4o",
        "input_hash": "f" * 64,
        "input_chars": 120,
        "output_hash": "e" * 64,
        "output_chars": 80,
        "sources": [
            {"uri": "kb://policies/credit-001", "hash": "abc", "version": "v3"},
        ],
        "user_role": "loan_officer",
        "metadata": {"region": "EU"},
        "sdk_version": "0.1.0",
        "sdk_lang": "python",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_ingest_without_auth_returns_401(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/spans", json=_valid_payload())
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ingest_with_malformed_auth_returns_401(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/spans",
        json=_valid_payload(),
        headers={"Authorization": "Token ak_abc"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ingest_with_unknown_key_returns_401(client: AsyncClient) -> None:
    fake_key = "ak_" + "abc234567abcdefghijkmnpq"  # well-formed but not stored
    resp = await client.post(
        "/api/v1/spans",
        json=_valid_payload(),
        headers={"Authorization": f"Bearer {fake_key}"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ingest_with_revoked_key_returns_401(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    tenant, plaintext = authenticated_tenant
    # Revoke the only key for this tenant.
    api_key = (
        await db_session.execute(select(ApiKey).where(ApiKey.tenant_id == tenant.id))
    ).scalar_one()
    api_key.revoked_at = datetime.now(UTC)
    await db_session.commit()

    resp = await client.post(
        "/api/v1/spans",
        json=_valid_payload(),
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ingest_persists_span_and_audit_log(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    tenant, plaintext = authenticated_tenant

    payload = _valid_payload()
    resp = await client.post(
        "/api/v1/spans",
        json=payload,
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 202, resp.text
    body = resp.json()
    assert "id" in body
    assert "received_at" in body

    # Verify span persisted with the correct tenant + content.
    spans = (await db_session.execute(select(Span))).scalars().all()
    assert len(spans) == 1
    span = spans[0]
    assert span.tenant_id == tenant.id
    assert span.system_id == payload["system_id"]
    assert span.trace_id == payload["trace_id"]
    assert span.input_hash == payload["input_hash"]
    assert span.sources == payload["sources"]
    assert span.extras == payload["metadata"]
    assert span.sdk_version == "0.1.0"

    # Verify audit log entry with action ``span.ingested``.
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert len(audits) == 1
    audit = audits[0]
    assert audit.action == "span.ingested"
    assert audit.tenant_id == tenant.id
    assert audit.entity_type == "span"
    assert audit.entity_id == span.id
    assert audit.details["trace_id"] == payload["trace_id"]


@pytest.mark.asyncio
async def test_ingest_rejects_unknown_field(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    payload = _valid_payload()
    payload["wat"] = "no"  # extra field — schema is strict

    resp = await client.post(
        "/api/v1/spans",
        json=payload,
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_ingest_rejects_invalid_risk_tier(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    payload = _valid_payload(risk_tier="cosmic")

    resp = await client.post(
        "/api/v1/spans",
        json=payload,
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_ingest_updates_last_used_at(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant

    api_key_before = (
        await db_session.execute(select(ApiKey))
    ).scalar_one()
    assert api_key_before.last_used_at is None

    resp = await client.post(
        "/api/v1/spans",
        json=_valid_payload(),
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 202

    await db_session.refresh(api_key_before)
    assert api_key_before.last_used_at is not None
