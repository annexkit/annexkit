"""Span schema contract tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from annexkit.schema import Source, Span


def test_minimal_span_construction() -> None:
    span = Span(
        system_id="x",
        started_at=datetime.now(UTC),
        sdk_version="0.1.0",
    )
    assert span.system_id == "x"
    assert span.deployment == "prod"
    assert span.risk_tier == "auto"
    assert span.sources == []
    assert span.metadata == {}


def test_span_auto_ids_are_unique() -> None:
    a = Span(system_id="x", started_at=datetime.now(UTC), sdk_version="0.1.0")
    b = Span(system_id="x", started_at=datetime.now(UTC), sdk_version="0.1.0")
    assert a.trace_id != b.trace_id
    assert a.span_id != b.span_id


def test_span_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Span.model_validate(
            {
                "system_id": "x",
                "started_at": datetime.now(UTC).isoformat(),
                "sdk_version": "0.1.0",
                "wat": "no",
            }
        )


def test_source_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Source.model_validate({"uri": "kb://x", "wat": "no"})


def test_span_json_roundtrip() -> None:
    src = Source(uri="kb://policies/001", hash="abc", version="v1")
    original = Span(
        system_id="bot",
        started_at=datetime(2026, 5, 7, 12, 0, tzinfo=UTC),
        sdk_version="0.1.0",
        sources=[src],
        metadata={"k": "v"},
    )
    payload = original.model_dump(mode="json")
    revived = Span.model_validate(payload)
    assert revived.sources[0].uri == "kb://policies/001"
    assert revived.metadata == {"k": "v"}
    assert revived.started_at == original.started_at


def test_risk_tier_must_be_valid() -> None:
    with pytest.raises(ValidationError):
        Span(
            system_id="x",
            started_at=datetime.now(UTC),
            sdk_version="0.1.0",
            risk_tier="cosmic",  # type: ignore[arg-type]
        )
