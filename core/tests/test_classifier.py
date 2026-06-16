"""Benchmark tests for the deterministic CUORE risk engine.

The engine is pure (no DB, no network). These tests feed a dict of
answers in, assert the verdict out, and — crucially — assert WHICH rules
fired. Reasoning assertions are what protect us from silent regressions
where the tier is right but the citation is wrong.

30+ scenarios, grouped by expected tier. Add new scenarios here when you
change or extend `annex_iii.json`.
"""

from __future__ import annotations

import pytest

from konformia_core.classifier import ANNEX
from konformia_core.classifier import engine as risk_engine


# ---------------------------------------------------------------------------
# Sanity checks on the JSON itself.
# ---------------------------------------------------------------------------
def test_annex_loads_with_expected_top_level_shape() -> None:
    assert ANNEX.version
    assert len(ANNEX.prohibited_practices) >= 8  # Art. 5 has 8 practices
    assert len(ANNEX.high_risk_categories) == 8  # Annex III has 8 domains
    assert len(ANNEX.transparency_triggers) >= 3  # Art. 50 has 4, but be lenient
    assert ANNEX.gpai.id == "gpai_marker"


def test_every_rule_id_is_globally_unique() -> None:
    """Two rules sharing an id would make the engine unable to distinguish them."""
    ids: list[str] = []
    ids.extend(r.id for r in ANNEX.prohibited_practices)
    ids.extend(r.id for r in ANNEX.transparency_triggers)
    ids.append(ANNEX.gpai.id)
    for c in ANNEX.high_risk_categories:
        ids.append(c.id)
        ids.extend(u.id for u in c.use_cases)
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# UNACCEPTABLE — prohibited practices (Art. 5)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "triggered_ids,scenario",
    [
        (["art5_social_scoring"], "public social scoring"),
        (["art5_subliminal"], "subliminal manipulation ad engine"),
        (["art5_vulnerabilities"], "loan shark exploiting elderly"),
        (["art5_crime_prediction"], "profiling-only crime predictor"),
        (["art5_facial_scraping"], "Clearview-style scraper"),
        (["art5_emotion_workplace"], "emotion tracker in call center"),
        (["art5_biometric_categorisation"], "face-based ethnicity inference"),
        (["art5_realtime_rbi"], "real-time street CCTV face ID for police"),
    ],
)
def test_prohibited_practices_yield_unacceptable(
    triggered_ids: list[str], scenario: str
) -> None:
    answers = {rule_id: True for rule_id in triggered_ids}
    verdict = risk_engine.classify(answers)

    assert verdict.tier == "unacceptable", f"[{scenario}] expected unacceptable"
    assert {r.rule_id for r in verdict.reasons} == set(triggered_ids)
    # Every reported reason must be of the prohibited type.
    assert all(r.rule_type == "prohibited" for r in verdict.reasons)


def test_multiple_prohibited_triggers_all_reported() -> None:
    """When two prohibited practices fire, the user must see BOTH, not one."""
    answers = {
        "art5_social_scoring": True,
        "art5_emotion_workplace": True,
    }
    verdict = risk_engine.classify(answers)
    assert verdict.tier == "unacceptable"
    triggered = {r.rule_id for r in verdict.reasons}
    assert triggered == {"art5_social_scoring", "art5_emotion_workplace"}


def test_prohibited_beats_high_risk() -> None:
    """Prohibited overrides high-risk — a recruiting tool doing social
    scoring is still prohibited."""
    answers = {
        "art5_social_scoring": True,
        "annex3_4_recruitment": True,
    }
    verdict = risk_engine.classify(answers)
    assert verdict.tier == "unacceptable"
    assert {r.rule_type for r in verdict.reasons} == {"prohibited"}


def test_prohibited_beats_transparency() -> None:
    answers = {
        "art5_facial_scraping": True,
        "art50_chat_interaction": True,
    }
    verdict = risk_engine.classify(answers)
    assert verdict.tier == "unacceptable"


# ---------------------------------------------------------------------------
# HIGH — Annex III categories
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "use_case_id,expected_category,scenario",
    [
        ("annex3_1_remote_id", "annex3_1_biometrics", "post-event face ID"),
        ("annex3_1_emotion", "annex3_1_biometrics", "clinical emotion recognition"),
        ("annex3_2_safety", "annex3_2_critical_infra", "power-grid safety controller"),
        ("annex3_3_admission", "annex3_3_education", "university admissions filter"),
        ("annex3_3_evaluation", "annex3_3_education", "automated grading"),
        ("annex3_3_exam_monitor", "annex3_3_education", "online-exam proctoring"),
        ("annex3_4_recruitment", "annex3_4_employment", "CV screener"),
        ("annex3_4_promotion", "annex3_4_employment", "layoff recommender"),
        ("annex3_4_monitoring", "annex3_4_employment", "gig-worker tracker"),
        ("annex3_5_credit", "annex3_5_essential_services", "loan-eligibility score"),
        ("annex3_5_insurance", "annex3_5_essential_services", "health-insurance pricer"),
        ("annex3_5_public_benefits", "annex3_5_essential_services", "welfare eligibility"),
        ("annex3_5_emergency", "annex3_5_essential_services", "911 dispatch priority"),
        ("annex3_6_risk_assessment", "annex3_6_law_enforcement", "victim risk model"),
        ("annex3_6_predictive_policing", "annex3_6_law_enforcement", "recidivism profiler"),
        ("annex3_7_applications", "annex3_7_migration", "visa decision assistant"),
        ("annex3_8_judicial", "annex3_8_justice", "judicial research tool"),
        ("annex3_8_elections", "annex3_8_justice", "election-influence engine"),
    ],
)
def test_high_risk_use_cases_yield_high(
    use_case_id: str, expected_category: str, scenario: str
) -> None:
    verdict = risk_engine.classify({use_case_id: True})
    assert verdict.tier == "high", f"[{scenario}] expected high"
    # The reported reason is the CATEGORY, not the micro use-case — that's
    # the shape regulators/auditors think in.
    reason_ids = {r.rule_id for r in verdict.reasons}
    assert expected_category in reason_ids


