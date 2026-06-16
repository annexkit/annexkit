"""Contract tests for ``POST /api/v1/tools/annex-iv-generator``.

This endpoint is the highest-leverage marketing surface: anonymous
users land here, fill a form, and receive a real Annex IV PDF. The
contract that must NOT regress:

  * Returns a real PDF (Content-Type, magic bytes, X-Document-Id).
  * Classifies deterministically from the form.
  * Persists one ``leads`` row per successful generation.
  * Rejects invalid emails with 422.
  * Rejects unknown rule ids with 422.
  * Rate-limits per IP.

Note: the rate-limit case is exercised in a separate test below with
``reset_limiter`` so the order of tests in this file doesn't matter.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.rate_limit import limiter


@pytest.fixture(autouse=True)
def reset_limiter() -> None:
    """Per-test reset so the 10/hour cap doesn't leak across tests."""
    limiter.reset()


def _valid_payload(**overrides: object) -> dict[str, object]:
    """Minimum-viable valid payload. Override any key per test."""
    payload: dict[str, object] = {
        "purpose": (
            "Internal helpdesk chatbot for engineers, summarises "
            "Confluence runbooks on demand."
        ),
        "annex_iii_categories": [],
        "prohibited_practices": [],
        "transparency_triggers": ["art50_chat_interaction"],
        "is_gpai": False,
        "provider_info": {
            "legal_name": "Test Corp S.r.l.",
            "country": "IT",
            "contact_email": "compliance@test.example",
        },
        "email": "founder@test.example",
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_generator_returns_pdf_for_limited_tier(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Happy path — Art. 50 chatbot → tier 'limited' → real PDF."""
    resp = await client.post(
        "/api/v1/tools/annex-iv-generator",
        json=_valid_payload(),
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.headers["x-risk-tier"] == "limited"
    assert "x-document-id" in resp.headers
    # PDF magic bytes — `%PDF-`.
    assert resp.content[:5] == b"%PDF-"
    # WeasyPrint produces something non-trivial.
    assert len(resp.content) > 10_000


@pytest.mark.asyncio
async def test_generator_classifies_high_risk_correctly(
    client: AsyncClient,
) -> None:
    """Annex III §4 employment → tier 'high'."""
    resp = await client.post(
        "/api/v1/tools/annex-iv-generator",
        json=_valid_payload(annex_iii_categories=["annex3_4_employment"]),
    )
    assert resp.status_code == 200
    assert resp.headers["x-risk-tier"] == "high"


@pytest.mark.asyncio
async def test_generator_classifies_prohibited_as_unacceptable(
    client: AsyncClient,
) -> None:
    """Article 5 prohibited practice → tier 'unacceptable'."""
    resp = await client.post(
        "/api/v1/tools/annex-iv-generator",
        json=_valid_payload(prohibited_practices=["art5_social_scoring"]),
    )
    assert resp.status_code == 200
    assert resp.headers["x-risk-tier"] == "unacceptable"


@pytest.mark.asyncio
async def test_generator_persists_one_lead_per_call(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Each successful generation writes a row to leads."""
    payload = _valid_payload(email="lead-capture@test.example")
    resp = await client.post("/api/v1/tools/annex-iv-generator", json=payload)
    assert resp.status_code == 200

    leads = (
        (await db_session.execute(select(Lead).where(Lead.email == "lead-capture@test.example")))
        .scalars()
        .all()
    )
    assert len(leads) == 1
    lead = leads[0]
    assert lead.source == "annex-iv-generator"
    assert lead.system_tier == "limited"
    assert "art50_chat_interaction" in lead.declared_categories
    # Purpose stored (truncated to 1000 chars, well within for this test).
    assert lead.system_purpose is not None
    assert "helpdesk chatbot" in lead.system_purpose


@pytest.mark.asyncio
async def test_generator_rejects_invalid_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/tools/annex-iv-generator",
        json=_valid_payload(email="not-an-email"),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_generator_rejects_unknown_annex_iii_id(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/tools/annex-iv-generator",
        json=_valid_payload(annex_iii_categories=["this_does_not_exist"]),
    )
    assert resp.status_code == 422
    body = resp.json()
    assert "Unknown Annex III category" in body["detail"]


@pytest.mark.asyncio
async def test_generator_email_is_lowercased_for_dedup(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Email validator lowercases — two casings produce two leads with
    the same lowercase email (so dedup queries work)."""
    for casing in ("Mixed.CASE@Example.COM", "mixed.case@example.com"):
        await client.post(
            "/api/v1/tools/annex-iv-generator",
            json=_valid_payload(email=casing),
        )

    leads = (
        (await db_session.execute(select(Lead).where(Lead.email == "mixed.case@example.com")))
        .scalars()
        .all()
    )
    assert len(leads) == 2  # both casings normalised to the same key


@pytest.mark.asyncio
async def test_generator_rate_limit_kicks_in_at_11th(client: AsyncClient) -> None:
    """11th call within an hour returns 429.

    Limit is 10/hour. Use distinct emails so we don't trip any
    accidental dedup logic in the future.
    """
    for i in range(10):
        resp = await client.post(
            "/api/v1/tools/annex-iv-generator",
            json=_valid_payload(email=f"user-{i}@test.example"),
        )
        assert resp.status_code != 429, (
            f"call #{i + 1} unexpectedly rate-limited at {resp.status_code}"
        )

    blocked = await client.post(
        "/api/v1/tools/annex-iv-generator",
        json=_valid_payload(email="user-eleventh@test.example"),
    )
    assert blocked.status_code == 429
