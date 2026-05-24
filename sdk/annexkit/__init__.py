"""annexkit — EU AI Act compliance pipeline for developers.

Quickstart:

    from annexkit import track

    @track(
        system_id="customer-bot",
        risk_tier="auto",
        purpose="answer customer questions on shipping and returns",
    )
    def chat(user_msg: str, user_role: str) -> str:
        ...

That's it. As ``chat(...)`` runs the SDK records:

  * start/end timestamps + latency
  * SHA-256 hashes of input/output (privacy-preserving)
  * model details (when known)
  * exception (if any)
  * SDK + system metadata

Spans go to stderr by default (great for testing). Set
``ANNEXKIT_API_KEY=ak_...`` to ship them to the AnnexKit collector
instead.

Configuration (env vars):

  * ``ANNEXKIT_API_KEY`` — enables HTTP exporter when set
  * ``ANNEXKIT_COLLECTOR_URL`` — default ``https://annexkit.dev``
  * ``ANNEXKIT_EXPORTER`` — ``auto|stdout|http|noop`` (default ``auto``)
  * ``ANNEXKIT_DISABLED`` — ``1`` to disable tracking globally
  * ``ANNEXKIT_DEPLOYMENT`` — default deployment label (``"prod"``)

Programmatic config: ``annexkit.configure(api_key="ak_...", deployment="staging")``.

Full docs at https://annexkit.dev/docs.
"""

from __future__ import annotations

from annexkit._state import SDK_VERSION as __version__  # noqa: N811 — Python convention
from annexkit._state import configure, flush, shutdown
from annexkit.decorator import track
from annexkit.schema import Source, Span
from annexkit.session import SpanHandle, session

__all__ = [
    "Source",
    "Span",
    "SpanHandle",
    "__version__",
    "configure",
    "flush",
    "session",
    "shutdown",
    "track",
]