def test_multiple_high_risk_categories_reported() -> None:
    """A system straddling recruiting + credit triggers both categories."""
    answers = {
        "annex3_4_recruitment": True,
        "annex3_5_credit": True,
    }
    verdict = risk_engine.classify(answers)
    assert verdict.tier == "high"
    reasons = {r.rule_id for r in verdict.reasons}
    assert reasons == {"annex3_4_employment", "annex3_5_essential_services"}


def test_high_risk_beats_transparency() -> None:
    """A CV-screening chatbot is high-risk, not merely transparency-limited."""
    answers = {
        "annex3_4_recruitment": True,
        "art50_chat_interaction": True,
    }
    verdict = risk_engine.classify(answers)
    assert verdict.tier == "high"
    assert {r.rule_type for r in verdict.reasons} == {"high_risk"}


# ---------------------------------------------------------------------------
# LIMITED — transparency obligations (Art. 50)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "trigger_id,scenario",
    [
        ("art50_chat_interaction", "customer service chatbot"),
        ("art50_synthetic_content", "AI article generator"),
        ("art50_deepfake", "deepfake advertising tool"),
        ("art50_emotion_biometric", "permitted emotion-recognition product"),
    ],
)
def test_transparency_triggers_yield_limited(
    trigger_id: str, scenario: str
) -> None:
    verdict = risk_engine.classify({trigger_id: True})
    assert verdict.tier == "limited", f"[{scenario}] expected limited"
    assert verdict.reasons[0].rule_id == trigger_id
    assert verdict.reasons[0].rule_type == "transparency"


# ---------------------------------------------------------------------------
# MINIMAL — the default
# ---------------------------------------------------------------------------
def test_no_answers_yields_minimal() -> None:
    verdict = risk_engine.classify({})
    assert verdict.tier == "minimal"
    assert verdict.reasons == ()


def test_all_false_answers_yield_minimal() -> None:
    answers = {rule.id: False for rule in ANNEX.prohibited_practices}
    for cat in ANNEX.high_risk_categories:
        for uc in cat.use_cases:
            answers[uc.id] = False
    for rule in ANNEX.transparency_triggers:
        answers[rule.id] = False

    verdict = risk_engine.classify(answers)
    assert verdict.tier == "minimal"
    assert verdict.reasons == ()


def test_unknown_keys_are_ignored() -> None:
    verdict = risk_engine.classify({"totally_made_up_id": True})
    assert verdict.tier == "minimal"


# ---------------------------------------------------------------------------
# GPAI — orthogonal flag
# ---------------------------------------------------------------------------
def test_gpai_flag_is_preserved_at_every_tier() -> None:
    # Unacceptable + gpai
    v1 = risk_engine.classify({"art5_social_scoring": True}, is_gpai=True)
    assert v1.tier == "unacceptable" and v1.is_gpai is True

    # High + gpai (a GPT-powered CV screener, say)
    v2 = risk_engine.classify({"annex3_4_recruitment": True}, is_gpai=True)
    assert v2.tier == "high" and v2.is_gpai is True

    # Limited + gpai (the canonical case: GPT-powered chatbot)
    v3 = risk_engine.classify({"art50_chat_interaction": True}, is_gpai=True)
    assert v3.tier == "limited" and v3.is_gpai is True

    # Minimal + gpai (a GPT-backed product with no user interaction)
    v4 = risk_engine.classify({}, is_gpai=True)
    assert v4.tier == "minimal" and v4.is_gpai is True


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
def test_classify_is_deterministic() -> None:
    """Same input, same output, always — run 10 times to catch ordering bugs."""
    answers = {
        "annex3_4_recruitment": True,
        "annex3_5_credit": True,
        "art50_chat_interaction": True,
    }
    first = risk_engine.classify(answers)
    for _ in range(10):
        v = risk_engine.classify(answers)
        assert v.tier == first.tier
        assert v.is_gpai == first.is_gpai
        assert tuple(r.rule_id for r in v.reasons) == tuple(
            r.rule_id for r in first.reasons
        )


def test_reasoning_is_serialisable() -> None:
    """The verdict must round-trip through the `to_reasoning_dicts()` form
    used for DB persistence."""
    verdict = risk_engine.classify({"annex3_4_recruitment": True})
    dicts = verdict.to_reasoning_dicts()
    assert isinstance(dicts, list)
    assert all(set(d.keys()) == {"rule_id", "rule_type", "article", "name_it", "name_en"} for d in dicts)
