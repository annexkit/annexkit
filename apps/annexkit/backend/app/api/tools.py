"""``/api/v1/tools/*`` — public free tools.

These endpoints are **unauthenticated** and rate-limited per IP. They
power the marketing-driven ``annexkit.dev/tools/*`` pages: try the
Annex IV generator without an account, classify a system without
signing up, etc.

Each tool captures a lead (email) and the minimal context needed to
follow up. No tenant is created; no spans are persisted.

Current tools:
  * ``POST /tools/annex-iv-generator`` — form -> classify -> PDF
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response
from konformia_core.classifier import ANNEX
from konformia_core.schemas.evidence import IngestSpan

from app.api.deps import SessionDep
from app.config import settings
from app.rate_limit import limiter
from app.schemas.tools import AnnexIVGeneratorRequest
from app.services import anonymous_annex_iv, demo_scenarios
from app.services.annex_iv_renderer import render_markdown, render_pdf
from app.services.risk_classifier import (
    UnknownAnnexIIICategoryError,
    UnknownProhibitedRuleError,
    UnknownTransparencyTriggerError,
)

router = APIRouter(prefix="/tools", tags=["tools"])
logger = logging.getLogger("annexkit.tools")

# Aggressive limit — this endpoint is computational (PDF render via
# WeasyPrint is ~50-200ms + ~70KB allocation per call). 10 per hour
# per IP is plenty for a real user filling the form; tight enough to
# kill bots and accidental scripts.
_RATE_LIMIT_ANNEX_IV = "10/hour"


# ---- Article 12 logging schema (free tool) -----------------------------
#
# Returns the wire-format ``IngestSpan`` as JSON Schema. Article 12 of
# the EU AI Act requires automatic event logging for high-risk AI
# systems; this schema is what the AnnexKit SDK populates per call.
# Useful for: validators in OTel collectors, adapter authors, training
# material on what counts as a compliant log row.
#
# Two flavours:
#   * /article-12-schema/v1.json           — vanilla Pydantic export
#   * /article-12-schema-annotated/v1.json — same + x-aiact-* mapping
#
# Versioned URL — future shape change ships as /v2.json, never silently
# breaks existing validators.

#: Per-field mapping from IngestSpan property → which Article 12
#: clause it satisfies + human explanation. Used in the annotated
#: variant only.
_FIELD_ANNOTATIONS: dict[str, dict[str, str]] = {
    "trace_id": {
        "x-aiact-clause": "traceability identifier",
        "x-purpose": (
            "Article 12 §1 — events must be linkable across the system. "
            "trace_id is the OTel-style root identifier the SDK generates "
            "per logical AI operation."
        ),
    },
    "span_id": {
        "x-aiact-clause": "event identifier",
        "x-purpose": "Unique per recorded event; lets auditors anchor an evidence row.",
    },
    "parent_span_id": {
        "x-aiact-clause": "parent linkage",
        "x-purpose": "Optional. Reconstructs sub-call hierarchies (RAG → LLM).",
    },
    "system_id": {
        "x-aiact-clause": "AI system identifier",
        "x-purpose": (
            "Article 12 §2(a) — the system whose use is being logged. Stable "
            "per AnnexKit declaration."
        ),
    },
    "deployment": {
        "x-aiact-clause": "environment label",
        "x-purpose": "Differentiates prod / staging / dev so audit logs scope correctly.",
    },
    "risk_tier": {
        "x-aiact-clause": "classification snapshot",
        "x-purpose": (
            "Annex III classification at time of inference. 'auto' means the "
            "collector resolves from the AISystem declaration on ingest."
        ),
    },
    "purpose": {
        "x-aiact-clause": "intended purpose context (Annex IV §1(a))",
        "x-purpose": "Optional inline override of the declared purpose.",
    },
    "started_at": {
        "x-aiact-clause": "Article 12 §2(b) — period of use (start)",
        "x-purpose": "UTC, ISO 8601. Required.",
    },
    "ended_at": {
        "x-aiact-clause": "Article 12 §2(b) — period of use (end)",
        "x-purpose": "UTC. Null if the operation crashed before completion.",
    },
    "latency_ms": {
        "x-aiact-clause": "performance evidence (Article 15 + post-market)",
        "x-purpose": "Annex IV §3.3 latency tables aggregate this across time windows.",
    },
    "model_provider": {
        "x-aiact-clause": "model provenance",
        "x-purpose": "Annex IV §2.2 — provider name (e.g. 'anthropic', 'openai', 'mistral').",
    },
    "model_name": {
        "x-aiact-clause": "model provenance",
        "x-purpose": "Family/name (e.g. 'claude-haiku-4-5', 'gpt-4o-mini').",
    },
    "model_version": {
        "x-aiact-clause": "model provenance",
        "x-purpose": "Specific version string (e.g. 'claude-haiku-4-5-20251001').",
    },
    "input_hash": {
        "x-aiact-clause": "Article 12 §2(c) — input data evidence (privacy-preserving)",
        "x-purpose": (
            "SHA-256 hex of the serialised input. Never plaintext — the SDK "
            "hashes before transport (project non-negotiable #7)."
        ),
    },
    "input_chars": {
        "x-aiact-clause": "input data evidence (size)",
        "x-purpose": "Char count. Useful for auditors without leaking content.",
    },
    "output_hash": {
        "x-aiact-clause": "Article 12 §2(c) — output evidence (privacy-preserving)",
        "x-purpose": "SHA-256 hex of the serialised output.",
    },
    "output_chars": {
        "x-aiact-clause": "output evidence (size)",
        "x-purpose": "Char count of the serialised output.",
    },
    "sources": {
        "x-aiact-clause": "Article 12 + Annex IV §2.3 — reference data used",
        "x-purpose": (
            "Retrieval sources (URIs + content hash + version). For RAG "
            "systems this is how auditors verify the system grounded its output."
        ),
    },
    "user_role": {
        "x-aiact-clause": "Article 13/14 — human oversight context",
        "x-purpose": (
            "Role of the user invoking the system (e.g. 'loan_officer', "
            "'recruiter', 'customer'). NOT a personal identifier."
        ),
    },
    "error": {
        "x-aiact-clause": "Article 12 §2 — adverse event recording",
        "x-purpose": "'<module>.<class>: <message>' when the wrapped function raised.",
    },
    "metadata": {
        "x-aiact-clause": "extension point",
        "x-purpose": "Free-form dict for adapter authors. Not interpreted by the collector.",
    },
    "sdk_version": {
        "x-aiact-clause": "evidence provenance",
        "x-purpose": "SDK version that produced this span — flags spans from outdated SDKs.",
    },
    "sdk_lang": {
        "x-aiact-clause": "evidence provenance",
        "x-purpose": "'python', 'typescript' (when the TS SDK lands), etc.",
    },
}


def _annotate(schema: dict) -> dict:
    """Add x-aiact-* annotations to each top-level property in the schema."""
    props = schema.get("properties", {})
    for field_name, annot in _FIELD_ANNOTATIONS.items():
        if field_name in props:
            for k, v in annot.items():
                props[field_name][k] = v
    schema["title"] = "AnnexKit Span — Article 12 logging schema (annotated)"
    schema["description"] = (
        "Wire-format schema for AnnexKit spans, with annotations mapping "
        "each field to the EU AI Act Article 12 clause it helps satisfy. "
        "See annexkit.dev/tools/logging-schema for usage examples."
    )
    schema["x-version"] = "1.0.0"
    schema["x-source"] = "https://annexkit.dev/api/v1/tools/article-12-schema-annotated/v1.json"
    return schema


@router.get(
    "/article-12-schema/v1.json",
    summary="JSON Schema (v1) for AnnexKit Article 12 logging spans",
    description=(
        "Raw JSON Schema (Pydantic export) for the wire-format span the "
        "AnnexKit SDK POSTs to `/api/v1/spans`. Use to validate spans "
        "before sending — e.g. in an OTel collector pipeline, in a "
        "custom adapter, or in CI tests that assert span shape.\n\n"
        "Versioned URL — a future shape change ships as `/v2.json`."
    ),
)
async def get_article_12_schema_v1() -> dict:
    schema = IngestSpan.model_json_schema(mode="serialization")
    schema["title"] = "AnnexKit Span — Article 12 logging schema (v1)"
    schema["x-version"] = "1.0.0"
    schema["x-source"] = "https://annexkit.dev/api/v1/tools/article-12-schema/v1.json"
    return schema


@router.get(
    "/article-12-schema-annotated/v1.json",
    summary="JSON Schema (v1) + Article 12 clause mapping per field",
    description=(
        "Same as `/article-12-schema/v1.json` but each top-level "
        "property carries `x-aiact-clause` + `x-purpose` annotations "
        "showing exactly which Article 12 clause it satisfies and how. "
        "Use for documentation / training material; the vanilla "
        "variant is what validators want."
    ),
)
async def get_article_12_schema_annotated_v1() -> dict:
    return _annotate(IngestSpan.model_json_schema(mode="serialization"))


@router.get(
    "/rules.json",
    summary="Raw rule tree used by the public free tools",
    description=(
        "Returns the contents of `app/data/annex_iii.json` — the 8 "
        "Annex III high-risk categories (with use-cases), the 8 "
        "Article 5 prohibited practices, the 4 Article 50 "
        "transparency triggers, and the GPAI marker. Bilingual "
        "(it/en).\n\n"
        "Powers the form on `annexkit.dev/tools/annex-iv-generator` "
        "and `/tools/classifier`. Stable contract — versioned via "
        "`annex_iii.json`'s `version` field."
    ),
)
async def get_rules() -> dict:
    """Return the parsed annex_iii.json content."""
    return ANNEX.raw


# ---- Demo browser scenarios (free tool, no install) -------------------

@router.get(
    "/demo/scenarios",
    summary="List the pre-built demo scenarios powering /demo/annex-iv",
    description=(
        "Returns the catalogue (slug, name, tier, model) the demo page "
        "renders as cards. The actual PDF for a scenario comes from "
        "`/tools/demo/{slug}/annex-iv?format=pdf`."
    ),
)
async def get_demo_scenarios() -> dict:
    return {"scenarios": demo_scenarios.list_scenarios()}


@router.get(
    "/demo/{slug}/annex-iv",
    summary="Pre-built Annex IV (PDF or markdown) for a demo scenario",
    description=(
        "Public, no-auth. Returns a realistic Annex IV for one of three "
        "pre-built scenarios (loan-screener, cv-screener, "
        "customer-support). No DB writes — the scenario data is baked "
        "into the codebase. `format=pdf` (default) or `format=md`."
    ),
    responses={
        200: {"content": {"application/pdf": {}, "text/markdown": {}}},
        404: {"description": "Unknown scenario slug"},
    },
)
async def get_demo_annex_iv(slug: str, format: str = "pdf") -> Response:
    try:
        ctx = demo_scenarios.build(slug, annexkit_version=settings.app_version)  # type: ignore[arg-type]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if format == "md":
        body = render_markdown(ctx)
        return Response(
            content=body,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f'inline; filename="annex-iv-demo-{slug}.md"',
                "X-Document-Id": str(ctx.document_id),
                "X-Risk-Tier": ctx.system.risk_tier,
            },
        )

    pdf_bytes = render_pdf(ctx)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="annex-iv-demo-{slug}.pdf"',
            "X-Document-Id": str(ctx.document_id),
            "X-Risk-Tier": ctx.system.risk_tier,
            # Scenario PDFs are deterministic per version — let Cloudflare
            # cache them across visitors for 1h.
            "Cache-Control": "public, max-age=3600",
        },
    )


@router.post(
    "/annex-iv-generator",
    summary="Generate an Annex IV PDF from a form (no account required)",
    description=(
        "Public, no-auth endpoint. Takes a system declaration via JSON "
        "form, classifies it deterministically against Annex III + "
        "Article 5 + Article 50 rules, renders the Annex IV technical "
        "documentation as a PDF, and returns the bytes.\n\n"
        "**Lead capture**: the `email` field is required and persisted "
        "to the `leads` table for follow-up. The PDF is generated in "
        "memory — no tenant / system / span rows are written.\n\n"
        f"**Rate limit**: {_RATE_LIMIT_ANNEX_IV} per IP."
    ),
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Annex IV PDF with X-Risk-Tier, X-Document-Id headers.",
        },
        422: {"description": "Form validation failed (unknown rule id, bad email, ...)"},
        429: {"description": "Rate limit exceeded."},
    },
)
@limiter.limit(_RATE_LIMIT_ANNEX_IV)
async def generate_annex_iv(
    request: Request,
    payload: AnnexIVGeneratorRequest,
    session: SessionDep,
) -> Response:
    client_host = request.client.host if request.client else None

    try:
        pdf_bytes, snapshot, ctx = await anonymous_annex_iv.generate_pdf_and_capture_lead(
            session,
            request=payload,
            annexkit_version=settings.app_version,
            ip_address=client_host,
        )
    except (
        UnknownAnnexIIICategoryError,
        UnknownProhibitedRuleError,
        UnknownTransparencyTriggerError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    logger.info(
        "annex_iv_generator: tier=%s rules_version=%s doc_id=%s ip=%s",
        snapshot.risk_tier,
        snapshot.rules_version,
        ctx.document_id,
        client_host or "-",
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers=anonymous_annex_iv.headers_for_pdf(snapshot, ctx),
    )
