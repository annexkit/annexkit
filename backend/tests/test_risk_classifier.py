"""Risk classifier wrapper contract tests.

The wrapper translates AnnexKit's declarative wire format
(Annex III category ids, prohibited rule ids, transparency trigger ids)
into the underlying engine's question→answer dict, then calls
:func:`app.services.risk_engine.classify`.

The tests pin two contracts:
  * Translation: known ids resolve to correct verdicts.
  * Validation: unknown ids raise typed exceptions the route layer can
    turn into 422s.

Tier precedence is a property of the underlying engine — these tests
just confirm the wrapper preserves it (prohibited > high > limited >
minimal, never declassified).
"""

from __future__ import annotations

import pytest

from app.services.risk_classifier import (
    UnknownAnnexIIICategoryError,
    UnknownProhibitedRuleError,
    UnknownTransparencyTriggerError,
    classify_declaration,
)


def test_minimal_when_nothing_declared() -> None:
    v = classify_declaration()
    assert v.tier == "minimal"
    assert v.is_gpai is False
    assert v.reasons == ()


def test_gpai_flag_echoed_without_changing_tier() -> None:
    v = classify_declaration(is_gpai=True)
    assert v.tier == "minimal"
    assert v.is_gpai is True


def test_high_when_annex_iii_category_declared() -> None:
    # Employment / workers management is a real Annex III category.
    v = classify_declaration(annex_iii_categories=["annex3_4_employment"])
    assert v.tier == "high"
    assert any(r.rule_id == "annex3_4_employment" for r in v.reasons)


def test_unacceptable_when_prohibited_practice_declared() -> None:
    v = classify_declaration(prohibited_practices=["art5_social_scoring"])
    assert v.tier == "unacceptable"
    assert any(r.rule_id == "art5_social_scoring" for r in v.reasons)


def test_limited_when_transparency_trigger_declared() -> None:
    v = classify_declaration(transparency_triggers=["art50_chat_interaction"])
    assert v.tier == "limited"


def test_prohibited_dominates_high() -> None:
    """Prohibited + high-risk both declared → still unacceptable."""
    v = classify_declaration(
        prohibited_practices=["art5_social_scoring"],
        annex_iii_categories=["annex3_4_employment"],
    )
    assert v.tier == "unacceptable"


def test_high_dominates_limited() -> None:
    v = classify_declaration(
        annex_iii_categories=["annex3_4_employment"],
        transparency_triggers=["art50_chat_interaction"],
    )
    assert v.tier == "high"


def test_unknown_category_raises_typed_error() -> None:
    with pytest.raises(UnknownAnnexIIICategoryError):
        classify_declaration(annex_iii_categories=["bogus_category"])


def test_unknown_prohibited_raises_typed_error() -> None:
    with pytest.raises(UnknownProhibitedRuleError):
        classify_declaration(prohibited_practices=["art5_bogus"])


def test_unknown_transparency_raises_typed_error() -> None:
    with pytest.raises(UnknownTransparencyTriggerError):
        classify_declaration(transparency_triggers=["art50_bogus"])
