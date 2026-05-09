"""``annexkit.session(...)`` context-manager tests."""

from __future__ import annotations

import pytest

from annexkit import session


def test_session_records_span(collector) -> None:
    with session(system_id="rag", purpose="answer policy") as h:
        h.set_input("what's the refund policy?")
        h.attach_source(uri="kb://policies/refund-v3", hash="abc", version="v3")
        h.set_model(provider="mistral", name="mistral-small-latest")
        h.set_output("Refunds within 14 days...")
        h.set_user_role("customer")
        h.add_metadata(channel="web")

    assert len(collector.spans) == 1
    s = collector.spans[0]
    assert s.system_id == "rag"
    assert s.input_hash is not None
    assert s.output_hash is not None
    assert len(s.sources) == 1
    assert s.sources[0].uri == "kb://policies/refund-v3"
    assert s.model_provider == "mistral"
    assert s.model_name == "mistral-small-latest"
    assert s.user_role == "customer"
    assert s.metadata == {"channel": "web"}
    assert s.latency_ms is not None


def test_session_records_exception_and_reraises(collector) -> None:
    with pytest.raises(ValueError, match="bad"):  # noqa: SIM117
        with session(system_id="rag") as h:
            h.set_input("x")
            raise ValueError("bad")

    assert len(collector.spans) == 1
    assert "ValueError" in collector.spans[0].error


def test_set_error_with_string(collector) -> None:
    with session(system_id="rag") as h:
        h.set_error("manual error reason")
    assert collector.spans[0].error == "manual error reason"


def test_partial_set_model(collector) -> None:
    with session(system_id="rag") as h:
        h.set_model(provider="openai")
    s = collector.spans[0]
    assert s.model_provider == "openai"
    assert s.model_name is None
