"""Contract tests for ``/api/v1/tools/demo/*`` — the pre-built demos.

These endpoints serve realistic Annex IV PDFs without any DB writes,
backed by `app/services/demo_scenarios.py`. The contract that the
public /demo/annex-iv page depends on:

  * `GET /tools/demo/scenarios` lists exactly 3 scenarios.
  * Each scenario slug renders a real PDF (>10KB, %PDF- magic) with
    the right X-Risk-Tier header.
  * Unknown slug → 404, opaque message.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

EXPECTED_SCENARIOS = {
    "loan-screener": "high",
    "cv-screener": "high",
    "customer-support": "limited",
}


@pytest.mark.asyncio
async def test_scenarios_lists_all_three(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/tools/demo/scenarios")
    assert resp.status_code == 200
    slugs = {s["slug"] for s in resp.json()["scenarios"]}
    assert slugs == set(EXPECTED_SCENARIOS.keys())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "slug,expected_tier", list(EXPECTED_SCENARIOS.items())
)
async def test_demo_pdf_renders_for_scenario(
    client: AsyncClient, slug: str, expected_tier: str
) -> None:
    resp = await client.get(f"/api/v1/tools/demo/{slug}/annex-iv?format=pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.headers["x-risk-tier"] == expected_tier
    assert resp.content[:5] == b"%PDF-"
    # Each demo scenario produces a non-trivial PDF.
    assert len(resp.content) > 10_000


@pytest.mark.asyncio
async def test_demo_markdown_renders_for_scenario(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/tools/demo/loan-screener/annex-iv?format=md")
    assert resp.status_code == 200
    assert "text/markdown" in resp.headers["content-type"]
    body = resp.text
    # The scenario name should appear in the rendered markdown body.
    assert "loan-screener" in body
    assert "Annex IV" in body


@pytest.mark.asyncio
async def test_unknown_scenario_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/tools/demo/this-doesnt-exist/annex-iv?format=pdf")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_demo_pdf_carries_cache_header(client: AsyncClient) -> None:
    """PDFs are cacheable across visitors for an hour — Cloudflare-friendly."""
    resp = await client.get("/api/v1/tools/demo/cv-screener/annex-iv?format=pdf")
    assert resp.status_code == 200
    assert "public" in resp.headers.get("cache-control", "")
    assert "max-age=3600" in resp.headers.get("cache-control", "")
