"""HTTP exporter — POST spans to the AnnexKit collector.

Synchronous ``httpx.Client``. The decorator wraps async use cases in a
thread (``asyncio.to_thread``) so async event loops aren't blocked.

v0.1 is best-effort: failures are logged at ``WARNING`` and the span is
dropped. Retries with exponential backoff land in v0.2 once we have a
real collector to test against.

Auth: ``Authorization: Bearer <api_key>``. The collector also accepts
``X-AnnexKit-Api-Key`` as a fallback for environments that strip
``Authorization`` (rare but seen in some reverse proxies).
"""

from __future__ import annotations

import logging

import httpx

from annexkit.exporters.base import Exporter
from annexkit.schema import Span

logger = logging.getLogger("annexkit.http")


class HttpExporter(Exporter):
    """POST spans to the AnnexKit collector."""

    def __init__(
        self,
        api_key: str,
        collector_url: str,
        *,
        timeout: float = 5.0,
        client: httpx.Client | None = None,
    ) -> None:
        # The optional ``client`` parameter is the seam for tests — pass
        # an ``httpx.Client(transport=httpx.MockTransport(...))`` and you
        # get full control over the network layer.
        self._collector_url = collector_url.rstrip("/")
        self._endpoint = f"{self._collector_url}/api/v1/spans"
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)
        # Headers are applied per-request (not on the client) so a
        # caller-supplied client doesn't need to pre-configure them.
        # User-Agent reads from the package metadata (same source as
        # SDK_VERSION) so the bumped pyproject.toml propagates here too.
        # Imported lazily to avoid an import cycle (_state imports this module).
        from annexkit._state import SDK_VERSION

        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "X-AnnexKit-Api-Key": api_key,
            "User-Agent": f"annexkit-python/{SDK_VERSION}",
            "Content-Type": "application/json",
        }

    def export(self, span: Span) -> None:
        try:
            resp = self._client.post(
                self._endpoint,
                json=span.model_dump(mode="json"),
                headers=self._headers,
            )
            if resp.status_code >= 400:
                logger.warning(
                    "AnnexKit collector rejected span (system_id=%s): HTTP %d %s",
                    span.system_id,
                    resp.status_code,
                    resp.text[:200],
                )
        except Exception as exc:
            logger.warning(
                "AnnexKit HTTP export failed (system_id=%s): %s",
                span.system_id,
                exc,
            )

    def shutdown(self) -> None:
        if self._owns_client:
            try:
                self._client.close()
            except Exception:
                logger.exception("AnnexKit HTTP client close failed")
