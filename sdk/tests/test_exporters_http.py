"""HttpExporter tests — uses httpx.MockTransport for hermetic networking."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from annexkit.exporters.http import HttpExporter
from annexkit.schema import Span


def _span() -> Span:
    return Span(
        system_id="x",
        started_at=datetime.now(UTC),
        sdk_version="0.1.0",
    )


def test_post_includes_auth_header_and_body() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        captured["body"] = request.content
        return httpx.Response(202)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    exporter = HttpExporter(
        api_key="ak_test",
        collector_url="https://example.test",
        client=client,
    )

    exporter.export(_span())

    assert captured["url"] == "https://example.test/api/v1/spans"
    assert captured["auth"] == "Bearer ak_test"
    assert b"system_id" in captured["body"]  # type: ignore[operator]


def test_4xx_response_logged_and_swallowed(caplog) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="unauthorised")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    exporter = HttpExporter(
        api_key="ak_test",
        collector_url="https://example.test",
        client=client,
    )

    with caplog.at_level("WARNING", logger="annexkit.http"):
        exporter.export(_span())

    assert any("HTTP 401" in r.message for r in caplog.records)


def test_network_error_swallowed(caplog) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    exporter = HttpExporter(
        api_key="ak_test",
        collector_url="https://example.test",
        client=client,
    )

    with caplog.at_level("WARNING", logger="annexkit.http"):
        # Must not raise.
        exporter.export(_span())

    assert any("AnnexKit HTTP export failed" in r.message for r in caplog.records)


def test_collector_url_trailing_slash_is_normalised() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        return httpx.Response(202)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    exporter = HttpExporter(
        api_key="k",
        collector_url="https://example.test///",
        client=client,
    )
    exporter.export(_span())
    assert seen["url"] == "https://example.test/api/v1/spans"
