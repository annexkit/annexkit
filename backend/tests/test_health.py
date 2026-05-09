"""Smoke tests for the health and ping endpoints.

If these pass, `app.main:app` is importable, the router is wired, and
the basic FastAPI plumbing works. Add deeper integration tests under
their feature module (e.g. `test_ingest.py`) once those endpoints land.
"""

from __future__ import annotations

from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "annexkit-api"


async def test_ping(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/ping")
    assert resp.status_code == 200
    assert resp.json() == {"ping": "pong"}
