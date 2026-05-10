"""Public API surface check.

Replaces the v0.0.1 placeholder tests once the SDK is real (v0.1.0).
"""

from __future__ import annotations

import re

import annexkit


def test_version_exposed() -> None:
    # Don't pin a specific version string — `_state.py` reads from the
    # installed package metadata, so the answer follows `pyproject.toml`
    # automatically. We only check that what comes out *looks like*
    # something a release would ship: SemVer-ish, optionally with a
    # local-version segment for the source-tree fallback.
    assert re.match(
        r"^\d+\.\d+\.\d+(?:[+-][0-9A-Za-z.-]+)?$",
        annexkit.__version__,
    ), f"unexpected __version__: {annexkit.__version__!r}"


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
