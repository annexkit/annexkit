"""``/api/v1/trust/{slug}`` — public trust-center API.

**No authentication.** These endpoints are intentionally public so a
tenant's trust page (``https://<slug>.annexkit.eu/trust`` long-term;
``http://localhost:3000/trust/<slug>`` in dev) renders for anyone with
the URL. The slug is the only identifier; tenants are NOT enumerable
(no ``GET /api/v1/trust`` to list them).

Sensitive fields are redacted in :mod:`app.services.trust_service`.
Operational telemetry (latency, error rates) is intentionally NOT
exposed; if a customer wants to share that with a prospect they share
the Annex IV PDF directly.

All "not found" cases return the same opaque ``404 {"detail":
"Not found"}`` so an attacker can't tell whether they probed a
non-existent slug, or a known slug whose system_id they guessed
wrong. Slug + system_id enumeration via differential-error-message
is closed.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.config import settings
from app.schemas.trust import (
    TrustOverview,
    TrustSystemDetailResponse,
    TrustSystemsResponse,
)
from app.services import trust_service

router = APIRouter(prefix="/trust", tags=["trust"])


@router.get(
    "/{slug}",
    response_model=TrustOverview,
    summary="Public trust-page overview for a tenant",
    description=(
        "Returns the tenant's name + count of declared AI systems "
        "broken down by EU AI Act risk tier. **No auth required** — "
        "the slug acts as the public URL."
    ),
)
async def get_overview(slug: str, session: SessionDep) -> TrustOverview:
    tenant = await trust_service.get_tenant_by_slug(session, slug)
    if tenant is None:
        raise _not_found()
    return await trust_service.overview(
        session, tenant, annexkit_version=settings.app_version
    )


@router.get(
    "/{slug}/systems",
    response_model=TrustSystemsResponse,
    summary="List the tenant's declared AI systems (public)",
)
async def list_systems(slug: str, session: SessionDep) -> TrustSystemsResponse:
    tenant = await trust_service.get_tenant_by_slug(session, slug)
    if tenant is None:
        raise _not_found()
    return await trust_service.list_systems(
        session, tenant, annexkit_version=settings.app_version
    )


@router.get(
    "/{slug}/systems/{system_id}",
    response_model=TrustSystemDetailResponse,
    summary="One declared AI system in detail (public)",
    description=(
        "Public detail view of a single AI system. ``provider_info`` "
        "is redacted to the whitelist of keys safe to publish; "
        "operational telemetry is not exposed."
    ),
)
async def get_system(
    slug: str, system_id: str, session: SessionDep
) -> TrustSystemDetailResponse:
    tenant = await trust_service.get_tenant_by_slug(session, slug)
    if tenant is None:
        raise _not_found()
    response = await trust_service.get_system(
        session, tenant, system_id, annexkit_version=settings.app_version
    )
    if response is None:
        raise _not_found()
    return response


def _not_found() -> HTTPException:
    """Single opaque 404 — see module docstring."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
    )
