"""Static-analysis guard: the risk engine must remain LLM-free.

The Risk Engine decides whether an AI system is unacceptable / high /
limited / minimal under the EU AI Act. The answer it returns is shown
to regulators as a compliance artefact, which means:

  * Two identical inputs must always produce the same classification.
  * Two customers with the same Annex III profile must get the same
    classification.
  * An auditor must be able to trace every decision back to a rule in
    `app/data/annex_iii.json`.

Those properties all break the moment the engine starts calling an LLM.
So we pin the property in a test: the module must not import the
Mistral SDK, the Anthropic SDK, or any of our own LLM wrappers. This
catches a well-intentioned refactor that routes ambiguous cases
through `mistral_client` before it lands on master.

The test is a string scan rather than a runtime import probe because:

  * A runtime check would need to *import* `risk_engine`, whose tests
    already cover behaviour.
  * We specifically want to fail on the *presence* of the import
    statement, even if it sits behind a `TYPE_CHECKING` guard — we
    don't want reviewers to have to reason about "is this conditional
    ever entered".
"""

from __future__ import annotations

from pathlib import Path

# These substrings are what a reviewer would grep for if they suspected
# an LLM call snuck into the engine. Keep the list explicit — a
# `re.search(r"mistral|anthropic|openai")` would catch comments too,
# which we don't want (the module may legitimately document *why*
# LLMs are forbidden).
_FORBIDDEN_IMPORT_PATTERNS = (
    "from mistralai",
    "import mistralai",
    "from anthropic",
    "import anthropic",
    "from openai",
    "import openai",
    # The engine must never route through the LLM adapter (it would break
    # determinism). In the monorepo the adapter lives under
    # konformia_core.adapters — forbid any reach into it.
    "from konformia_core.adapters",
    "import konformia_core.adapters",
)

# Resolve the path relative to this file, not the CWD — pytest can be
# invoked from anywhere and we don't want the test to flip on that.
_RISK_ENGINE_PATH = (
    Path(__file__).resolve().parent.parent
    / "konformia_core"
    / "classifier"
    / "engine.py"
)


def test_risk_engine_has_no_llm_imports() -> None:
    """Fail if the risk engine source mentions any LLM import path."""
    # Sanity: the file should exist. If it doesn't, the test would
    # trivially pass — which is worse than failing.
    assert _RISK_ENGINE_PATH.exists(), (
        f"risk_engine.py not found at {_RISK_ENGINE_PATH}"
    )

    source = _RISK_ENGINE_PATH.read_text(encoding="utf-8")
    # Check line-by-line so we can report *which* line offended — when
    # this test fails, the reviewer reads the assertion message and
    # knows exactly what to delete.
    offenders: list[tuple[int, str]] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        stripped = line.lstrip()
        # Skip comment lines — the module docstring is allowed to
        # mention the forbidden names when explaining why they're
        # forbidden.
        if stripped.startswith("#"):
            continue
        for pattern in _FORBIDDEN_IMPORT_PATTERNS:
            if pattern in stripped:
                offenders.append((lineno, stripped))
                break

    assert not offenders, (
        "risk_engine.py must be LLM-free (deterministic classification). "
        f"Offending lines: {offenders}"
    )
