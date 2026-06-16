"""Rate-limit contract tests for the public trust API.

The trust endpoints have no auth — anyone with the slug can hit them.
Without rate limiting, a single attacker can DOS the public trust page.
``slowapi`` caps each IP at ``60/minute``; this file pins that contract
so a future PR removing the decorator gets bounced in CI.

Note on isolation: ``slowapi``'s in-memory limiter is process-wide. The
``reset_limiter`` fixture clears its state before each test so order
doesn't matter and other trust-API tests don't accidentally consume
the budget for this test.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.rate_limit import limiter


@pytest.fixture(autouse=True)
def reset_limiter() -> None:
    """Clear the limiter's in-memory state before every test in this file."""
    limiter.reset()


@pytest.mark.asyncio
async def test_trust_overview_rate_limit_kicks_in_at_61(client: AsyncClient) -> None:
    """60 requests succeed; the 61st returns 429."""
    slug = "any-slug"  # 404 vs 200 doesn't matter — rate limit fires first.

    # 60 requests should all be allowed (we expect 404 because no tenant
    # exists with this slug, but we're not testing that here).
    for i in range(60):
        resp = await client.get(f"/api/v1/trust/{slug}")
        assert resp.status_code != 429, (
            f"request #{i + 1} unexpectedly rate-limited at status "
            f"{resp.status_code}"
        )

    # The 61st request should be rate-limited.
    resp = await client.get(f"/api/v1/trust/{slug}")
    assert resp.status_code == 429
    # slowapi's default handler returns a JSON body with `error` +
    # the limit string; the body proves the rejection is rate-limit-driven
    # (not a generic 429 from some other source). Header `Retry-After` is
    # not set by slowapi's default handler in v0.1.9 — don't pin it.
    body = resp.json()
    assert "60 per 1 minute" in body.get("error", ""), (
        f"expected rate-limit body, got {body!r}"
    )


@pytest.mark.asyncio
async def test_trust_systems_rate_limit_independent_of_overview(
    client: AsyncClient,
) -> None:
    """Each decorator instance counts independently per endpoint.

    Concretely: hitting /trust/<slug> 60 times consumes its own budget;
    /trust/<slug>/systems still has its own 60.

    (slowapi's default key is ``ip:endpoint:limit_string`` so different
    endpoints don't share a bucket.)
    """
    slug = "any-slug"

    # Exhaust /trust/<slug>
    for _ in range(60):
        await client.get(f"/api/v1/trust/{slug}")
    overview_blocked = await client.get(f"/api/v1/trust/{slug}")
    assert overview_blocked.status_code == 429

    # /trust/<slug>/systems should still be allowed — its budget is fresh.
    systems_resp = await client.get(f"/api/v1/trust/{slug}/systems")
    assert systems_resp.status_code != 429, (
        f"different endpoint should have its own rate-limit bucket; "
        f"got {systems_resp.status_code}"
    )


@pytest.mark.asyncio
async def test_trust_system_detail_is_rate_limited(client: AsyncClient) -> None:
    """The detail endpoint also has the @limiter.limit decorator."""
    slug = "any-slug"
    system_id = "any-system"

    for _ in range(60):
        await client.get(f"/api/v1/trust/{slug}/systems/{system_id}")

    blocked = await client.get(f"/api/v1/trust/{slug}/systems/{system_id}")
    assert blocked.status_code == 429
