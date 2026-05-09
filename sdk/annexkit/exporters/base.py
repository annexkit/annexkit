"""Exporter abstract base.

All exporters are synchronous from the user's point of view. The
``@track`` decorator wraps async export in ``asyncio.to_thread`` so that
async event loops aren't blocked.

An exporter MUST NOT raise from ``export()`` — a tracing failure must
not break the user's app. Exceptions inside ``export()`` should be
caught and logged; the user's function continues.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from annexkit.schema import Span


class Exporter(ABC):
    """Where spans go after a tracked function returns."""

    @abstractmethod
    def export(self, span: Span) -> None:
        """Persist or transmit one span. Must not raise."""

    def flush(self) -> None:  # noqa: B027 — intentional no-op default, not abstract
        """Drain any internal buffer. Default: no-op.

        Override only if the exporter buffers (e.g. batched HTTP).
        Subclasses are NOT required to implement this — the base
        no-op is the right default for fire-and-forget exporters.
        """

    def shutdown(self) -> None:  # noqa: B027 — intentional no-op default, not abstract
        """Free resources (sockets, threads). Default: no-op.

        Override only if the exporter holds resources that survive
        the process (httpx client, file handles, threads). Subclasses
        are NOT required to implement.
        """
