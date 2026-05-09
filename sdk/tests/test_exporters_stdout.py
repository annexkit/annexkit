"""StdoutExporter tests — JSON output to stream."""

from __future__ import annotations

import io
import json
from datetime import UTC, datetime

from annexkit.exporters.stdout import StdoutExporter
from annexkit.schema import Span


def test_export_writes_json_line() -> None:
    buf = io.StringIO()
    exporter = StdoutExporter(stream=buf)
    span = Span(
        system_id="x",
        started_at=datetime.now(UTC),
        sdk_version="0.1.0",
    )
    exporter.export(span)
    output = buf.getvalue()
    assert output.endswith("\n")
    parsed = json.loads(output.strip())
    assert parsed["system_id"] == "x"
    assert parsed["sdk_version"] == "0.1.0"


def test_export_one_line_per_span() -> None:
    buf = io.StringIO()
    exporter = StdoutExporter(stream=buf)
    for i in range(3):
        exporter.export(
            Span(
                system_id=f"x-{i}",
                started_at=datetime.now(UTC),
                sdk_version="0.1.0",
            )
        )
    lines = buf.getvalue().splitlines()
    assert len(lines) == 3
    for line in lines:
        json.loads(line)


def test_export_does_not_raise_on_broken_stream() -> None:
    class BrokenStream:
        def write(self, _: str) -> int:
            raise OSError("disk full")

        def flush(self) -> None:
            pass

    exporter = StdoutExporter(stream=BrokenStream())  # type: ignore[arg-type]
    # Must not raise — tracing failures must never break the user app.
    exporter.export(
        Span(
            system_id="x",
            started_at=datetime.now(UTC),
            sdk_version="0.1.0",
        )
    )
