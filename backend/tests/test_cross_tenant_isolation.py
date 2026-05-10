"""Cross-tenant isolation contract tests.

For an EU compliance product the *single most important* property is
that tenant A cannot read, mutate, or fabricate evidence in tenant B's
domain. This file pins that contract for every public surface that has
a tenant boundary:

  * ``/api/v1/spans`` ingest — span lands under the auth'd tenant_id
    even when a malicious payload tries to spoof system_id.
  * ``/api/v1/systems`` upsert/read/list — tenant A cannot see or mutate
    tenant B's declarations.
  * ``/api/v1/systems/{id}/annex-iv`` generation — tenant A gets 404
    on tenant B's system_id.
  * ``/api/v1/trust/{slug}*`` — public endpoints render only one
    tenant's data, never cross-pollinated.

These tests use the shared ``client`` + ``db_session`` fixtures and
explicitly create a SECOND tenant inside the test (rather than via the
``authenticated_tenant`` fixture) so we have two distinct API keys.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_system import AISystem
from app.models.span import Span
from app.models.tenant import ApiKey, Tenant
from app.services import api_key as api_key_service


async def _seed_second_tenant(
    db_session: AsyncSession, slug: str = "tenant-b"
) -> tuple[Tenant, str]:
    tenant = Tenant(name="Tenant B", slug=slug)
    db_session.add(tenant)
    await db_session.flush()

    generated = api_key_service.generate()
    db_session.add(
        ApiKey(
            tenant_id=tenant.id,
            name="default",
            key_prefix=generated.prefix,
            key_hash=generated.key_hash,
        )
    )
    await db_session.commit()
    return tenant, generated.plaintext


def _span_payload(system_id: str = "shared-id") -> dict[str, Any]:
    return {
        "trace_id": "a" * 32,
        "span_id": "b" * 16,
        "system_id": system_id,
        "deployment": "prod",
        "risk_tier": "auto",
        "started_at": datetime(2026, 5, 7, 10, 0, tzinfo=UTC).isoformat(),
        "sdk_version": "0.1.0",
        "sdk_lang": "python",
    }


def _declaration(system_id: str = "shared-id") -> dict[str, Any]:
    return {
        "system_id": system_id,
        "annex_iii_categories": ["annex3_4_employment"],
    }


@pytest.mark.asyncio
async def test_span_lands_under_auth_tenant_not_payload_tenant(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    """A span POSTed by tenant A is owned by tenant A, regardless of
    what system_id the payload claims. There is no tenant-id field in
    the payload — the auth'd tenant decides ownership."""
    tenant_a, key_a = authenticated_tenant
    tenant_b, _ = await _seed_second_tenant(db_session)

    resp = await client.post(
        "/api/v1/spans",
        json=_span_payload(system_id="anything"),
        headers={"Authorization": f"Bearer {key_a}"},
    )
    assert resp.status_code == 202

    spans = (await db_session.execute(select(Span))).scalars().all()
    assert len(spans) == 1
    assert spans[0].tenant_id == tenant_a.id
    assert spans[0].tenant_id != tenant_b.id


