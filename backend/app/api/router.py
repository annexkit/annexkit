"""Top-level API router.

Each feature owns a sub-module under ``app/api/`` exposing its own
``router = APIRouter(...)``. This file aggregates them onto a single
``api_router`` mounted by ``app/main.py`` at ``/api/v1``.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.annex_iv import router as annex_iv_router
from app.api.spans import router as spans_router
from app.api.systems import router as systems_router
from app.api.tools import router as tools_router
from app.api.trust import router as trust_router

api_router = APIRouter()

api_router.include_router(spans_router)
api_router.include_router(systems_router)
# Annex IV router defines /systems/{system_id}/annex-iv — must mount
# AFTER the systems router because FastAPI matches routes in
# registration order.
api_router.include_router(annex_iv_router)
# Public trust-center API — intentionally no Bearer auth.
api_router.include_router(trust_router)
# Public free tools — no auth, aggressive per-IP rate limit, lead capture.
api_router.include_router(tools_router)


@api_router.get("/ping", tags=["meta"])
async def ping() -> dict[str, str]:
    """Versioned ping — useful as a smoke test that ``/api/v1/`` is wired."""
    return {"ping": "pong"}
