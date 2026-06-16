"""Contract test: the AnnexKit SDK Span schema is a DELIBERATE copy of core's
Evidence (``IngestSpan``).

The SDK (``sdk/annexkit/schema.py``) and the collector (``core`` Evidence) version
independently and are never imported into each other — so THIS test is the only
guard against silent drift:

  * If the SDK adds a field the collector's ``IngestSpan`` doesn't accept, the
    collector (``extra="forbid"``) rejects real spans at ingest.
  * If the collector adds a required field the SDK doesn't send, older SDKs break.

Either way drift = a broken evidence pipeline. Keep the two field-compatible;
when you change one, change the other in the same PR.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from konformia_core.schemas.evidence import IngestSource, IngestSpan


def _load_sdk_schema():
    # The SDK is a separate package, not installed in core's env. Its schema
    # module is pure Pydantic + stdlib, so load it standalone by file path.
    path = Path(__file__).resolve().parents[2] / "sdk" / "annexkit" / "schema.py"
    spec = importlib.util.spec_from_file_location("annexkit_sdk_schema", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SDK = _load_sdk_schema()


def test_sdk_span_fields_match_core_evidence() -> None:
    """The SDK ``Span`` and the collector's ``IngestSpan`` must carry the same fields."""
    sdk = set(_SDK.Span.model_fields)
    core = set(IngestSpan.model_fields)
    assert sdk == core, (
        "SDK Span and core IngestSpan drifted — "
        f"SDK-only: {sorted(sdk - core)} | collector-only: {sorted(core - sdk)}. "
        "Update sdk/annexkit/schema.py and core/schemas/evidence.py together."
    )


def test_sdk_source_fields_match_core() -> None:
    """The retrieval-source sub-model must match too."""
    sdk = set(_SDK.Source.model_fields)
    core = set(IngestSource.model_fields)
    assert sdk == core, (
        f"SDK Source / core IngestSource drifted: {sorted(sdk ^ core)}"
    )
