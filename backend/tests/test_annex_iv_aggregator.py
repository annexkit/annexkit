"""Aggregator unit tests — span aggregations + change-history extraction.

Builds a tenant + AI system + a handful of spans + audit log entries
directly via the ORM, then asserts the aggregator produces the
expected :class:`AnnexIVContext`.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_system import AISystem
from app.models.audit_log import AuditLog
from app.models.span import Span
from app.models.tenant import Tenant
from app.services import annex_iv_aggregator


def _tenant_with_system(session: AsyncSession) -> tuple[Tenant, AISystem]:
    tenant = Tenant(name="Acme", slug=f"acme-{uuid.uuid4().hex[:6]}")
    session.add(tenant)
    return tenant, None  # filled below


@pytest.mark.asyncio
async def test_empty_aggregations_when_no_spans(db_session: AsyncSession) -> None:
    tenant = Tenant(name="Acme", slug="acme-empty")
    db_session.add(tenant)
    await db_session.flush()

    system = AISystem(
        tenant_id=tenant.id,
        system_id="bot",
        annex_iii_categories=["annex3_4_employment"],
        prohibited_practices=[],
        transparency_triggers=[],
        is_gpai=False,
        risk_tier="high",
        rules_version="1.0.0",
        reasoning=[
            {
                "rule_id": "annex3_4_employment",
                "rule_type": "high_risk",
                "article": "Annex III, §4",
                "name_it": "Occupazione",
                "name_en": "Employment",
            }
        ],
        classified_at=datetime.now(UTC),
    )
    db_session.add(system)
    await db_session.flush()

    ctx = await annex_iv_aggregator.gather(
        db_session, tenant=tenant, system=system, annexkit_version="0.0.1"
    )

    assert ctx.aggregations.total == 0
    assert ctx.aggregations.error_count == 0
    assert ctx.aggregations.first_span_at is None
    assert ctx.aggregations.last_span_at is None
    assert ctx.aggregations.models == []
    assert ctx.aggregations.sources == []
    assert ctx.aggregations.sdk_versions == []
    assert ctx.aggregations.deployments == []
    assert ctx.aggregations.user_roles == []
    assert ctx.system.risk_tier == "high"
    assert ctx.tenant.name == "Acme"


@pytest.mark.asyncio
async def test_aggregations_count_models_sources_errors(
    db_session: AsyncSession,
) -> None:
    tenant = Tenant(name="Acme", slug="acme-aggs")
    db_session.add(tenant)
    await db_session.flush()

    system = AISystem(
        tenant_id=tenant.id,
        system_id="bot",
        annex_iii_categories=[],
        prohibited_practices=[],
        transparency_triggers=[],
        is_gpai=False,
        risk_tier="minimal",
        rules_version="1.0.0",
        reasoning=[],
        classified_at=datetime.now(UTC),
    )
    db_session.add(system)
    await db_session.flush()

    base = datetime(2026, 5, 7, 10, 0, tzinfo=UTC)

    # 3 gpt-4o invocations, 1 gpt-3.5 invocation.
    spans = [
        ("openai", "gpt-4o", "2024-11-20", None),
        ("openai", "gpt-4o", "2024-11-20", None),
        ("openai", "gpt-4o", "2024-11-20", "ValueError: nope"),
        ("openai", "gpt-3.5", "0613", None),
    ]
    sources_per_span = [
        [{"uri": "kb://a", "version": "v1"}],
        [{"uri": "kb://a", "version": "v2"}, {"uri": "kb://b"}],
        [{"uri": "kb://b"}],
        [],
    ]
    for i, ((p, n, v, err), srcs) in enumerate(zip(spans, sources_per_span, strict=True)):
        db_session.add(
            Span(
                tenant_id=tenant.id,
                trace_id=f"trace{i:030d}",
                span_id=f"span{i:012d}",
                system_id="bot",
                deployment="prod" if i < 3 else "staging",
                risk_tier="auto",
                started_at=base + timedelta(seconds=i),
                model_provider=p,
                model_name=n,
                model_version=v,
                error=err,
                sources=srcs,
                sdk_version="0.1.0",
                user_role="customer" if i % 2 == 0 else "employee",
            )
        )
    await db_session.flush()

    ctx = await annex_iv_aggregator.gather(
        db_session, tenant=tenant, system=system, annexkit_version="0.0.1"
    )

    aggs = ctx.aggregations
    assert aggs.total == 4
    assert aggs.error_count == 1
    # SQLite drops tzinfo on TIMESTAMP round-trip; Postgres preserves
    # it. Assert TZ-naive equivalence so the test is dialect-portable.
    assert aggs.first_span_at is not None
    assert aggs.first_span_at.replace(tzinfo=None) == base.replace(tzinfo=None)
    assert aggs.last_span_at is not None
    assert aggs.last_span_at.replace(tzinfo=None) == (
        base + timedelta(seconds=3)
    ).replace(tzinfo=None)

    # Top model = gpt-4o with 3 invocations.
    assert aggs.models[0].name == "gpt-4o"
    assert aggs.models[0].invocations == 3
    assert aggs.models[1].name == "gpt-3.5"
    assert aggs.models[1].invocations == 1

    # Sources: kb://a appears in spans 0+1 (2 citations); kb://b in 1+2 (2 citations).
    by_uri = {s.uri: s for s in aggs.sources}
    assert by_uri["kb://a"].citations == 2
    assert by_uri["kb://a"].versions == ["v1", "v2"]
    assert by_uri["kb://b"].citations == 2

    assert aggs.sdk_versions == ["0.1.0"]
    assert set(aggs.deployments) == {"prod", "staging"}
    assert set(aggs.user_roles) == {"customer", "employee"}


@pytest.mark.asyncio
async def test_changes_pulled_from_audit_log(db_session: AsyncSession) -> None:
    tenant = Tenant(name="Acme", slug="acme-changes")
    db_session.add(tenant)
    await db_session.flush()

    system = AISystem(
        tenant_id=tenant.id,
        system_id="bot",
        annex_iii_categories=[],
        prohibited_practices=[],
        transparency_triggers=[],
        is_gpai=False,
        risk_tier="minimal",
        rules_version="1.0.0",
        reasoning=[],
        classified_at=datetime.now(UTC),
    )
    db_session.add(system)
    await db_session.flush()

    # Two ai_system events + one unrelated span.ingested event we should ignore.
    db_session.add_all(
        [
            AuditLog(
                tenant_id=tenant.id,
                action="ai_system.created",
                entity_type="ai_system",
                entity_id=system.id,
                details={"system_id": "bot"},
            ),
            AuditLog(
                tenant_id=tenant.id,
                action="ai_system.updated",
                entity_type="ai_system",
                entity_id=system.id,
                details={"system_id": "bot", "risk_tier": "high"},
            ),
            AuditLog(
                tenant_id=tenant.id,
                action="span.ingested",
                entity_type="span",
                entity_id=uuid.uuid4(),
                details={"system_id": "bot"},
            ),
        ]
    )
    await db_session.flush()

    ctx = await annex_iv_aggregator.gather(
        db_session, tenant=tenant, system=system, annexkit_version="0.0.1"
    )
    actions = [c.action for c in ctx.changes]
    assert actions == ["ai_system.created", "ai_system.updated"]
