"""AI system declaration service.

One public entry point — :func:`upsert` — for ``PUT /api/v1/systems``.
Plus :func:`get_by_system_id` and :func:`list_for_tenant` for the read
side.

Upsert semantics:
  * If a row with ``(tenant_id, system_id)`` exists, it's updated in
    place and reclassified.
  * Otherwise a new row is inserted and classified.
  * Either way, an ``audit_logs`` entry is written
    (``ai_system.upserted``).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_system import AISystem
from app.schemas.ai_system import AISystemDeclaration
from app.services import audit_service
from app.services.risk_classifier import classify_declaration


async def get_by_system_id(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    system_id: str,
) -> AISystem | None:
    return (
        await session.execute(
            select(AISystem)
            .where(AISystem.tenant_id == tenant_id)
            .where(AISystem.system_id == system_id)
        )
    ).scalar_one_or_none()


async def list_for_tenant(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
) -> list[AISystem]:
    rows = (
        (
            await session.execute(
                select(AISystem).where(AISystem.tenant_id == tenant_id).order_by(AISystem.system_id)
            )
        )
        .scalars()
        .all()
    )
    return list(rows)


async def upsert(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    payload: AISystemDeclaration,
) -> AISystem:
    """Create-or-update an AI system declaration; reclassify on every call.

    The classifier is deterministic — the same declaration always
    produces the same verdict. Reclassifying on every upsert keeps the
    DB in sync if ``annex_iii.json`` ever changes between deploys.
    """
    verdict = classify_declaration(
        annex_iii_categories=payload.annex_iii_categories,
        prohibited_practices=payload.prohibited_practices,
        transparency_triggers=payload.transparency_triggers,
        is_gpai=payload.is_gpai,
    )

    existing = await get_by_system_id(session, tenant_id=tenant_id, system_id=payload.system_id)
    classified_at = datetime.now(UTC)

    provider_info_dict = payload.provider_info.model_dump(exclude_none=True)

    if existing is None:
        row = AISystem(
            tenant_id=tenant_id,
            system_id=payload.system_id,
            purpose=payload.purpose,
            annex_iii_categories=list(payload.annex_iii_categories),
            prohibited_practices=list(payload.prohibited_practices),
            transparency_triggers=list(payload.transparency_triggers),
            is_gpai=payload.is_gpai,
            provider_info=provider_info_dict,
            risk_tier=verdict.tier,
            rules_version=verdict.rules_version,
            reasoning=verdict.to_reasoning_dicts(),
            classified_at=classified_at,
        )
        session.add(row)
        await session.flush()
        action = "ai_system.created"
    else:
        existing.purpose = payload.purpose
        existing.annex_iii_categories = list(payload.annex_iii_categories)
        existing.prohibited_practices = list(payload.prohibited_practices)
        existing.transparency_triggers = list(payload.transparency_triggers)
        existing.is_gpai = payload.is_gpai
        existing.provider_info = provider_info_dict
        existing.risk_tier = verdict.tier
        existing.rules_version = verdict.rules_version
        existing.reasoning = verdict.to_reasoning_dicts()
        existing.classified_at = classified_at
        await session.flush()
        row = existing
        action = "ai_system.updated"

    await audit_service.record(
        session,
        tenant_id=tenant_id,
        action=action,
        entity_type="ai_system",
        entity_id=row.id,
        details={
            "system_id": row.system_id,
            "risk_tier": row.risk_tier,
            "rules_version": row.rules_version,
            "annex_iii_categories": row.annex_iii_categories,
            "is_gpai": row.is_gpai,
        },
    )

    return row
