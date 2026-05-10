"""``annexkit.session(...)`` — context manager for non-function tracing.

Useful when a single AI invocation spans multiple imperative steps that
don't fit naturally inside a function (notebook cells, orchestration
scripts, agent loops where the LLM call isn't at the top of a stack).

The context manager yields a :class:`SpanHandle` exposing setter methods
for the user to flesh out the span before it's exported on ``__exit__``.

Example:

    import annexkit

    with annexkit.session(
        system_id="rag-search",
        purpose="answer policy questions from internal KB",
    ) as span:
        span.set_input(user_query)
        docs = retriever.search(user_query)
        for d in docs:
            span.attach_source(uri=d.uri, hash=d.hash, version=d.version)
        answer = llm.generate(user_query, docs)
        span.set_output(answer)
        span.set_model(provider="mistral", name="mistral-small-latest")
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from annexkit import _state
from annexkit._hashing import hash_value, measure_chars
from annexkit.schema import RiskTier, Source, Span

logger = logging.getLogger("annexkit.session")


class SpanHandle:
    """User-facing handle inside a ``with annexkit.session(...)`` block.

    All setters mutate the wrapped Span in place. Methods never raise —
    bad input is logged and ignored so user code is not surprised by a
    tracing exception.
    """

    __slots__ = ("_span",)

    def __init__(self, span: Span) -> None:
        self._span = span

    @property
    def span(self) -> Span:
        """The underlying Span. Read-only contract — don't mutate directly."""
        return self._span

    # ---- Inputs / outputs --------------------------------------------------
    def set_input(self, value: Any) -> None:
        self._span.input_hash = hash_value(value)
        self._span.input_chars = measure_chars(value)

    def set_output(self, value: Any) -> None:
        self._span.output_hash = hash_value(value)
        self._span.output_chars = measure_chars(value)

    # ---- Retrieval ---------------------------------------------------------
    def attach_source(
        self,
        uri: str,
        *,
        hash: str | None = None,
        version: str | None = None,
    ) -> None:
        self._span.sources.append(Source(uri=uri, hash=hash, version=version))

    # ---- Model -------------------------------------------------------------
    def set_model(
        self,
        *,
        provider: str | None = None,
        name: str | None = None,
        version: str | None = None,
    ) -> None:
        if provider is not None:
            self._span.model_provider = provider
        if name is not None:
            self._span.model_name = name
        if version is not None:
            self._span.model_version = version

    # ---- Context -----------------------------------------------------------
    def set_user_role(self, role: str) -> None:
        self._span.user_role = role

    def set_error(self, exc: BaseException | str) -> None:
        if isinstance(exc, BaseException):
            self._span.error = f"{exc.__class__.__module__}.{exc.__class__.__qualname__}: {exc!s}"
        else:
            self._span.error = str(exc)

    def add_metadata(self, **fields: Any) -> None:
        self._span.metadata.update(fields)


@contextmanager
def session(
    system_id: str,
    *,
    risk_tier: RiskTier = "auto",
    purpose: str | None = None,
    deployment: str | None = None,
) -> Iterator[SpanHandle]:
    """Yield a :class:`SpanHandle` for the duration of the block.

    On exit (with or without exception), the span is timestamped, an
    error string is recorded if applicable, and the span is exported
    through the configured exporter.

    Exceptions inside the block are re-raised after recording.
    """
    cfg = _state.config()
    span = Span(
        system_id=system_id,
        deployment=deployment or cfg.deployment,
        risk_tier=risk_tier,
        purpose=purpose,
        started_at=datetime.now(UTC),
        sdk_version=_state.SDK_VERSION,
    )
    handle = SpanHandle(span)
    try:
        yield handle
    except Exception as exc:
        handle.set_error(exc)
        raise
    finally:
        span.ended_at = datetime.now(UTC)
        if span.started_at and span.ended_at:
            span.latency_ms = int((span.ended_at - span.started_at).total_seconds() * 1000)
        try:
            _state.export(span)
        except Exception:
            logger.exception("AnnexKit session export failed")
