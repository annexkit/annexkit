"""Public trust-center read service.

Read-only — no audit-log writes here. The trust page is meant to be
high-traffic (prospects, search bots, auditors), so every endpoint is
a single indexed query plus a Pydantic projection. No denormalised
materialised view yet; if traffic warrants we add one in M2.

Redaction happens in :func:`redact_provider_info` — a whitelist of
keys that are safe to publish. New keys default to redacted; you have
to explicitly add them to ``_PUBLIC_PROVIDER_FIELDS`` to surface them
on the trust page.
"""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_system import AISystem
from app.models.tenant import Tenant
from app.schemas.trust import (
    PublicProviderInfo,
    PublicReasoningEntry,
    PublicSystemDetail,
    PublicSystemSummary,
    PublicTenant,
    TierBreakdown,
    TrustOverview,
    TrustSystemDetailResponse,
    TrustSystemsResponse,
)

#: Whitelist of ``provider_info`` keys safe to expose on the public
#: trust page. New fields default to private; add them here only after
#: confirming with the user that publishing is intended.
_PUBLIC_PROVIDER_FIELDS: frozenset[str] = frozenset(
    {
        "legal_name",
        "address",
        "country",
        "authorised_representative",
        "system_version",
        "software_environment",
        "hardware_environment",
    }
)


async def get_tenant_by_slug(session: AsyncSession, slug: str) -> Tenant | None:
    return (await session.execute(select(Tenant).where(Tenant.slug == slug))).scalar_one_or_none()


async def overview(
    session: AsyncSession, tenant: Tenant, *, annexkit_version: str
) -> TrustOverview:
    rows = (
        (await session.execute(select(AISystem.risk_tier).where(AISystem.tenant_id == tenant.id)))
        .scalars()
        .all()
    )
    counter: Counter[str] = Counter(rows)
    return TrustOverview(
        tenant=PublicTenant(name=tenant.name, slug=tenant.slug),
        total_systems=len(rows),
        by_tier=TierBreakdown(
            unacceptable=counter.get("unacceptable", 0),
            high=counter.get("high", 0),
            limited=counter.get("limited", 0),
            minimal=counter.get("minimal", 0),
            auto=counter.get("auto", 0),
        ),
        annexkit_version=annexkit_version,
        as_of=datetime.now(UTC),
    )


async def list_systems(
    session: AsyncSession, tenant: Tenant, *, annexkit_version: str
) -> TrustSystemsResponse:
    rows = (
        (
            await session.execute(
                select(AISystem)
                .where(AISystem.tenant_id == tenant.id)
                .order_by(AISystem.system_id.asc())
            )
        )
        .scalars()
        .all()
    )
    return TrustSystemsResponse(
        tenant=PublicTenant(name=tenant.name, slug=tenant.slug),
        systems=[
            PublicSystemSummary(
                system_id=r.system_id,
                purpose=r.purpose,
                risk_tier=r.risk_tier,
                annex_iii_categories=list(r.annex_iii_categories),
                transparency_triggers=list(r.transparency_triggers),
                is_gpai=r.is_gpai,
                rules_version=r.rules_version,
                classified_at=r.classified_at,
            )
            for r in rows
        ],
        annexkit_version=annexkit_version,
        as_of=datetime.now(UTC),
    )


async def get_system(
    session: AsyncSession,
    tenant: Tenant,
    system_id: str,
    *,
    annexkit_version: str,
) -> TrustSystemDetailResponse | None:
    row = (
        await session.execute(
            select(AISystem)
            .where(AISystem.tenant_id == tenant.id)
            .where(AISystem.system_id == system_id)
        )
    ).scalar_one_or_none()
    if row is None:
        return None
    return TrustSystemDetailResponse(
        tenant=PublicTenant(name=tenant.name, slug=tenant.slug),
        system=PublicSystemDetail(
            system_id=row.system_id,
            purpose=row.purpose,
            risk_tier=row.risk_tier,
            annex_iii_categories=list(row.annex_iii_categories),
            prohibited_practices=list(row.prohibited_practices),
            transparency_triggers=list(row.transparency_triggers),
            is_gpai=row.is_gpai,
            rules_version=row.rules_version,
            reasoning=[PublicReasoningEntry(**e) for e in row.reasoning],
            classified_at=row.classified_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
            provider_info=PublicProviderInfo(**redact_provider_info(row.provider_info or {})),
        ),
        annexkit_version=annexkit_version,
        as_of=datetime.now(UTC),
    )


def redact_provider_info(info: dict[str, Any]) -> dict[str, Any]:
    """Return only the whitelist of keys safe to publish.

    Whitelist (not blacklist) approach so a future schema addition is
    private by default — you have to explicitly add a key to
    ``_PUBLIC_PROVIDER_FIELDS`` to surface it on the trust page.
    """
    return {k: v for k, v in info.items() if k in _PUBLIC_PROVIDER_FIELDS}


__all__ = [
    "_PUBLIC_PROVIDER_FIELDS",
    "get_system",
    "get_tenant_by_slug",
    "list_systems",
    "overview",
    "redact_provider_info",
]
