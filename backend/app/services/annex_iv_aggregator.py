"""Gather the data context for Annex IV rendering.

Pure read-only — no DB writes happen here. The audit-log entry for
"document generated" is the route layer's responsibility (so the
renderer can be tested against an in-memory context without touching
the audit trail).

Pipeline:

  1. Fetch the AISystem row + tenant (caller-supplied).
  2. Fetch ALL spans for the (tenant, system) ordered by started_at
     in a single query. The aggregator computes everything in Python
     from there: counts, error rates, percentile latencies, time-windowed
     slices, model groupings, source citations, deployments, user roles,
     SDK versions, error class breakdown, and a sample of recent spans
     for the appendix evidence section.
  3. Pull the system's audit-log change history.
  4. Compute the gap analysis (which Annex IV requirements are
     auto-populated, partially populated, or require provider input).
  5. Generate a brief executive summary.

For tenants with millions of spans this approach would be slow; M2's
plan is a denormalised ``system_stats`` materialised view refreshed on
a schedule. For per-system span counts in the 0-100K range -- the
expected MVP scenario -- single-fetch + Python is correct and clear.
"""

from __future__ import annotations

import uuid
from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_system import AISystem
from app.models.audit_log import AuditLog
from app.models.span import Span
from app.models.tenant import Tenant
from app.schemas.annex_iv import (
    AISystemSnapshot,
    AnnexIVContext,
    ChangeEvent,
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

_WINDOW_SPECS: list[tuple[str, timedelta | None]] = [
    ("24h", timedelta(hours=24)),
    ("7d", timedelta(days=7)),
    ("30d", timedelta(days=30)),
    ("all_time", None),
]
_SAMPLE_SPAN_LIMIT = 10


async def gather(
    session: AsyncSession,
    *,
    tenant: Tenant,
    system: AISystem,
    annexkit_version: str,
    now: datetime | None = None,
) -> AnnexIVContext:
    """Build the full :class:`AnnexIVContext` for one (tenant, system)."""
    now = now or datetime.now(UTC)
    document_id = uuid.uuid4()

    span_rows = await _fetch_spans(session, tenant_id=tenant.id, system_id=system.system_id)

    aggregations = _aggregate(span_rows, now=now)
    sample_spans = _sample_spans(span_rows)
    changes = await _collect_changes(
        session,
        tenant_id=tenant.id,
        system_db_id=system.id,
    )
    system_snapshot = _system_snapshot(system)
    gap_analysis = _gap_analysis(system_snapshot, aggregations)
    executive_summary = _executive_summary(
        system=system_snapshot, aggregations=aggregations, now=now
    )

    return AnnexIVContext(
        document_id=document_id,
        generated_at=now,
        annexkit_version=annexkit_version,
        tenant=TenantSnapshot(id=tenant.id, name=tenant.name, slug=tenant.slug),
        system=system_snapshot,
        aggregations=aggregations,
        changes=changes,
        gap_analysis=gap_analysis,
        sample_spans=sample_spans,
        executive_summary=executive_summary,
    )


def gather_anonymous(
    *,
    system: AISystemSnapshot,
    annexkit_version: str,
    now: datetime | None = None,
) -> AnnexIVContext:
    """Build an :class:`AnnexIVContext` without touching the DB.

    Powers the public ``/api/v1/tools/annex-iv-generator`` endpoint:
    an anonymous user fills the form, we classify deterministically,
    and we render a PDF on the fly. No tenant, no spans, no audit log
    entries (the lead-capture write goes to the ``leads`` table — see
    ``services.anonymous_annex_iv``).

    The resulting PDF looks like a v0-of-a-real-Annex-IV: the
    declarative §1.x and §2.1 are populated from the form, the
    runtime-dependent sections (§2.2 models, §3.2/§3.3 logging
    statistics, §8 post-market) show "no invocations recorded yet"
    placeholders, and the appendix gap analysis correctly flags those
    as missing-from-runtime rather than missing-from-the-doc.
    """
    now = now or datetime.now(UTC)
    aggregations = _aggregate([], now=now)
    gap_analysis = _gap_analysis(system, aggregations)
    executive_summary = _executive_summary(
        system=system, aggregations=aggregations, now=now
    )
    return AnnexIVContext(
        document_id=uuid.uuid4(),
        generated_at=now,
        annexkit_version=annexkit_version,
        tenant=TenantSnapshot(
            id=uuid.UUID(int=0),
            name="Anonymous (free tool)",
            slug="anonymous",
        ),
        system=system,
        aggregations=aggregations,
        changes=[],
        gap_analysis=gap_analysis,
        sample_spans=[],
        executive_summary=executive_summary,
    )


# ---------------------------------------------------------------------------
# DB fetches
# ---------------------------------------------------------------------------
async def _fetch_spans(
    session: AsyncSession, *, tenant_id: uuid.UUID, system_id: str
) -> list[Span]:
    rows = (
        (
            await session.execute(
                select(Span)
                .where(Span.tenant_id == tenant_id)
                .where(Span.system_id == system_id)
                .order_by(Span.started_at.asc())
            )
        )
        .scalars()
        .all()
    )
    return list(rows)


async def _collect_changes(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    system_db_id: uuid.UUID,
) -> list[ChangeEvent]:
    rows = (
        (
            await session.execute(
                select(AuditLog)
                .where(AuditLog.tenant_id == tenant_id)
                .where(AuditLog.entity_type == "ai_system")
                .where(AuditLog.entity_id == system_db_id)
                .where(AuditLog.action.in_(["ai_system.created", "ai_system.updated"]))
                .order_by(AuditLog.created_at.asc())
            )
        )
        .scalars()
        .all()
    )
    return [
        ChangeEvent(
            occurred_at=r.created_at,
            action=r.action,
            details=dict(r.details or {}),
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# In-memory aggregations
# ---------------------------------------------------------------------------
def _aggregate(spans: list[Span], *, now: datetime) -> SpanAggregations:
    if not spans:
        return SpanAggregations(
            total=0,
            error_count=0,
            first_span_at=None,
            last_span_at=None,
            is_active=False,
            windows=[
                WindowStats(
                    window=name,  # type: ignore[arg-type]
                    total=0,
                    error_count=0,
                    error_rate_pct=None,
                    latency=LatencyStats(),
                )
                for name, _ in _WINDOW_SPECS
            ],
        )

    first_at = spans[0].started_at
    last_at = spans[-1].started_at
    error_count = sum(1 for s in spans if s.error is not None)

    # ---- models grouped --------------------------------------------------
    model_counter: Counter[tuple[str | None, str | None, str | None]] = Counter()
    model_first: dict[tuple[Any, ...], datetime] = {}
    model_last: dict[tuple[Any, ...], datetime] = {}
    for s in spans:
        key = (s.model_provider, s.model_name, s.model_version)
        model_counter[key] += 1
        if key not in model_first or s.started_at < model_first[key]:
            model_first[key] = s.started_at
        if key not in model_last or s.started_at > model_last[key]:
            model_last[key] = s.started_at
    models = sorted(
        [
            ModelUsage(
                provider=k[0],
                name=k[1],
                version=k[2],
                invocations=v,
                first_seen=model_first[k],
                last_seen=model_last[k],
            )
            for k, v in model_counter.items()
        ],
        key=lambda m: m.invocations,
        reverse=True,
    )

    # ---- sources --------------------------------------------------------
    source_counts: Counter[str] = Counter()
    source_versions: dict[str, set[str]] = {}
    for s in spans:
        for src in s.sources or []:
            uri = src.get("uri")
            if not uri:
                continue
            source_counts[uri] += 1
            v = src.get("version")
            if v:
                source_versions.setdefault(uri, set()).add(v)
    sources = [
        SourceUsage(
            uri=uri,
            citations=cnt,
            versions=sorted(source_versions.get(uri, set())),
        )
        for uri, cnt in source_counts.most_common()
    ]

    # ---- simple sets ----------------------------------------------------
    sdk_versions = sorted({s.sdk_version for s in spans if s.sdk_version})
    deployments = sorted({s.deployment for s in spans if s.deployment})
    user_roles = sorted({s.user_role for s in spans if s.user_role})

    # ---- error breakdown ------------------------------------------------
    error_class_counter: Counter[str] = Counter()
    for s in spans:
        if s.error is None:
            continue
        # error format is "<module>.<class>: <message>" — pull the prefix
        head = s.error.split(":", 1)[0].strip()
        error_class_counter[head or "UnknownError"] += 1
    error_breakdown = [
        ErrorBreakdownEntry(error_class=cls, count=cnt)
        for cls, cnt in error_class_counter.most_common()
    ]

    # ---- windowed stats -------------------------------------------------
    windows: list[WindowStats] = []
    for name, delta in _WINDOW_SPECS:
        if delta is None:
            slice_spans = spans
        else:
            cutoff = _strip_tz(now) - delta
            slice_spans = [s for s in spans if _strip_tz(s.started_at) >= cutoff]
        slice_total = len(slice_spans)
        slice_errors = sum(1 for s in slice_spans if s.error is not None)
        latency_values = [s.latency_ms for s in slice_spans if s.latency_ms is not None]
        windows.append(
            WindowStats(
                window=name,  # type: ignore[arg-type]
                total=slice_total,
                error_count=slice_errors,
                error_rate_pct=(
                    round(slice_errors * 100.0 / slice_total, 2) if slice_total else None
                ),
                latency=_latency_stats(latency_values),
            )
        )

    return SpanAggregations(
        total=len(spans),
        error_count=error_count,
        first_span_at=first_at,
        last_span_at=last_at,
        is_active=_is_active(last_at, now),
        models=models,
        sources=sources,
        sdk_versions=sdk_versions,
        deployments=deployments,
        user_roles=user_roles,
        error_breakdown=error_breakdown,
        windows=windows,
    )


def _is_active(last_at: datetime | None, now: datetime) -> bool:
    if last_at is None:
        return False
    return (_strip_tz(now) - _strip_tz(last_at)) <= timedelta(days=7)


def _strip_tz(dt: datetime) -> datetime:
    """SQLite drops tzinfo on round-trip; Postgres keeps it. Compare
    naive-UTC for portability."""
    return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt


def _latency_stats(values: list[int]) -> LatencyStats:
    if not values:
        return LatencyStats()
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    return LatencyStats(
        sample_size=n,
        p50_ms=_percentile(sorted_vals, 50),
        p95_ms=_percentile(sorted_vals, 95),
        p99_ms=_percentile(sorted_vals, 99),
        mean_ms=int(sum(sorted_vals) / n),
        max_ms=sorted_vals[-1],
    )


def _percentile(sorted_vals: Sequence[int], p: float) -> int:
    """Linear-interpolation percentile (NumPy default)."""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    k = (n - 1) * p / 100
    f = int(k)
    c = min(f + 1, n - 1)
    if f == c:
        return sorted_vals[f]
    return int(sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f))


def _sample_spans(spans: list[Span]) -> list[SampleSpanRef]:
    # Most-recent N, descending.
    recent = sorted(spans, key=lambda s: s.started_at, reverse=True)[:_SAMPLE_SPAN_LIMIT]
    return [
        SampleSpanRef(
            trace_id=s.trace_id,
            span_id=s.span_id,
            started_at=s.started_at,
            risk_tier=s.risk_tier,
            model=_model_label(s.model_provider, s.model_name, s.model_version),
            error=s.error,
        )
        for s in recent
    ]


def _model_label(provider: str | None, name: str | None, version: str | None) -> str | None:
    parts = [p for p in (provider, name, version) if p]
    return "/".join(parts) if parts else None


def _system_snapshot(system: AISystem) -> AISystemSnapshot:
    pi = dict(system.provider_info or {})
    return AISystemSnapshot(
        id=system.id,
        system_id=system.system_id,
        purpose=system.purpose,
        annex_iii_categories=list(system.annex_iii_categories),
        prohibited_practices=list(system.prohibited_practices),
        transparency_triggers=list(system.transparency_triggers),
        is_gpai=system.is_gpai,
        provider_info=ProviderInfoSnapshot(**pi),
        risk_tier=system.risk_tier,
        rules_version=system.rules_version,
        reasoning=[ReasoningSnapshot(**entry) for entry in system.reasoning],
        classified_at=system.classified_at,
        created_at=system.created_at,
        updated_at=system.updated_at,
    )


# ---------------------------------------------------------------------------
# Gap analysis
# ---------------------------------------------------------------------------
def _gap_analysis(system: AISystemSnapshot, aggregations: SpanAggregations) -> list[GapItem]:
    """Map every Annex IV requirement to its evidence-completeness status.

    The gap section is one of the most useful surfaces for the user —
    it tells them exactly what AnnexKit covers automatically vs what
    their legal team / risk officer must still produce.
    """
    pi = system.provider_info
    has_some_provider = any(
        getattr(pi, f)
        for f in (
            "legal_name",
            "address",
            "country",
            "contact_email",
            "authorised_representative",
        )
    )
    has_full_provider_basics = all(
        getattr(pi, f) for f in ("legal_name", "address", "country", "contact_email")
    )
    has_spans = aggregations.total > 0

    items: list[GapItem] = []

    def add(section: str, en: str, it: str, status: str, note: str | None = None) -> None:
        items.append(
            GapItem(
                section=section,
                requirement_en=en,
                requirement_it=it,
                status=status,  # type: ignore[arg-type]
                note=note,
            )
        )

    add(
        "§1.1",
        "Intended purpose",
        "Finalità del sistema",
        "auto" if system.purpose else "manual",
        None if system.purpose else "Set 'purpose' on the AI system declaration.",
    )

    if has_full_provider_basics:
        provider_status = "auto"
        provider_note: str | None = None
    elif has_some_provider:
        provider_status = "partial"
        missing = [
            f for f in ("legal_name", "address", "country", "contact_email") if not getattr(pi, f)
        ]
        provider_note = f"Missing: {', '.join(missing)}."
    else:
        provider_status = "manual"
        provider_note = "Add provider_info on the AI system declaration."
    add(
        "§1.2",
        "Persons responsible (provider, address, contact)",
        "Soggetti responsabili (provider, indirizzo, contatto)",
        provider_status,
        provider_note,
    )
    add(
        "§1.3",
        "System version + software/hardware environment",
        "Versione del sistema + ambiente software/hardware",
        "auto" if pi.system_version and pi.software_environment else "manual",
        None
        if pi.system_version and pi.software_environment
        else "Add provider_info.system_version and software_environment.",
    )
    add(
        "§1.4",
        "Risk classification",
        "Classificazione di rischio",
        "auto",
        None,
    )
    add(
        "§2.1",
        "Methodology and design choices",
        "Metodologia e scelte di progettazione",
        "auto" if pi.notes else "manual",
        None if pi.notes else "Use provider_info.notes for design choices.",
    )
    add(
        "§2.2",
        "Models in use",
        "Modelli utilizzati",
        "auto" if has_spans else "partial",
        None if has_spans else "No invocations recorded yet.",
    )
    add(
        "§2.4",
        "Validation and testing methodology",
        "Metodologia di validazione e test",
        "auto" if pi.validation_methods else "manual",
        None if pi.validation_methods else "Add provider_info.validation_methods.",
    )
    add(
        "§3.2",
        "Article 12 — Logging",
        "Articolo 12 — Tracciatura",
        "auto" if has_spans else "partial",
        None if has_spans else "Begin tracking invocations via the SDK.",
    )
    add(
        "§3.4",
        "Article 14 — Human oversight",
        "Articolo 14 — Sorveglianza umana",
        "auto" if aggregations.user_roles else "partial",
        None if aggregations.user_roles else "Populate user_role on tracked invocations.",
    )
    add(
        "§4",
        "Article 9 — Risk management lifecycle",
        "Articolo 9 — Ciclo di gestione del rischio",
        "auto" if pi.notes else "manual",
        None if pi.notes else "Provider risk-management documentation required.",
    )
    add(
        "§5",
        "Description of changes",
        "Storico delle modifiche",
        "auto",
        None,
    )
    add(
        "§6",
        "Harmonised standards applied",
        "Norme armonizzate applicate",
        "manual",
        "Provider compliance team input required.",
    )
    add(
        "§7",
        "EU declaration of conformity (Article 47)",
        "Dichiarazione UE di conformità (Articolo 47)",
        "manual",
        "Separate legal artefact — your legal counsel signs it.",
    )
    add(
        "§8",
        "Post-market monitoring (Article 72)",
        "Monitoraggio post-mercato (Articolo 72)",
        "auto" if has_spans else "partial",
        None if has_spans else "Begin tracking invocations to populate metrics.",
    )
    add(
        "§9",
        "Information for deployers (Article 13)",
        "Informazioni per i deployer (Articolo 13)",
        "auto",
        None,
    )

    return items


# ---------------------------------------------------------------------------
# Executive summary
# ---------------------------------------------------------------------------
def _executive_summary(
    *, system: AISystemSnapshot, aggregations: SpanAggregations, now: datetime
) -> str:
    tier_phrase = {
        "unacceptable": "an UNACCEPTABLE-risk system (Article 5 prohibition triggered)",
        "high": "a HIGH-risk system under Annex III",
        "limited": "a LIMITED-risk system under Article 50 transparency requirements",
        "minimal": "a MINIMAL-risk system under the AI Act",
    }.get(system.risk_tier, f"a {system.risk_tier!r} system under the AI Act")

    purpose = system.purpose or "no declared purpose"

    if aggregations.total == 0:
        ops = (
            "No runtime invocations have been recorded for this system "
            "yet — the operational sections of this document will be "
            "populated automatically once the AnnexKit SDK is "
            "instrumenting calls in production."
        )
    else:
        primary_model = (
            f" via {aggregations.models[0].provider}/{aggregations.models[0].name}"
            if aggregations.models and aggregations.models[0].name
            else ""
        )
        active = "currently active" if aggregations.is_active else "not currently active"
        error_rate = (
            f"{aggregations.error_count * 100.0 / aggregations.total:.2f}%"
            if aggregations.total
            else "0%"
        )
        ops = (
            f"Between {aggregations.first_span_at:%Y-%m-%d %H:%M} UTC and "
            f"{aggregations.last_span_at:%Y-%m-%d %H:%M} UTC the system "
            f"recorded {aggregations.total} invocations{primary_model}, "
            f"with an observed error rate of {error_rate}. "
            f"The system is {active} (last invocation at "
            f"{aggregations.last_span_at:%Y-%m-%d %H:%M} UTC)."
        )

    return (
        f"This document is the EU AI Act Annex IV technical documentation "
        f"for the AI system `{system.system_id}`, classified as "
        f"{tier_phrase} (rules version {system.rules_version}). The "
        f"declared purpose is: {purpose}. "
        f"{ops}"
    )
