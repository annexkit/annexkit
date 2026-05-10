"""SDK global state — single Config + lazy Exporter singleton.

This module is private (leading underscore). Public API lives in
``annexkit.__init__``. Splitting state into its own module avoids
circular imports between ``decorator.py`` / ``session.py`` / the
public ``__init__``.
"""

from __future__ import annotations

import logging
import threading
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from annexkit.config import Config
from annexkit.exporters.base import Exporter
from annexkit.exporters.http import HttpExporter
from annexkit.exporters.stdout import StdoutExporter
from annexkit.schema import Span

logger = logging.getLogger("annexkit")

#: Stamped into every span as ``sdk_version`` so the collector can flag
#: spans coming from old SDKs. Read from the installed package metadata
#: at import time, so a bump in ``pyproject.toml`` is the single source
#: of truth — no parallel constant to keep in sync. Fallback only fires
#: in editable / source-tree dev where the package isn't really
#: installed; the ``+dev`` local-version segment makes that case
#: visually obvious if it ever leaks into a span.
try:
    SDK_VERSION = version("annexkit")
except PackageNotFoundError:
    SDK_VERSION = "0.0.0+dev"

# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------
_config: Config = Config.from_env()
_exporter: Exporter | None = None
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Public-by-name (re-exported from annexkit.__init__)
# ---------------------------------------------------------------------------
def config() -> Config:
    """Return the current Config singleton (read-only contract)."""
    return _config


def configure(
    *,
    api_key: str | None = ...,  # type: ignore[assignment]
    collector_url: str = ...,  # type: ignore[assignment]
    exporter: Any = ...,  # str name or Exporter instance
    disabled: bool = ...,  # type: ignore[assignment]
    deployment: str = ...,  # type: ignore[assignment]
) -> None:
    """Override Config at runtime.

    Each kwarg is sentinel-defaulted so unspecified fields keep their
    current value. Pass an Exporter instance via ``exporter=`` to plug
    in a custom backend; pass a string ("auto"|"stdout"|"http"|"noop")
    to switch among the built-ins.
    """
    global _config, _exporter
    with _lock:
        if api_key is not ...:
            _config.api_key = api_key
        if collector_url is not ...:
            _config.collector_url = collector_url
        if disabled is not ...:
            _config.disabled = disabled
        if deployment is not ...:
            _config.deployment = deployment

        # Custom exporter instance → bypass _build_exporter entirely.
        if isinstance(exporter, Exporter):
            _shutdown_locked()
            _exporter = exporter
            return
        if isinstance(exporter, str):
            if exporter not in ("auto", "stdout", "http", "noop"):
                raise ValueError(
                    f"Unknown exporter name: {exporter!r}. "
                    "Use 'auto'|'stdout'|'http'|'noop' or pass an Exporter instance."
                )
            _config.exporter = exporter  # type: ignore[assignment]

        # Reset built-in exporter so the next export() call rebuilds it
        # from the new config.
        if not isinstance(exporter, Exporter):
            _shutdown_locked()


def _shutdown_locked() -> None:
    """Internal: shutdown current exporter, called holding ``_lock``."""
    global _exporter
    if _exporter is not None:
        try:
            _exporter.shutdown()
        except Exception:
            logger.exception("Exporter shutdown failed")
        _exporter = None


def _build_exporter(cfg: Config) -> Exporter:
    """Pick the built-in exporter based on Config."""
    if cfg.disabled:
        return _NoopExporter()
    if cfg.exporter == "stdout":
        return StdoutExporter()
    if cfg.exporter == "http":
        if not cfg.api_key:
            logger.warning(
                "ANNEXKIT_EXPORTER=http but ANNEXKIT_API_KEY is not set; "
                "falling back to stdout."
            )
            return StdoutExporter()
        return HttpExporter(api_key=cfg.api_key, collector_url=cfg.collector_url)
    if cfg.exporter == "noop":
        return _NoopExporter()
    # auto
    if cfg.api_key:
        return HttpExporter(api_key=cfg.api_key, collector_url=cfg.collector_url)
    return StdoutExporter()


def exporter() -> Exporter:
    """Return the active exporter, lazily constructed on first use."""
    global _exporter
    if _exporter is None:
        with _lock:
            if _exporter is None:
                _exporter = _build_exporter(_config)
    return _exporter


def export(span: Span) -> None:
    """Send one span through the active exporter. Never raises."""
    if _config.disabled:
        return
    try:
        exporter().export(span)
    except Exception:
        logger.exception("AnnexKit export failed")


def flush() -> None:
    """Drain any in-memory buffer. Useful before process exit."""
    if _exporter is not None:
        try:
            _exporter.flush()
        except Exception:
            logger.exception("AnnexKit flush failed")


def shutdown() -> None:
    """Free exporter resources (sockets, threads). Idempotent."""
    with _lock:
        _shutdown_locked()


# ---------------------------------------------------------------------------
# Test helpers — not part of the public API
# ---------------------------------------------------------------------------
def _reset_for_tests() -> None:
    """Reset Config + exporter to env defaults. Tests only."""
    global _config
    with _lock:
        _config = Config.from_env()
        _shutdown_locked()


class _NoopExporter(Exporter):
    """Drops every span on the floor. Used when ``disabled=True`` or
    when ``exporter="noop"`` is selected explicitly."""

    def export(self, span: Span) -> None:
        return None
