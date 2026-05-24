"""Anonymous Annex IV generator service — backs ``POST /api/v1/tools/annex-iv-generator``.

The public free-tool endpoint accepts a form, classifies the declared
system deterministically, generates the Annex IV PDF in-memory, and
persists ONLY a lead row (email + minimal context) for marketing
follow-up. No tenant, no AISystem, no spans, no audit log entries are
written — all three of those require a real signed-up customer.

The classifier reuses the existing :mod:`app.services.risk_classifier`
(deterministic, never declassifies). The renderer reuses
:mod:`app.services.annex_iv_renderer`. The "no DB lookups" Annex IV
context comes from :func:`annex_iv_aggregator.gather_anonymous`.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.schemas.ai_system import ProviderInfo
from app.schemas.annex_iv import (
    AISystemSnapshot,
    AnnexIVContext,
    ProviderInfoSnapshot,
    ReasoningSnapshot,
)
from app.schemas.tools import AnnexIVGeneratorRequest
from app.services.annex_iv_aggregator import gather_anonymous
from app.services.annex_iv_renderer import render_pdf
from app.services.risk_classifier import classify_declaration
from app.services.risk_engine import Verdict


def build_anonymous_snapshot(
    request: AnnexIVGeneratorRequest,
    verdict: Verdict,
    now: datetime,
) -> AISystemSnapshot:
    """Map the public form into the snapshot shape the renderer expects.

    We synthesise a deterministic stand-in id from the email + system
    purpose so the same user generating twice gets the same id (useful
    if we later want to dedupe "they re-tried").
    """
    pi = _provider_info_to_snapshot(request.provider_info)
    seed = f"{request.email.lower()}::{request.purpose.strip()[:200]}"
    deterministic_id = uuid.uuid5(uuid.NAMESPACE_URL, seed)
    return AISystemSnapshot(
        id=deterministic_id,
        system_id="anonymous-tool-generation",
        purpose=request.purpose.strip(),
        annex_iii_categories=list(request.annex_iii_categories),
        prohibited_practices=list(request.prohibited_practices),
        transparency_triggers=list(request.transparency_triggers),
        is_gpai=request.is_gpai,
        provider_info=pi,
        risk_tier=verdict.tier,
        rules_version=verdict.rules_version,
        reasoning=[
            ReasoningSnapshot(
                rule_id=r.rule_id,
                rule_type=r.rule_type,
                article=r.article,
                name_it=r.name_it,
                name_en=r.name_en,
            )
            for r in verdict.reasons
        ],
        classified_at=now,
        created_at=now,
        updated_at=now,
    )


def _provider_info_to_snapshot(pi: ProviderInfo) -> ProviderInfoSnapshot:
    """The wire-format model is `ProviderInfo`; the renderer wants
    `ProviderInfoSnapshot`. Same shape, different schema family — copy
    the fields explicitly so extra-keys don't leak."""
    return ProviderInfoSnapshot(
        legal_name=pi.legal_name,
        address=pi.address,
        country=pi.country,
        contact_email=pi.contact_email,
        authorised_representative=pi.authorised_representative,
        system_version=pi.system_version,
        software_environment=pi.software_environment,
        hardware_environment=pi.hardware_environment,
        validation_methods=pi.validation_methods,
        notes=pi.notes,
    )


async def generate_pdf_and_capture_lead(
    session: AsyncSession,
    *,
    request: AnnexIVGeneratorRequest,
    annexkit_version: str,
    ip_address: str | None,
) -> tuple[bytes, AISystemSnapshot, AnnexIVContext]:
    """Run the full anonymous-generator pipeline.

    Steps:
      1. Classify the declaration via the deterministic rule engine.
      2. Build an in-memory ``AISystemSnapshot``.
      3. Build the full Annex IV context (no DB fetch).
      4. Render to PDF bytes.
      5. INSERT one row into ``leads`` with the email + minimal context.

    The lead INSERT happens AFTER the PDF render succeeds so a render
    failure doesn't leak emails for un-deliverable PDFs.

    Returns ``(pdf_bytes, snapshot, context)`` so the caller can:
      * write the bytes as the HTTP response body
      * read ``snapshot.risk_tier`` for response headers / metadata
      * read ``context.document_id`` for the X-Document-Id header
    """
    now = datetime.now(UTC)

    verdict = classify_declaration(
        annex_iii_categories=request.annex_iii_categories,
        prohibited_practices=request.prohibited_practices,
        transparency_triggers=request.transparency_triggers,
        is_gpai=request.is_gpai,
    )

    snapshot = build_anonymous_snapshot(request, verdict, now=now)
    ctx = gather_anonymous(
        system=snapshot,
        annexkit_version=annexkit_version,
        now=now,
    )

    pdf_bytes = render_pdf(ctx)

    declared: list[str] = (
        list(request.annex_iii_categories)
        + list(request.prohibited_practices)
        + list(request.transparency_triggers)
    )
    lead = Lead(
        email=request.email,
        source="annex-iv-generator",
        system_purpose=request.purpose[:1000],
        system_tier=verdict.tier,
        declared_categories=declared,
        ip_address=ip_address,
    )
    session.add(lead)
    await session.flush()

    return pdf_bytes, snapshot, ctx


def safe_filename(snapshot: AISystemSnapshot, ctx: AnnexIVContext) -> str:
    """Build a Content-Disposition-safe filename. Just slug + date."""
    date_slug = ctx.generated_at.strftime("%Y%m%d")
    return f"annex-iv-anonymous-{snapshot.risk_tier}-{date_slug}.pdf"


def headers_for_pdf(snapshot: AISystemSnapshot, ctx: AnnexIVContext) -> dict[str, Any]:
    """Standard response headers for the PDF download."""
    return {
        "Content-Disposition": f'attachment; filename="{safe_filename(snapshot, ctx)}"',
        "X-Document-Id": str(ctx.document_id),
        "X-Risk-Tier": snapshot.risk_tier,
        "X-Rules-Version": snapshot.rules_version,
    }
