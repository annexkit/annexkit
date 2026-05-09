"""Stdout exporter — JSON spans to stderr.

Default exporter when no API key is configured. Writes one span per
line as JSON to ``sys.stderr`` (so it doesn't pollute application
``stdout``). Useful for:

  * Testing the SDK without standing up a collector.
  * Local development where a JSON log shipper picks up stderr.
  * Reproducing customer issues from copy-pasted log lines.

Format: a single line of JSON, suitable for ``jq``, Logfmt parsers, and
``grep``-friendly tooling. Datetime fields are ISO-8601 UTC.
"""

from __future__ import annotations

import json
import sys
from typing import TextIO

from annexkit.exporters.base import Exporter
from annexkit.schema import Span


class StdoutExporter(Exporter):
    """Write spans as JSON lines to ``stream`` (default: ``sys.stderr``)."""

    def __init__(self, stream: TextIO | None = None) -> None:
        # Resolve stderr lazily so monkeypatched stderr in tests works.
        self._stream = stream

    def _resolved_stream(self) -> TextIO:
        return self._stream if self._stream is not None else sys.stderr

    def export(self, span: Span) -> None:
        try:
            line = json.dumps(span.model_dump(mode="json"), default=str)
            stream = self._resolved_stream()
            stream.write(line + "\n")
            stream.flush()
        except Exception:
            # Tracing must never break the user's app — swallow.
            pass
