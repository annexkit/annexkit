"""Span ingest now resolves ``risk_tier="auto"`` from the declared AI system.

When the SDK sends ``risk_tier="auto"``:
  * If a matching ``ai_systems`` row exists for the tenant, the span's
    persisted tier is the declaration's tier.
  * Otherwise the tier stays ``"auto"`` — the user is expected to
    declare the system later, and a future M2 backfill job will
    upgrade older spans.

The SDK can override by sending an explicit non-auto tier (rare —
mostly used by adapters that have already classified upstream).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.span import Span
from app.models.tenant import Tenant


def _span_payload(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "trace_id": "a" * 32,
        "span_id": "b" * 16,
        "system_id": "hr-screener",
        "deployment": "prod",
        "risk_tier": "auto",
        "started_at": datetime(2026, 5, 7, 10, 0, tzinfo=UTC).isoformat(),
        "sdk_version": "0.1.0",
        "sdk_lang": "python",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_auto_resolves_to_declared_tier(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}

    # Declare the system as high-risk.
    declare = await client.put(
        "/api/v1/systems",
        json={
            "system_id": "hr-screener",
            "annex_iii_categories": ["annex3_4_employment"],
        },
        headers=headers,
    )
    assert declare.status_code == 200

    # SDK sends auto.
    ingest = await client.post(
        "/api/v1/spans",
        json=_span_payload(),
        headers=headers,
    )
    assert ingest.status_code == 202

    span = (await db_session.execute(select(Span))).scalar_one()
    assert span.risk_tier == "high"


@pytest.mark.asyncio
async def test_auto_stays_auto_when_no_declaration(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}

    # No PUT first — the system is undeclared.
    ingest = await client.post(
        "/api/v1/spans",
        json=_span_payload(system_id="never-declared"),
        headers=headers,
    )
    assert ingest.status_code == 202

    span = (await db_session.execute(select(Span))).scalar_one()
    assert span.risk_tier == "auto"


@pytest.mark.asyncio
async def test_explicit_tier_is_not_overridden(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    """If the SDK sends a non-auto tier, we trust it and don't re-classify.

    This lets adapters (e.g. a downstream observability tool) ship spans
    they've already classified without us silently overriding.
    """
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}

    # Declare as high.
    await client.put(
        "/api/v1/systems",
        json={
            "system_id": "hr-screener",
            "annex_iii_categories": ["annex3_4_employment"],
        },
        headers=headers,
    )

    # SDK explicitly sends "limited" — should NOT be upgraded.
    ingest = await client.post(
        "/api/v1/spans",
        json=_span_payload(risk_tier="limited"),
        headers=headers,
    )
    assert ingest.status_code == 202

    span = (await db_session.execute(select(Span))).scalar_one()
    assert span.risk_tier == "limited"
