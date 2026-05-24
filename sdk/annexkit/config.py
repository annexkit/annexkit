"""SDK runtime configuration.

Two ways to configure:

1. **Environment variables** (preferred — twelve-factor friendly):

       ANNEXKIT_API_KEY=ak_xxxxx           # enables HTTP exporter
       ANNEXKIT_COLLECTOR_URL=https://...  # default: https://annexkit.dev
       ANNEXKIT_EXPORTER=auto|stdout|http|noop  # default: auto
       ANNEXKIT_DISABLED=1                  # disables tracking globally
       ANNEXKIT_DEPLOYMENT=prod             # default deployment label

2. **Programmatic override** at startup:

       import annexkit
       annexkit.configure(api_key="ak_...", deployment="staging")

The "auto" exporter picks HTTP when ``api_key`` is set, otherwise
``stdout``. This keeps day-1 testing frictionless: ``pip install
annexkit`` + ``@track`` and you can already see spans in your logs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

DEFAULT_COLLECTOR_URL = "https://annexkit.dev"

ExporterName = Literal["auto", "stdout", "http", "noop"]


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Config:
    """Mutable SDK configuration. Singleton lives in ``annexkit._state``."""

    api_key: str | None = None
    collector_url: str = DEFAULT_COLLECTOR_URL
    exporter: ExporterName = "auto"
    disabled: bool = False
    deployment: str = "prod"

    @classmethod
    def from_env(cls) -> Config:
        """Build a Config from ``ANNEXKIT_*`` env vars, falling back to defaults."""
        raw_exporter = os.getenv("ANNEXKIT_EXPORTER", "auto").strip().lower()
        if raw_exporter not in ("auto", "stdout", "http", "noop"):
            raw_exporter = "auto"
        return cls(
            api_key=(os.getenv("ANNEXKIT_API_KEY") or None),
            collector_url=os.getenv("ANNEXKIT_COLLECTOR_URL", DEFAULT_COLLECTOR_URL),
            exporter=raw_exporter,  # type: ignore[arg-type]
            disabled=_truthy(os.getenv("ANNEXKIT_DISABLED")),
            deployment=os.getenv("ANNEXKIT_DEPLOYMENT", "prod"),
        )
