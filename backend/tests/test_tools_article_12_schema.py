"""Contract tests for ``/api/v1/tools/article-12-schema/v1.json``.

Two flavours: vanilla (Pydantic export) + annotated (with
``x-aiact-clause`` per property). The contract that downstream
consumers (OTel adapters, CI validators) depend on:

  * Stable URL versioning (`v1.json` doesn't change shape between
    SDK versions in the v0.1.x line)
  * Every required ``IngestSpan`` field appears in `properties`
  * Annotated variant has ``x-aiact-clause`` on every field
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.schemas.span import IngestSpan


@pytest.mark.asyncio
async def test_vanilla_schema_has_all_ingest_span_fields(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/tools/article-12-schema/v1.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert schema["x-version"] == "1.0.0"
    assert "AnnexKit Span" in schema["title"]

    # Every IngestSpan field should appear in the schema.
    expected = set(IngestSpan.model_fields.keys())
    got = set(schema["properties"].keys())
    missing = expected - got
    assert not missing, f"schema is missing fields from IngestSpan: {missing}"


@pytest.mark.asyncio
async def test_annotated_schema_marks_every_field(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/tools/article-12-schema-annotated/v1.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "annotated" in schema["title"]
    assert schema["x-version"] == "1.0.0"

    # Every property should carry both annotation keys.
    for field_name, prop in schema["properties"].items():
        assert "x-aiact-clause" in prop, f"{field_name} missing x-aiact-clause"
        assert "x-purpose" in prop, f"{field_name} missing x-purpose"


@pytest.mark.asyncio
async def test_annotated_schema_carries_article_12_mapping_for_key_fields(
    client: AsyncClient,
) -> None:
    """Spot-check that the most-load-bearing fields actually mention Article 12."""
    resp = await client.get("/api/v1/tools/article-12-schema-annotated/v1.json")
    schema = resp.json()
    props = schema["properties"]

    # Period of use (start/end + duration) → Article 12 §2(b)
    assert "Article 12" in props["started_at"]["x-aiact-clause"]
    assert "Article 12" in props["ended_at"]["x-aiact-clause"]

    # Input/output evidence (privacy-preserving hashes) → Article 12 §2(c)
    assert "Article 12" in props["input_hash"]["x-aiact-clause"]
    assert "Article 12" in props["output_hash"]["x-aiact-clause"]

    # Adverse event recording
    assert "Article 12" in props["error"]["x-aiact-clause"]


@pytest.mark.asyncio
async def test_vanilla_schema_does_not_carry_annotations(client: AsyncClient) -> None:
    """The vanilla variant is what validators want — no x-aiact-* noise."""
    resp = await client.get("/api/v1/tools/article-12-schema/v1.json")
    schema = resp.json()
    sample_prop = schema["properties"]["trace_id"]
    assert "x-aiact-clause" not in sample_prop
    assert "x-purpose" not in sample_prop


@pytest.mark.asyncio
async def test_rules_json_endpoint_returns_8_8_4(client: AsyncClient) -> None:
    """The /rules.json endpoint (used by the form) returns the rule tree."""
    resp = await client.get("/api/v1/tools/rules.json")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["high_risk_categories"]) == 8
    assert len(data["prohibited_practices"]) == 8
    assert len(data["transparency_triggers"]) == 4
    assert data["gpai"]["id"] == "gpai_marker"
