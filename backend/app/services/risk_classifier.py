"""Wrapper around :mod:`app.services.risk_engine` for AnnexKit's wire
format (Annex III categories declared directly, rather than via
question/answer pairs).

The underlying engine is verbatim Konformia code: deterministic, never
declassifies. This module's only job is to translate the
``ai_systems`` row into the engine's input dict.

The engine's contract:
    classify(answers: dict[question_id, bool], is_gpai: bool) -> Verdict

For AnnexKit we receive::

    annex_iii_categories=["credit_scoring"]

…and need to translate it into::

    {<each use_case under credit_scoring>: True}

then call :func:`classify`. The same translation happens for prohibited
practices and transparency triggers (those are already at rule
granularity, so the mapping is direct).
"""

from __future__ import annotations

from collections.abc import Sequence

from app.services.annex import ANNEX
from app.services.risk_engine import Verdict, classify


class UnknownAnnexIIICategoryError(ValueError):
    """Raised when a declaration cites an Annex III category we don't recognise."""


class UnknownProhibitedRuleError(ValueError):
    """Raised when a declaration cites a prohibited-practice rule we don't recognise."""


class UnknownTransparencyTriggerError(ValueError):
    """Raised when a declaration cites a transparency trigger we don't recognise."""


def known_annex_iii_category_ids() -> set[str]:
    return {c.id for c in ANNEX.high_risk_categories}


def known_prohibited_rule_ids() -> set[str]:
    return {r.id for r in ANNEX.prohibited_practices}


def known_transparency_trigger_ids() -> set[str]:
    return {r.id for r in ANNEX.transparency_triggers}


def classify_declaration(
    *,
    annex_iii_categories: Sequence[str] = (),
    prohibited_practices: Sequence[str] = (),
    transparency_triggers: Sequence[str] = (),
    is_gpai: bool = False,
) -> Verdict:
    """Classify an AI system from declarative inputs.

    Validates that every cited id is one the rule engine recognises;
    raises :class:`UnknownAnnexIIICategoryError` /
    :class:`UnknownProhibitedRuleError` /
    :class:`UnknownTransparencyTriggerError` otherwise. The route layer
    turns these into 422s.

    Translation:
      * Each declared Annex III category → all its use_cases set to True.
      * Each prohibited rule id → that id set to True.
      * Each transparency trigger id → that id set to True.
    """
    valid_categories = known_annex_iii_category_ids()
    valid_prohibited = known_prohibited_rule_ids()
    valid_transparency = known_transparency_trigger_ids()

    bad = [c for c in annex_iii_categories if c not in valid_categories]
    if bad:
        raise UnknownAnnexIIICategoryError(
            f"Unknown Annex III category id(s): {bad}. "
            f"Allowed: {sorted(valid_categories)}"
        )
    bad = [r for r in prohibited_practices if r not in valid_prohibited]
    if bad:
        raise UnknownProhibitedRuleError(
            f"Unknown prohibited-practice id(s): {bad}. "
            f"Allowed: {sorted(valid_prohibited)}"
        )
    bad = [r for r in transparency_triggers if r not in valid_transparency]
    if bad:
        raise UnknownTransparencyTriggerError(
            f"Unknown transparency-trigger id(s): {bad}. "
            f"Allowed: {sorted(valid_transparency)}"
        )

    answers: dict[str, bool] = {}

    # Prohibited rules — direct id → True.
    for rule_id in prohibited_practices:
        answers[rule_id] = True

    # Transparency triggers — direct id → True.
    for rule_id in transparency_triggers:
        answers[rule_id] = True

    # Annex III categories — expand each category to its use_cases.
    by_id = {c.id: c for c in ANNEX.high_risk_categories}
    for cat_id in annex_iii_categories:
        category = by_id[cat_id]
        for use_case in category.use_cases:
            answers[use_case.id] = True

    return classify(answers, is_gpai=is_gpai)
