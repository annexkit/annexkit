"""Span ingest endpoint.

``POST /api/v1/spans``
    Auth: ``Authorization: Bearer ak_<key>``
    Body: a single span matching ``app.schemas.span.IngestSpan`` (the
          mirror of ``annexkit.schema.Span``).

The thinness of this controller is intentional. CLAUDE.md non-negotiable
#4: route handlers validate + dispatch, nothing else. The persistence,
audit-log writing, and risk-tier mapping live in
``app/services/span_service.py``.

Returns ``202 Accepted`` rather than 201 Created — accepting the span is
not the same as having processed it (in v0.1 the work is done
synchronously, but in v0.2 we plan a background classifier that
upgrades the risk tier from ``"auto"`` after ingest).
"""

from __future__ import annotations

from fastapi import APIRouter, status
from konformia_core.schemas.evidence import IngestResponse, IngestSpan

from app.api.auth import TenantDep
from app.api.deps import SessionDep
from app.services import span_service

router = APIRouter(tags=["spans"])


@router.post(
    "/spans",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=IngestResponse,
    summary="Ingest one tracked LLM invocation",
    description=(
        "Receive a span from the AnnexKit SDK. The span is persisted "
        "append-mostly and a corresponding entry is written to the "
        "append-only audit log.\n\n"
        "**Auth**: Bearer token (`Authorization: Bearer ak_...`)."
    ),
)
async def ingest_span(
    payload: IngestSpan,
    tenant: TenantDep,
    session: SessionDep,
) -> IngestResponse:
    span = await span_service.ingest(
        session,
        tenant_id=tenant.id,
        payload=payload,
    )
    return IngestResponse(id=span.id, received_at=span.received_at)
