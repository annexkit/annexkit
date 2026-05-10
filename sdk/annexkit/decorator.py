"""``@track`` — the primary user-facing API.

Auto-detects sync vs async via :func:`asyncio.iscoroutinefunction`.
Captures inputs, output, exception, and latency; ships a Span through
the configured exporter; *always* re-raises the original exception so
the decorator is invisible to the function's contract.

Privacy: input/output payloads are SHA-256 hashed before transport
(see ``_hashing.py``). Plaintext logging is intentionally not exposed
in v0.1 — it lands in v0.2 with explicit ``allow_plaintext=True``
opt-in plus encryption-at-rest on the collector.

Example:

    from annexkit import track

    @track(
        system_id="customer-support",
        risk_tier="auto",
        purpose="answer customer questions on shipping and returns",
    )
    def chat(user_msg: str, user_role: str) -> str:
        ...
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, TypeVar

from annexkit import _state
from annexkit._hashing import hash_value, measure_chars
from annexkit.schema import RiskTier, Span

logger = logging.getLogger("annexkit.track")

F = TypeVar("F", bound=Callable[..., Any])


def track(
    system_id: str,
    *,
    risk_tier: RiskTier = "auto",
    purpose: str | None = None,
    deployment: str | None = None,
) -> Callable[[F], F]:
    """Decorate a function (sync or async) to record an AI Act span.

    Args:
        system_id: stable identifier for the AI system this function
            belongs to (e.g. ``"loan-screener"``). Multiple functions
            can share an id when they're part of the same logical AI
            system.
        risk_tier: AI Act risk tier. ``"auto"`` (default) lets the
            collector classify from Annex III categories. Override only
            when classification has already happened upstream.
        purpose: human-readable description of what the system does.
            Required for high-risk systems' Annex IV documentation.
        deployment: environment label (``"prod"``, ``"staging"``...).
            Defaults to ``ANNEXKIT_DEPLOYMENT`` (else ``"prod"``).

    Returns the wrapped function with **identical** observable
    behaviour: same args, same return type, same exceptions raised.
    """

    def decorator(fn: F) -> F:
        # Resolve the function's signature once — cheap at decoration
        # time, would be a perf hit if done per call.
        signature = _try_get_signature(fn)

        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                span = _start_span(
                    args,
                    kwargs,
                    signature,
                    system_id,
                    risk_tier,
                    purpose,
                    deployment,
                )
                try:
                    result = await fn(*args, **kwargs)
                    _record_output(span, result)
                    return result
                except Exception as exc:
                    _record_error(span, exc)
                    raise
                finally:
                    _close_span(span)
                    # asyncio.to_thread keeps the event loop unblocked
                    # while the (sync) exporter does its I/O.
                    try:
                        await asyncio.to_thread(_state.export, span)
                    except Exception:
                        logger.exception("AnnexKit async export failed")

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            span = _start_span(
                args,
                kwargs,
                signature,
                system_id,
                risk_tier,
                purpose,
                deployment,
            )
            try:
                result = fn(*args, **kwargs)
                _record_output(span, result)
                return result
            except Exception as exc:
                _record_error(span, exc)
                raise
            finally:
                _close_span(span)
                _state.export(span)

        return sync_wrapper  # type: ignore[return-value]

    return decorator


# ---------------------------------------------------------------------------
# Internals — kept module-private but unprefixed so tests can introspect
# them via ``from annexkit.decorator import _start_span`` etc.
# ---------------------------------------------------------------------------
def _try_get_signature(fn: Callable[..., Any]) -> inspect.Signature | None:
    try:
        return inspect.signature(fn)
    except (TypeError, ValueError):
        # Some C-implemented callables don't expose a signature.
        return None


def _bound_args(signature: inspect.Signature | None, args: tuple, kwargs: dict) -> dict[str, Any]:
    """Best-effort {param_name: value} mapping for hashing. Never raises."""
    if signature is None:
        return {"args": list(args), "kwargs": dict(kwargs)}
    try:
        bound = signature.bind_partial(*args, **kwargs)
        return dict(bound.arguments)
    except TypeError:
        return {"args": list(args), "kwargs": dict(kwargs)}


def _start_span(
    args: tuple,
    kwargs: dict,
    signature: inspect.Signature | None,
    system_id: str,
    risk_tier: RiskTier,
    purpose: str | None,
    deployment: str | None,
) -> Span:
    cfg = _state.config()
    bound = _bound_args(signature, args, kwargs)
    return Span(
        system_id=system_id,
        deployment=deployment or cfg.deployment,
        risk_tier=risk_tier,
        purpose=purpose,
        started_at=datetime.now(UTC),
        input_hash=hash_value(bound),
        input_chars=measure_chars(bound),
        sdk_version=_state.SDK_VERSION,
    )


def _record_output(span: Span, result: Any) -> None:
    span.output_hash = hash_value(result)
    span.output_chars = measure_chars(result)


def _record_error(span: Span, exc: BaseException) -> None:
    span.error = f"{exc.__class__.__module__}.{exc.__class__.__qualname__}: {exc!s}"


def _close_span(span: Span) -> None:
    span.ended_at = datetime.now(UTC)
    if span.started_at and span.ended_at:
        span.latency_ms = int((span.ended_at - span.started_at).total_seconds() * 1000)
