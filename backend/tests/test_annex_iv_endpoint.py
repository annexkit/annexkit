"""``GET /api/v1/systems/{system_id}/annex-iv`` integration tests.

PDF rendering uses WeasyPrint which has native (Cairo/Pango) deps
not always available on test hosts; PDF tests are guarded with
``pytest.importorskip``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.tenant import Tenant


async def _declare_high_risk(client: AsyncClient, headers: dict[str, str]) -> None:
    resp = await client.put(
        "/api/v1/systems",
        json={
            "system_id": "hr-screener",
            "purpose": "shortlist incoming CVs",
            "annex_iii_categories": ["annex3_4_employment"],
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text


def _span(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "trace_id": "a" * 32,
        "span_id": "b" * 16,
        "system_id": "hr-screener",
        "deployment": "prod",
        "risk_tier": "auto",
        "started_at": datetime(2026, 5, 7, 10, 0, tzinfo=UTC).isoformat(),
        "ended_at": datetime(2026, 5, 7, 10, 0, 1, tzinfo=UTC).isoformat(),
        "latency_ms": 1000,
        "model_provider": "openai",
        "model_name": "gpt-4o",
        "input_hash": "f" * 64,
        "input_chars": 100,
        "output_hash": "e" * 64,
        "output_chars": 50,
        "sources": [{"uri": "kb://policy/x", "version": "v1"}],
        "user_role": "recruiter",
        "metadata": {},
        "sdk_version": "0.1.0",
        "sdk_lang": "python",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_404_when_system_undeclared(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    resp = await client.get(
        "/api/v1/systems/never/annex-iv",
        headers={"Authorization": f"Bearer {plaintext}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_markdown_default_format(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}
    await _declare_high_risk(client, headers)

    resp = await client.get(
        "/api/v1/systems/hr-screener/annex-iv", headers=headers
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/markdown")
    assert resp.headers["X-Document-Id"]
    body = resp.text
    # Cover banner present.
    assert "Annex IV — Technical Documentation" in body
    assert "Allegato IV — Documentazione Tecnica" in body
    # Tier label appears in cover badge + §1.4 + §3.1.
    assert "HIGH" in body
    # Triggered rule with bilingual labels.
    assert "annex3_4_employment" in body
    assert "Employment and workers management" in body
    assert "Occupazione, gestione dei lavoratori" in body
    # Top-design appendices.
    assert "Compliance gap analysis" in body
    assert "Glossary / Glossario" in body
    assert "Document control" in body
    # Executive summary section.
    assert "Executive summary" in body
    # Disclaimer permanent — non-negotiable.
    assert "AnnexKit is not a law firm" in body


@pytest.mark.asyncio
async def test_markdown_includes_aggregations_after_ingest(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}
    await _declare_high_risk(client, headers)

    # Ingest two spans for that system — different trace ids so they
    # don't collide on the idempotency key.
    for i in range(2):
        await client.post(
            "/api/v1/spans",
            json=_span(
                trace_id=f"{i:032x}",
                span_id=f"{i:016x}",
            ),
            headers=headers,
        )

    resp = await client.get(
        "/api/v1/systems/hr-screener/annex-iv", headers=headers
    )
    assert resp.status_code == 200
    body = resp.text
    # Total invocations row should reflect the 2 ingested spans.
    assert "**Total invocations** | 2" in body
    # Models table should mention gpt-4o.
    assert "gpt-4o" in body
    # Sources table should mention kb://policy/x.
    assert "kb://policy/x" in body
    # SDK versions row.
    assert "0.1.0" in body


@pytest.mark.asyncio
async def test_audit_log_records_generation(
    client: AsyncClient,
    db_session: AsyncSession,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}
    await _declare_high_risk(client, headers)

    resp = await client.get(
        "/api/v1/systems/hr-screener/annex-iv", headers=headers
    )
    assert resp.status_code == 200
    document_id = resp.headers["X-Document-Id"]

    audits = (
        await db_session.execute(
            select(AuditLog).where(AuditLog.action == "annex_iv.generated")
        )
    ).scalars().all()
    assert len(audits) == 1
    assert audits[0].details["document_id"] == document_id
    assert audits[0].details["format"] == "md"


def _weasyprint_works() -> bool:
    """WeasyPrint imports fine even without Cairo/Pango — it fails at
    runtime. Probe with a tiny render so we can ``pytest.skip`` the PDF
    test cleanly on hosts without the native deps (the prod backend
    Docker image does have them; ``make backend-test`` covers PDF).
    """
    try:
        from weasyprint import HTML  # type: ignore[import-untyped]

        HTML(string="<html><body>x</body></html>").write_pdf()
        return True
    except Exception:
        return False


@pytest.mark.asyncio
@pytest.mark.skipif(
    not _weasyprint_works(),
    reason="WeasyPrint native libs (Cairo/Pango) not installed on this host",
)
async def test_pdf_format(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}
    await _declare_high_risk(client, headers)

    resp = await client.get(
        "/api/v1/systems/hr-screener/annex-iv?format=pdf", headers=headers
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    # PDFs start with "%PDF-".
    assert resp.content[:5] == b"%PDF-"
    assert resp.headers["content-disposition"].startswith("attachment;")


@pytest.mark.asyncio
async def test_unknown_format_returns_422(
    client: AsyncClient,
    authenticated_tenant: tuple[Tenant, str],
) -> None:
    _, plaintext = authenticated_tenant
    headers = {"Authorization": f"Bearer {plaintext}"}
    await _declare_high_risk(client, headers)

    resp = await client.get(
        "/api/v1/systems/hr-screener/annex-iv?format=xml", headers=headers
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_unauthorised_request_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/systems/anything/annex-iv")
    assert resp.status_code == 401
