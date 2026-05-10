"""``/api/v1/systems`` — declare and read AI system classifications.

Endpoints:

  * ``PUT  /api/v1/systems``           — declare-or-update an AI system.
  * ``GET  /api/v1/systems``           — list systems for the auth'd tenant.
  * ``GET  /api/v1/systems/{system_id}`` — read one system declaration.

PUT is upsert-by-(tenant_id, system_id) so SDK adapters /
infrastructure-as-code tools can re-PUT idempotently. Each PUT
re-classifies via the deterministic engine and writes an audit log
entry — see :mod:`app.services.ai_system_service`.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.auth import TenantDep
from app.api.deps import SessionDep
from app.schemas.ai_system import (
    AISystemDeclaration,
    AISystemListResponse,
    AISystemRead,
)
from app.services import ai_system_service
from app.services.risk_classifier import (
    UnknownAnnexIIICategoryError,
    UnknownProhibitedRuleError,
    UnknownTransparencyTriggerError,
)

router = APIRouter(tags=["systems"])


@router.put(
    "/systems",
    status_code=status.HTTP_200_OK,
    response_model=AISystemRead,
    summary="Declare or update an AI system",
    description=(
        "Idempotent upsert keyed on `(tenant, system_id)`. Re-classifies "
        "the system on every call via the deterministic risk engine.\n\n"
        "**Auth**: Bearer token (`Authorization: Bearer ak_...`)."
    ),
)
async def upsert_system(
    payload: AISystemDeclaration,
    tenant: TenantDep,
    session: SessionDep,
) -> AISystemRead:
    try:
        row = await ai_system_service.upsert(session, tenant_id=tenant.id, payload=payload)
    except (
        UnknownAnnexIIICategoryError,
        UnknownProhibitedRuleError,
        UnknownTransparencyTriggerError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return AISystemRead.model_validate(row)


@router.get(
    "/systems",
    response_model=AISystemListResponse,
    summary="List AI systems for the authenticated tenant",
)
async def list_systems(
    tenant: TenantDep,
    session: SessionDep,
) -> AISystemListResponse:
    rows = await ai_system_service.list_for_tenant(session, tenant_id=tenant.id)
    return AISystemListResponse(
        systems=[AISystemRead.model_validate(r) for r in rows],
        total=len(rows),
    )


@router.get(
    "/systems/{system_id}",
    response_model=AISystemRead,
    summary="Read one AI system declaration + classification",
)
async def get_system(
    system_id: str,
    tenant: TenantDep,
    session: SessionDep,
) -> AISystemRead:
    row = await ai_system_service.get_by_system_id(
        session, tenant_id=tenant.id, system_id=system_id
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI system {system_id!r} not declared for this tenant",
        )
    return AISystemRead.model_validate(row)
