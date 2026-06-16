"""Public trust-center API tests.

These endpoints are intentionally **public** — the integration tests
explicitly assert that no Authorization header is required.

Redaction is the headline contract: a system declared with sensitive
provider_info fields (contact_email, validation_methods, notes) must
NOT have those fields surfaced on the public trust page. This is
verified field-by-field in :func:`test_provider_info_redaction`.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_system import AISystem
from app.models.tenant import Tenant


async def _seed_system(
    db_session: AsyncSession,
    *,
    tenant: Tenant,
    system_id: str,
    risk_tier: str = "high",
    annex_iii_categories: list[str] | None = None,
    provider_info: dict | None = None,
    purpose: str | None = "test purpose",
) -> AISystem:
    from datetime import UTC, datetime

    row = AISystem(
        tenant_id=tenant.id,
        system_id=system_id,
        purpose=purpose,
        annex_iii_categories=annex_iii_categories or [],
        prohibited_practices=[],
        transparency_triggers=[],
        is_gpai=False,
        provider_info=provider_info or {},
        risk_tier=risk_tier,
        rules_version="1.0.0",
        reasoning=[],
        classified_at=datetime.now(UTC),
    )
    db_session.add(row)
    await db_session.flush()
    return row


@pytest.mark.asyncio
async def test_overview_404_when_slug_unknown(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/trust/never-existed")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_overview_no_auth_required(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    tenant, _ = authenticated_tenant
    # Explicitly send NO Authorization header — public endpoint.
    resp = await client.get(f"/api/v1/trust/{tenant.slug}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["tenant"]["slug"] == tenant.slug
    assert body["tenant"]["name"] == tenant.name


@pytest.mark.asyncio
async def test_overview_tier_breakdown(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    tenant, _ = authenticated_tenant
    await _seed_system(db_session, tenant=tenant, system_id="a", risk_tier="high")
    await _seed_system(db_session, tenant=tenant, system_id="b", risk_tier="high")
    await _seed_system(db_session, tenant=tenant, system_id="c", risk_tier="limited")
    await _seed_system(db_session, tenant=tenant, system_id="d", risk_tier="minimal")
    await db_session.commit()

    resp = await client.get(f"/api/v1/trust/{tenant.slug}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_systems"] == 4
    assert body["by_tier"]["high"] == 2
    assert body["by_tier"]["limited"] == 1
    assert body["by_tier"]["minimal"] == 1
    assert body["by_tier"]["unacceptable"] == 0


@pytest.mark.asyncio
async def test_list_systems_returns_summaries(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    tenant, _ = authenticated_tenant
    await _seed_system(
        db_session,
        tenant=tenant,
        system_id="hr-screener",
        risk_tier="high",
        annex_iii_categories=["annex3_4_employment"],
        purpose="shortlist CVs",
    )
    await db_session.commit()

    resp = await client.get(f"/api/v1/trust/{tenant.slug}/systems")
    assert resp.status_code == 200
    body = resp.json()
    assert body["tenant"]["slug"] == tenant.slug
    assert len(body["systems"]) == 1
    s = body["systems"][0]
    assert s["system_id"] == "hr-screener"
    assert s["risk_tier"] == "high"
    assert s["purpose"] == "shortlist CVs"
    assert s["annex_iii_categories"] == ["annex3_4_employment"]
    # Operational telemetry is NOT exposed publicly.
    assert "spans" not in s
    assert "latency_ms" not in s


@pytest.mark.asyncio
async def test_get_system_404_when_undeclared(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    tenant, _ = authenticated_tenant
    resp = await client.get(f"/api/v1/trust/{tenant.slug}/systems/never")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_provider_info_redaction(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    """Public trust page MUST redact sensitive provider_info fields.

    Public-safe (whitelisted): legal_name, address, country,
        authorised_representative, system_version, software_environment,
        hardware_environment.
    Redacted: contact_email, validation_methods, notes.
    """
    tenant, _ = authenticated_tenant
    await _seed_system(
        db_session,
        tenant=tenant,
        system_id="hr-screener",
        risk_tier="high",
        provider_info={
            # public-safe
            "legal_name": "Velmara S.r.l.",
            "address": "Via Manzoni 1, Milano, IT",
            "country": "IT",
            "system_version": "v2.4.1",
            "software_environment": "Python 3.13",
            "hardware_environment": "AWS c7i.large",
            "authorised_representative": "John Doe Legal",
            # MUST be redacted
            "contact_email": "private@velmara.example",
            "validation_methods": "PRIVATE: holdout test of 5K samples...",
            "notes": "PRIVATE: ranking head fine-tuned monthly...",
        },
    )
    await db_session.commit()

    resp = await client.get(f"/api/v1/trust/{tenant.slug}/systems/hr-screener")
    assert resp.status_code == 200
    pi = resp.json()["system"]["provider_info"]

    # Public fields surface
    assert pi["legal_name"] == "Velmara S.r.l."
    assert pi["address"] == "Via Manzoni 1, Milano, IT"
    assert pi["country"] == "IT"
    assert pi["system_version"] == "v2.4.1"
    assert pi["software_environment"] == "Python 3.13"
    assert pi["hardware_environment"] == "AWS c7i.large"
    assert pi["authorised_representative"] == "John Doe Legal"

    # Sensitive fields MUST NOT appear in the response
    assert "contact_email" not in pi
    assert "validation_methods" not in pi
    assert "notes" not in pi
    # And the body must not contain the sensitive values anywhere
    raw = resp.text
    assert "private@velmara.example" not in raw
    assert "holdout test" not in raw
    assert "fine-tuned" not in raw


@pytest.mark.asyncio
async def test_get_system_includes_reasoning(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    tenant, _ = authenticated_tenant
    from datetime import UTC, datetime

    db_session.add(
        AISystem(
            tenant_id=tenant.id,
            system_id="x",
            purpose=None,
            annex_iii_categories=["annex3_4_employment"],
            prohibited_practices=[],
            transparency_triggers=[],
            is_gpai=False,
            provider_info={},
            risk_tier="high",
            rules_version="1.0.0",
            reasoning=[
                {
                    "rule_id": "annex3_4_employment",
                    "rule_type": "high_risk",
                    "article": "Annex III, §4",
                    "name_it": "Occupazione",
                    "name_en": "Employment",
                }
            ],
            classified_at=datetime.now(UTC),
        )
    )
    await db_session.commit()

    resp = await client.get(f"/api/v1/trust/{tenant.slug}/systems/x")
    assert resp.status_code == 200
    body = resp.json()
    reasoning = body["system"]["reasoning"]
    assert len(reasoning) == 1
    assert reasoning[0]["rule_id"] == "annex3_4_employment"
    assert reasoning[0]["name_it"] == "Occupazione"
    assert reasoning[0]["name_en"] == "Employment"
