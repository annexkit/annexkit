"""``@track`` sync function tests."""

from __future__ import annotations

import pytest

from annexkit import __version__, track
from annexkit._hashing import hash_value


def test_basic_capture(collector) -> None:
    @track(system_id="bot", purpose="say hello")
    def greet(name: str) -> str:
        return f"hello {name}"

    out = greet("world")
    assert out == "hello world"
    assert len(collector.spans) == 1
    span = collector.spans[0]
    assert span.system_id == "bot"
    assert span.purpose == "say hello"
    assert span.risk_tier == "auto"
    assert span.error is None
    assert span.input_hash == hash_value({"name": "world"})
    assert span.output_hash == hash_value("hello world")
    assert span.latency_ms is not None
    assert span.latency_ms >= 0
    assert span.sdk_version == __version__


def test_kwargs_captured(collector) -> None:
    @track(system_id="bot")
    def f(a: int, b: int = 10) -> int:
        return a + b

    assert f(1, b=2) == 3
    span = collector.spans[0]
    assert span.input_hash == hash_value({"a": 1, "b": 2})


def test_exception_recorded_and_reraised(collector) -> None:
    @track(system_id="bot")
    def boom() -> None:
        raise ValueError("nope")

    with pytest.raises(ValueError, match="nope"):
        boom()
    span = collector.spans[0]
    assert "ValueError" in span.error
    assert "nope" in span.error
    # Output not captured on failure.
    assert span.output_hash is None


def test_signature_introspection_failure_falls_back_safely(collector) -> None:
    # Functions without an introspectable signature (built-ins) should
    # still work — decorator captures positional/kwargs verbatim.
    @track(system_id="bot")
    def f(*args, **kwargs):
        return sum(args) + sum(kwargs.values())

    assert f(1, 2, x=3) == 6
    assert len(collector.spans) == 1


def test_deployment_override(collector) -> None:
    @track(system_id="bot", deployment="staging")
    def f() -> int:
        return 1

    f()
    assert collector.spans[0].deployment == "staging"


def test_returns_native_function(collector) -> None:
    """The wrapper preserves docstring and __name__ via functools.wraps."""

    @track(system_id="bot")
    def greet(name: str) -> str:
        """Say hi."""
        return f"hi {name}"

    assert greet.__name__ == "greet"
    assert (greet.__doc__ or "").strip() == "Say hi."
