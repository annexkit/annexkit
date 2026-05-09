"""Public API surface check.

Replaces the v0.0.1 placeholder tests once the SDK is real (v0.1.0).
"""

from __future__ import annotations

import annexkit


def test_version_exposed() -> None:
    assert annexkit.__version__ == "0.1.0"


def test_public_api_surface() -> None:
    expected = {
        "__version__",
        "track",
        "session",
        "configure",
        "flush",
        "shutdown",
        "Span",
        "Source",
        "SpanHandle",
    }
    assert set(annexkit.__all__) == expected
    for name in expected:
        assert hasattr(annexkit, name), f"missing {name!r} on annexkit"
