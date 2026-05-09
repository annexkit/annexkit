"""Shared pytest fixtures for the SDK test suite.

The ``isolated_state`` fixture is autouse so every test starts with a
fresh Config + Exporter. Without it, the global singleton in
``annexkit._state`` would leak between tests and the test order would
matter (a known anti-pattern).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from annexkit import _state
from annexkit.exporters.base import Exporter
from annexkit.schema import Span


class CollectingExporter(Exporter):
    """Test double — accumulates exported spans in a list."""

    def __init__(self) -> None:
        self.spans: list[Span] = []
        self.flushed = 0
        self.shutdown_calls = 0

    def export(self, span: Span) -> None:
        self.spans.append(span)

    def flush(self) -> None:
        self.flushed += 1

    def shutdown(self) -> None:
        self.shutdown_calls += 1


@pytest.fixture(autouse=True)
def isolated_state() -> Iterator[None]:
    """Reset the SDK singleton between tests."""
    _state._reset_for_tests()
    yield
    _state._reset_for_tests()


@pytest.fixture
def collector() -> Iterator[CollectingExporter]:
    """Install a CollectingExporter and return it for assertions."""
    exporter = CollectingExporter()
    from annexkit import configure

    configure(exporter=exporter)
    yield exporter
