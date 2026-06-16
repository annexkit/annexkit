"""``/api/v1/systems`` integration tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_system import AISystem
from app.models.audit_log import AuditLog
from app.models.tenant import Tenant


@pytest.mark.asyncio
async def test_put_creates_classified_high_risk(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    payload = {
        "system_id": "hr-screener",
        "purpose": "screen incoming CVs and shortlist candidates",
        "annex_iii_categories": ["annex3_4_employment"],
    }
    resp = await client.put(
        "/api/v1/systems",
        json=payload,
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["system_id"] == "hr-screener"
    assert body["risk_tier"] == "high"
    assert body["rules_version"]
    assert any(r["rule_id"] == "annex3_4_employment" for r in body["reasoning"])

    rows = (await db_session.execute(select(AISystem))).scalars().all()
    assert len(rows) == 1
    assert rows[0].risk_tier == "high"


@pytest.mark.asyncio
async def test_put_unacceptable_dominates(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    payload = {
        "system_id": "x",
        "prohibited_practices": ["art5_social_scoring"],
        "annex_iii_categories": ["annex3_4_employment"],
    }
    resp = await client.put(
        "/api/v1/systems",
        json=payload,
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 200
    assert resp.json()["risk_tier"] == "unacceptable"


@pytest.mark.asyncio
async def test_put_unknown_category_returns_422(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    resp = await client.put(
        "/api/v1/systems",
        json={"system_id": "x", "annex_iii_categories": ["bogus_x"]},
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_put_is_idempotent_upsert(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}

    first = await client.put(
        "/api/v1/systems",
        json={
            "system_id": "x",
            "annex_iii_categories": ["annex3_4_employment"],
        },
        headers=headers,
    )
    assert first.status_code == 200
    first_id = first.json()["id"]

    # Update: change purpose, add transparency trigger.
    second = await client.put(
        "/api/v1/systems",
        json={
            "system_id": "x",
            "purpose": "expanded purpose",
            "annex_iii_categories": ["annex3_4_employment"],
            "transparency_triggers": ["art50_chat_interaction"],
        },
        headers=headers,
    )
    assert second.status_code == 200
    assert second.json()["id"] == first_id  # same row updated, not new
    assert second.json()["risk_tier"] == "high"  # unchanged tier
    assert second.json()["purpose"] == "expanded purpose"

    rows = (await db_session.execute(select(AISystem))).scalars().all()
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_get_404_when_system_undeclared(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    resp = await client.get(
        "/api/v1/systems/never-declared",
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_returns_only_owners_systems(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}

    # Create two
    for sid in ("x", "y"):
        resp = await client.put(
            "/api/v1/systems",
            json={"system_id": sid, "annex_iii_categories": ["annex3_4_employment"]},
            headers=headers,
        )
        assert resp.status_code == 200

    list_resp = await client.get("/api/v1/systems", headers=headers)
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["total"] == 2
    assert {s["system_id"] for s in body["systems"]} == {"x", "y"}


@pytest.mark.asyncio
async def test_put_writes_audit_log(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}

    create_resp = await client.put(
        "/api/v1/systems",
        json={
            "system_id": "x",
            "annex_iii_categories": ["annex3_4_employment"],
        },
        headers=headers,
    )
    assert create_resp.status_code == 200

    update_resp = await client.put(
        "/api/v1/systems",
        json={
            "system_id": "x",
            "purpose": "updated",
            "annex_iii_categories": ["annex3_4_employment"],
        },
        headers=headers,
    )
    assert update_resp.status_code == 200

    audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
    actions = [a.action for a in audits]
    assert "ai_system.created" in actions
    assert "ai_system.updated" in actions
