"""Pre-built demo scenarios for the public /demo/annex-iv page.

Three realistic AI-system stories that produce real-looking Annex IV
PDFs without persisting anything to the database. Powers the "try
AnnexKit without installing" page used in Show-HN / LinkedIn shares.

Each scenario returns a fully-populated :class:`AnnexIVContext` with
synthetic span aggregations (counts, latency percentiles, error rates)
baked in. The aggregator + classifier are bypassed — we just feed the
renderer pre-computed structured data.

Design notes:
  * Span aggregations are baked in, not generated. The point of the
    demo is "look at this realistic-looking doc", not "look at this
    classifier exercising itself" — the form generator on
    /tools/annex-iv-generator already covers the classifier-runs-live
    story.
  * Realistic numbers: 1-5K invocations, 0.2-0.8% error rate, p50
    latencies that match the model family (Haiku ~1s, GPT-4o ~2.5s).
  * One scenario per risk tier (high / limited / high) — covers the
    main shapes a prospect will see.
  * No PII. The system_id / purpose / provider info are clearly
    fictional ("Velmara Loans", "TopTalent", "Helios Support").
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

from app.schemas.annex_iv import (
    AISystemSnapshot,
    AnnexIVContext,
    ErrorBreakdownEntry,
    GapItem,
    LatencyStats,
    ModelUsage,
    ProviderInfoSnapshot,
    ReasoningSnapshot,
    SampleSpanRef,
    SourceUsage,
    SpanAggregations,
    TenantSnapshot,
    WindowStats,
)

ScenarioSlug = Literal["loan-screener", "cv-screener", "customer-support"]


def list_scenarios() -> list[dict[str, str]]:
    """Public catalogue — what /demo/annex-iv lists as cards."""
    return [
        {
            "slug": "loan-screener",
            "name": "Loan eligibility screener",
            "tier": "high",
            "annex_iii": "§5 Essential services (credit scoring)",
            "model": "OpenAI gpt-4o-mini",
            "tagline": (
                "Pre-screens small-business loan applications with retrieval-grounded "
                "LLM calls. Final approval stays with human underwriters."
            ),
        },
        {
            "slug": "cv-screener",
            "name": "CV pre-screener",
            "tier": "high",
            "annex_iii": "§4 Employment and workers management",
            "model": "Anthropic claude-haiku-4-5",
            "tagline": (
                "Produces structured shortlist notes for recruiters. Real Annex III §4 "
                "scenario from the EU AI Act."
            ),
        },
        {
            "slug": "customer-support",
            "name": "Customer support chatbot",
            "tier": "limited",
            "annex_iii": "Art. 50 transparency only",
            "model": "Mistral mistral-small-latest",
            "tagline": (
                "Answers shipping / returns questions from a static KB. Limited-risk: "
                "Article 50 disclosure obligations apply, but not high-risk Annex III."
            ),
        },
    ]


def build(slug: ScenarioSlug, *, annexkit_version: str) -> AnnexIVContext:
    """Return the AnnexIVContext for a named scenario, fully populated."""
    if slug == "loan-screener":
        return _loan_screener(annexkit_version)
    if slug == "cv-screener":
        return _cv_screener(annexkit_version)
    if slug == "customer-support":
        return _customer_support(annexkit_version)
    raise ValueError(f"Unknown demo scenario slug: {slug!r}")


# ---------------------------------------------------------------------------
# Helpers shared across scenarios
# ---------------------------------------------------------------------------

# Demo timestamps anchored at 2026-05-23 16:00 UTC so the generated PDFs
# are reproducible across visits (each visit re-anchors `now` to the
# request time so "active in last 7 days" stays true).
def _now() -> datetime:
    return datetime.now(UTC)


def _windows(total: int, error_count: int, p50: int, p95: int, p99: int) -> list[WindowStats]:
    """Same numbers across 24h/7d/30d/all_time — demo simplification."""
    latency = LatencyStats(
        sample_size=total,
        p50_ms=p50,
        p95_ms=p95,
        p99_ms=p99,
        mean_ms=int((p50 + p95) / 2),
        max_ms=p99 + 50,
    )
    error_rate = round(error_count * 100.0 / total, 2) if total else None
    return [
        WindowStats(
            window=name,  # type: ignore[arg-type]
            total=total,
            error_count=error_count,
            error_rate_pct=error_rate,
            latency=latency,
        )
        for name in ("24h", "7d", "30d", "all_time")
    ]


def _sample_spans(model_label: str, now: datetime, n: int = 5) -> list[SampleSpanRef]:
    """N most-recent fake trace_ids — anchors in the appendix evidence."""
    return [
        SampleSpanRef(
            trace_id=uuid.uuid4().hex,
            span_id=uuid.uuid4().hex[:16],
            started_at=now - timedelta(minutes=i * 7),
            risk_tier="high",
            model=model_label,
            error=None,
        )
        for i in range(n)
    ]


def _gap_for(provider: ProviderInfoSnapshot, has_spans: bool) -> list[GapItem]:
    """Replicates annex_iv_aggregator._gap_analysis without coupling.

    Kept minimal — the renderer only needs status + note per section.
    """
    def gap(section: str, en: str, it: str, status: str, note: str | None = None) -> GapItem:
        return GapItem(
            section=section,
            requirement_en=en,
            requirement_it=it,
            status=status,  # type: ignore[arg-type]
            note=note,
        )

    return [
        gap("§1.1", "Intended purpose", "Finalità del sistema", "auto"),
        gap("§1.2", "Persons responsible", "Soggetti responsabili", "auto"),
        gap("§1.3", "System version + environment", "Versione + ambiente", "auto"),
        gap("§1.4", "Risk classification", "Classificazione di rischio", "auto"),
        gap("§2.1", "Methodology and design", "Metodologia e progettazione", "auto"),
        gap("§2.2", "Models in use", "Modelli utilizzati", "auto" if has_spans else "partial"),
        gap("§2.4", "Validation methodology", "Validazione e test", "auto"),
        gap("§3.2", "Article 12 — Logging", "Articolo 12 — Tracciatura", "auto"),
        gap("§3.4", "Article 14 — Human oversight", "Articolo 14", "auto"),
        gap("§4", "Article 9 — Risk management", "Articolo 9", "auto"),
        gap("§5", "Description of changes", "Storico modifiche", "auto"),
        gap("§6", "Harmonised standards", "Norme armonizzate", "manual",
            "Provider compliance team input required."),
        gap("§7", "EU declaration of conformity", "Dichiarazione UE", "manual",
            "Separate legal artefact — your legal counsel signs it."),
        gap("§8", "Post-market monitoring", "Monitoraggio post-mercato", "auto"),
        gap("§9", "Information for deployers", "Informazioni per i deployer", "auto"),
    ]


def _summary(system_id: str, tier_phrase: str, total: int, model_label: str, rate_pct: float) -> str:
    return (
        f"This document is the EU AI Act Annex IV technical documentation "
        f"for the AI system `{system_id}` ({tier_phrase}). Across the "
        f"observation window the system recorded {total:,} invocations via "
        f"{model_label}, with an observed error rate of {rate_pct:.2f}%. "
        f"The system is currently active. — Demo data for "
        f"annexkit.dev/demo/annex-iv; no real customer information."
    )


# ---------------------------------------------------------------------------
# Scenario 1: loan-screener (HIGH)
# ---------------------------------------------------------------------------

def _loan_screener(version: str) -> AnnexIVContext:
    now = _now()
    total = 4218
    errors = 14
    model_label = "openai/gpt-4o-mini"
    provider = ProviderInfoSnapshot(
        legal_name="Velmara Loans S.r.l.",
        address="Corso Garibaldi 12, 20121 Milano (MI), Italia",
        country="IT",
        contact_email="compliance@velmara-loans.demo",
        system_version="v2.4.1",
        software_environment="Python 3.13, FastAPI 0.136, OpenAI gpt-4o-mini, pgvector",
        hardware_environment="Hetzner Cloud CCX23 (4 vCPU dedicated, 16 GB RAM, EU)",
        validation_methods=(
            "Quarterly review of 200 randomly-sampled transcripts against "
            "the VelmaraLoans credit policy v3. Bias audit completed Q1 2026."
        ),
        notes=(
            "Architecture: prompt-engineered LLM with retrieval-augmented generation "
            "over a static credit-policy KB. No fine-tuning. Pre-screening only — "
            "no autonomous approval authority. Article 26 deployer obligations apply."
        ),
    )
    system = AISystemSnapshot(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        system_id="loan-screener",
        purpose=(
            "Conversational AI assistant that helps small-business owners "
            "self-assess their eligibility for loans up to EUR 100K. "
            "Retrieves relevant excerpts from a static policy knowledge "
            "base. Final loan decisions are made by human underwriters."
        ),
        annex_iii_categories=["annex3_5_essential_services"],
        prohibited_practices=[],
        transparency_triggers=["art50_chat_interaction"],
        is_gpai=False,
        provider_info=provider,
        risk_tier="high",
        rules_version="1.0.0",
        reasoning=[
            ReasoningSnapshot(
                rule_id="annex3_5_essential_services",
                rule_type="high_risk",
                article="Annex III, §5",
                name_it="Servizi essenziali (pubblici e privati)",
                name_en="Essential services",
            ),
        ],
        classified_at=now - timedelta(days=45),
        created_at=now - timedelta(days=45),
        updated_at=now - timedelta(days=3),
    )
    aggregations = SpanAggregations(
        total=total,
        error_count=errors,
        first_span_at=now - timedelta(days=42),
        last_span_at=now - timedelta(minutes=4),
        is_active=True,
        models=[
            ModelUsage(
                provider="openai",
                name="gpt-4o-mini",
                version="2024-11-20",
                invocations=total,
                first_seen=now - timedelta(days=42),
                last_seen=now - timedelta(minutes=4),
            ),
        ],
        sources=[
            SourceUsage(uri="kb://policy/eligibility-criteria", citations=2104, versions=["v3"]),
            SourceUsage(uri="kb://policy/required-documents", citations=1850, versions=["v2"]),
            SourceUsage(uri="kb://policy/loan-amounts", citations=1402, versions=["v1"]),
            SourceUsage(uri="kb://policy/approval-timeline", citations=986, versions=["v1"]),
        ],
        sdk_versions=["0.1.3"],
        deployments=["prod"],
        user_roles=["loan_applicant"],
        error_breakdown=[
            ErrorBreakdownEntry(error_class="openai.RateLimitError", count=9),
            ErrorBreakdownEntry(error_class="httpx.TimeoutException", count=5),
        ],
        windows=_windows(total=total, error_count=errors, p50=1843, p95=3210, p99=4109),
    )
    return AnnexIVContext(
        document_id=uuid.uuid4(),
        generated_at=now,
        annexkit_version=version,
        tenant=TenantSnapshot(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            name="Velmara Loans (demo)",
            slug="demo-loan-screener",
        ),
        system=system,
        aggregations=aggregations,
        changes=[],
        gap_analysis=_gap_for(provider, has_spans=True),
        sample_spans=_sample_spans(model_label, now),
        executive_summary=_summary(
            "loan-screener",
            "a HIGH-risk system under Annex III §5 (credit scoring)",
            total, model_label, errors * 100.0 / total,
        ),
    )


# ---------------------------------------------------------------------------
# Scenario 2: cv-screener (HIGH)
# ---------------------------------------------------------------------------

def _cv_screener(version: str) -> AnnexIVContext:
    now = _now()
    total = 1267
    errors = 3
    model_label = "anthropic/claude-haiku-4-5"
    provider = ProviderInfoSnapshot(
        legal_name="TopTalent S.r.l.",
        address="Via Manzoni 1, 20121 Milano (MI), Italia",
        country="IT",
        contact_email="compliance@toptalent.demo",
        system_version="v1.8.0",
        software_environment="Python 3.13, FastAPI, Anthropic claude-haiku-4-5-20251001",
        hardware_environment="AWS Frankfurt — c7i.large (no PII in payloads)",
        validation_methods=(
            "Manual review of 100 candidate-screening transcripts/month by the "
            "TopTalent compliance team. Bias audit per EU non-discrimination "
            "checklist completed 2026-03."
        ),
        notes=(
            "Prompt-engineered LLM, no fine-tuning, no retrieval. Pre-screening only; "
            "every shortlist note routed through a human recruiter (Article 14 / 26)."
        ),
    )
    system = AISystemSnapshot(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        system_id="cv-screener",
        purpose=(
            "Conversational AI assistant that produces structured shortlist "
            "notes for recruiters from candidate summaries. Hire/no-hire "
            "decisions are made by human recruiters."
        ),
        annex_iii_categories=["annex3_4_employment"],
        prohibited_practices=[],
        transparency_triggers=["art50_chat_interaction"],
        is_gpai=False,
        provider_info=provider,
        risk_tier="high",
        rules_version="1.0.0",
        reasoning=[
            ReasoningSnapshot(
                rule_id="annex3_4_employment",
                rule_type="high_risk",
                article="Annex III, §4",
                name_it="Occupazione, gestione dei lavoratori",
                name_en="Employment and workers management",
            ),
        ],
        classified_at=now - timedelta(days=30),
        created_at=now - timedelta(days=30),
        updated_at=now - timedelta(days=1),
    )
    aggregations = SpanAggregations(
        total=total,
        error_count=errors,
        first_span_at=now - timedelta(days=28),
        last_span_at=now - timedelta(minutes=17),
        is_active=True,
        models=[
            ModelUsage(
                provider="anthropic",
                name="claude-haiku-4-5",
                version="claude-haiku-4-5-20251001",
                invocations=total,
                first_seen=now - timedelta(days=28),
                last_seen=now - timedelta(minutes=17),
            ),
        ],
        sources=[],
        sdk_versions=["0.1.3"],
        deployments=["prod"],
        user_roles=["recruiter"],
        error_breakdown=[
            ErrorBreakdownEntry(error_class="anthropic.RateLimitError", count=2),
            ErrorBreakdownEntry(error_class="httpx.TimeoutException", count=1),
        ],
        windows=_windows(total=total, error_count=errors, p50=952, p95=1720, p99=2208),
    )
    return AnnexIVContext(
        document_id=uuid.uuid4(),
        generated_at=now,
        annexkit_version=version,
        tenant=TenantSnapshot(
            id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
            name="TopTalent (demo)",
            slug="demo-cv-screener",
        ),
        system=system,
        aggregations=aggregations,
        changes=[],
        gap_analysis=_gap_for(provider, has_spans=True),
        sample_spans=_sample_spans(model_label, now),
        executive_summary=_summary(
            "cv-screener",
            "a HIGH-risk system under Annex III §4 (employment)",
            total, model_label, errors * 100.0 / total,
        ),
    )


# ---------------------------------------------------------------------------
# Scenario 3: customer-support (LIMITED)
# ---------------------------------------------------------------------------

def _customer_support(version: str) -> AnnexIVContext:
    now = _now()
    total = 18742
    errors = 47
    model_label = "mistral/mistral-small-latest"
    provider = ProviderInfoSnapshot(
        legal_name="Helios Support S.r.l.",
        address="Piazza dei Mercanti 5, 20121 Milano (MI), Italia",
        country="IT",
        contact_email="compliance@helios-support.demo",
        system_version="v3.1.2",
        software_environment="Python 3.13, FastAPI, Mistral La Plateforme (Paris)",
        hardware_environment="Hetzner Falkenstein — CCX13 (EU residency)",
        validation_methods=(
            "Weekly review of 50 conversations against the Helios CSAT framework. "
            "Mistral La Plateforme used for full GDPR + EU data residency."
        ),
        notes=(
            "Architecture: prompt-engineered LLM + retrieval over a static product "
            "FAQ. No fine-tuning. Limited-risk: not Annex III, but Article 50 "
            "chatbot disclosure required."
        ),
    )
    system = AISystemSnapshot(
        id=uuid.UUID("00000000-0000-0000-0000-000000000003"),
        system_id="customer-support",
        purpose=(
            "Customer-facing chatbot answering shipping, returns, and product "
            "questions from a static FAQ. Escalates to human agents on demand."
        ),
        annex_iii_categories=[],
        prohibited_practices=[],
        transparency_triggers=["art50_chat_interaction"],
        is_gpai=False,
        provider_info=provider,
        risk_tier="limited",
        rules_version="1.0.0",
        reasoning=[
            ReasoningSnapshot(
                rule_id="art50_chat_interaction",
                rule_type="transparency",
                article="Art. 50(1)",
                name_it="Interazione diretta con persone",
                name_en="Direct interaction with humans",
            ),
        ],
        classified_at=now - timedelta(days=90),
        created_at=now - timedelta(days=90),
        updated_at=now - timedelta(days=7),
    )
    aggregations = SpanAggregations(
        total=total,
        error_count=errors,
        first_span_at=now - timedelta(days=88),
        last_span_at=now - timedelta(minutes=2),
        is_active=True,
        models=[
            ModelUsage(
                provider="mistral",
                name="mistral-small-latest",
                version="2025-09",
                invocations=total,
                first_seen=now - timedelta(days=88),
                last_seen=now - timedelta(minutes=2),
            ),
        ],
        sources=[
            SourceUsage(uri="kb://faq/shipping-eu", citations=6240, versions=["v4"]),
            SourceUsage(uri="kb://faq/returns-policy", citations=4521, versions=["v6"]),
            SourceUsage(uri="kb://faq/product-care", citations=3017, versions=["v2"]),
        ],
        sdk_versions=["0.1.3"],
        deployments=["prod"],
        user_roles=["customer"],
        error_breakdown=[
            ErrorBreakdownEntry(error_class="mistralai.RateLimitError", count=28),
            ErrorBreakdownEntry(error_class="httpx.TimeoutException", count=19),
        ],
        windows=_windows(total=total, error_count=errors, p50=687, p95=1240, p99=1612),
    )
    return AnnexIVContext(
        document_id=uuid.uuid4(),
        generated_at=now,
        annexkit_version=version,
        tenant=TenantSnapshot(
            id=uuid.UUID("00000000-0000-0000-0000-000000000003"),
            name="Helios Support (demo)",
            slug="demo-customer-support",
        ),
        system=system,
        aggregations=aggregations,
        changes=[],
        gap_analysis=_gap_for(provider, has_spans=True),
        sample_spans=_sample_spans(model_label, now),
        executive_summary=_summary(
            "customer-support",
            "a LIMITED-risk system under Article 50 transparency requirements",
            total, model_label, errors * 100.0 / total,
        ),
    )