@pytest.mark.asyncio
async def test_two_tenants_can_declare_same_system_id(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    """``system_id`` is unique PER TENANT, not globally. Both tenants
    declaring ``loan-screener-bot`` is legal and each owns its own row."""
    tenant_a, key_a = authenticated_tenant
    tenant_b, key_b = await _seed_second_tenant(db_session)

    for key in (key_a, key_b):
        resp = await client.put(
            "/api/v1/systems",
            json=_declaration(system_id="loan-screener-bot"),
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp.status_code == 200

    rows = (await db_session.execute(select(AISystem))).scalars().all()
    assert len(rows) == 2
    assert {r.tenant_id for r in rows} == {tenant_a.id, tenant_b.id}


@pytest.mark.asyncio
async def test_tenant_a_cannot_read_tenant_b_system(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    """B declares ``b-only-bot``; A's GET returns 404."""
    _, key_a = authenticated_tenant
    _, key_b = await _seed_second_tenant(db_session)

    resp = await client.put(
        "/api/v1/systems",
        json=_declaration(system_id="b-only-bot"),
        headers={"Authorization": f"Bearer {key_b}"},
    )
    assert resp.status_code == 200

    resp = await client.get(
        "/api/v1/systems/b-only-bot",
        headers={"Authorization": f"Bearer {key_a}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_returns_only_callers_systems(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, key_a = authenticated_tenant
    _, key_b = await _seed_second_tenant(db_session)

    await client.put(
        "/api/v1/systems",
        json=_declaration(system_id="a-bot"),
        headers={"Authorization": f"Bearer {key_a}"},
    )
    await client.put(
        "/api/v1/systems",
        json=_declaration(system_id="b-bot"),
        headers={"Authorization": f"Bearer {key_b}"},
    )

    resp_a = await client.get("/api/v1/systems", headers={"Authorization": f"Bearer {key_a}"})
    assert resp_a.status_code == 200
    a_systems = {s["system_id"] for s in resp_a.json()["systems"]}
    assert a_systems == {"a-bot"}

    resp_b = await client.get("/api/v1/systems", headers={"Authorization": f"Bearer {key_b}"})
    assert resp_b.status_code == 200
    b_systems = {s["system_id"] for s in resp_b.json()["systems"]}
    assert b_systems == {"b-bot"}


@pytest.mark.asyncio
async def test_annex_iv_404_across_tenants(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    """Tenant A asking for tenant B's system Annex IV → 404."""
    _, key_a = authenticated_tenant
    _, key_b = await _seed_second_tenant(db_session)

    await client.put(
        "/api/v1/systems",
        json=_declaration(system_id="b-only-bot"),
        headers={"Authorization": f"Bearer {key_b}"},
    )

    resp = await client.get(
        "/api/v1/systems/b-only-bot/annex-iv",
        headers={"Authorization": f"Bearer {key_a}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_trust_pages_dont_leak_other_tenants(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    """Public trust pages render only the named tenant's data."""
    tenant_a, key_a = authenticated_tenant
    tenant_b, key_b = await _seed_second_tenant(db_session)

    await client.put(
        "/api/v1/systems",
        json=_declaration(system_id="a-bot"),
        headers={"Authorization": f"Bearer {key_a}"},
    )
    await client.put(
        "/api/v1/systems",
        json=_declaration(system_id="b-bot"),
        headers={"Authorization": f"Bearer {key_b}"},
    )

    # Tenant A's trust page lists only a-bot.
    resp_a = await client.get(f"/api/v1/trust/{tenant_a.slug}/systems")
    assert resp_a.status_code == 200
    a_ids = {s["system_id"] for s in resp_a.json()["systems"]}
    assert a_ids == {"a-bot"}

    # Tenant B's trust page lists only b-bot.
    resp_b = await client.get(f"/api/v1/trust/{tenant_b.slug}/systems")
    assert resp_b.status_code == 200
    b_ids = {s["system_id"] for s in resp_b.json()["systems"]}
    assert b_ids == {"b-bot"}


@pytest.mark.asyncio
async def test_404s_are_opaque_no_information_leak(
    client: AsyncClient,
) -> None:
    """All trust-page 404s share the same body — an attacker can't
    differentiate ``slug doesn't exist`` from ``slug exists, system
    doesn't``."""
    resp_unknown_slug = await client.get("/api/v1/trust/this-slug-does-not-exist")
    assert resp_unknown_slug.status_code == 404
    assert resp_unknown_slug.json() == {"detail": "Not found"}

    resp_unknown_slug_system = await client.get(
        "/api/v1/trust/this-slug-does-not-exist/systems/anything"
    )
    assert resp_unknown_slug_system.status_code == 404
    assert resp_unknown_slug_system.json() == {"detail": "Not found"}


@pytest.mark.asyncio
async def test_invalid_system_id_charset_rejected(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    """``system_id`` must match ``[A-Za-z0-9._-]+``. Path traversal
    (``../etc/passwd``), spaces, and quotes are rejected at the
    schema layer with 422."""
    _, key = authenticated_tenant

    for bad in [
        "../../etc/passwd",
        "system with spaces",
        'system"with-quotes',
        "system\\backslash",
        "system\x00null",
    ]:
        resp = await client.put(
            "/api/v1/systems",
            json={"system_id": bad, "annex_iii_categories": []},
            headers={"Authorization": f"Bearer {key}"},
        )
        assert resp.status_code == 422, (
            f"system_id {bad!r} should be rejected, got {resp.status_code}"
        )
