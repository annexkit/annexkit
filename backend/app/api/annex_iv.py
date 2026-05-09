"""``GET /api/v1/systems/{system_id}/annex-iv?format=md|pdf``.

Generates a fresh Annex IV technical-documentation document for the
named AI system. Markdown by default, PDF when ``?format=pdf``.

Each generation:
  * Reads the AI system declaration + span aggregations.
  * Builds the data context (``annex_iv_aggregator.gather``).
  * Renders to the requested format.
  * Writes ``annex_iv.generated`` to the audit log.

The bytes themselves are not persisted server-side in v0.1 — the
audit log is the canonical record of "this document was generated at
T for tenant X / system Y / document_id Z". A future
``GET /api/v1/documents/{document_id}`` can re-render against the
declaration as it stood at T using the audit history (deferred to
M2).
"""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse, Response

from app.api.auth import TenantDep
from app.api.deps import SessionDep
from app.config import settings
from app.services import ai_system_service, annex_iv_aggregator, audit_service
from app.services.annex_iv_renderer import render_markdown, render_pdf

router = APIRouter(tags=["annex-iv"])
logger = logging.getLogger("annexkit.annex_iv")

Format = Literal["md", "pdf"]


@router.get(
    "/systems/{system_id}/annex-iv",
    summary="Generate Annex IV technical documentation",
    description=(
        "Produces an EU AI Act Annex IV technical-documentation "
        "document for the named system, populated from the latest "
        "declaration + observed span telemetry.\n\n"
        "Use `?format=md` (default) for Markdown, `?format=pdf` for a "
        "WeasyPrint-rendered PDF.\n\n"
        "**Auth**: Bearer token (`Authorization: Bearer ak_...`)."
    ),
    responses={
        200: {
            "content": {
                "text/markdown": {},
                "application/pdf": {},
            },
            "description": "Annex IV document",
        },
        404: {"description": "System not declared for this tenant"},
    },
)
async def get_annex_iv(
    request: Request,
    system_id: str,
    tenant: TenantDep,
    session: SessionDep,
    format: Annotated[Format, Query(description="`md` (default) or `pdf`")] = "md",
) -> Response:
    system = await ai_system_service.get_by_system_id(
        session, tenant_id=tenant.id, system_id=system_id
    )
    if system is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI system {system_id!r} not declared for this tenant",
        )

    ctx = await annex_iv_aggregator.gather(
        session,
        tenant=tenant,
        system=system,
        annexkit_version=settings.app_version,
    )

    await audit_service.record(
        session,
        tenant_id=tenant.id,
        action="annex_iv.generated",
        entity_type="ai_system",
        entity_id=system.id,
        details={
            "document_id": str(ctx.document_id),
            "system_id": system.system_id,
            "risk_tier": system.risk_tier,
            "format": format,
            "request_id": getattr(request.state, "request_id", None),
        },
    )

    logger.info(
        "annex_iv generated: tenant=%s system=%s tier=%s format=%s document_id=%s",
        tenant.id,
        system.system_id,
        system.risk_tier,
        format,
        ctx.document_id,
    )

    safe_system_id = system.system_id.replace("/", "_").replace("..", "_")
    date_slug = ctx.generated_at.strftime("%Y%m%d")

    if format == "md":
        body = render_markdown(ctx)
        return PlainTextResponse(
            content=body,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": (
                    f'inline; filename="annex-iv-{safe_system_id}-{date_slug}.md"'
                ),
                "X-Document-Id": str(ctx.document_id),
            },
        )

    pdf_bytes = render_pdf(ctx)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="annex-iv-{safe_system_id}-{date_slug}.pdf"'
            ),
            "X-Document-Id": str(ctx.document_id),
        },
    )
