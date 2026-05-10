"""CUORE — the deterministic AI Act risk-tier classifier.

Inputs: a flat dict of `{question_id: bool}` plus a GPAI flag.
Outputs: a `Verdict` with the tier and the list of triggered rules.

Rules, in strict precedence order:
  1. Any prohibited-practice question answered `true` → `unacceptable`.
  2. Any Annex III use-case question answered `true` → `high`.
  3. Any transparency trigger answered `true` → `limited`.
  4. Otherwise → `minimal`.

The engine NEVER declassifies: once a higher tier triggers, the final tier
is that. LLMs can advise on how to answer the questions (future work),
they cannot change the verdict.

All reasoning rides in the `Verdict.reasons` list. A verdict with an empty
`reasons` list is always `minimal` — that is an invariant the callers can
rely on.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.services.annex import ANNEX, Rule

RiskTier = Literal["unacceptable", "high", "limited", "minimal"]
RuleType = Literal["prohibited", "high_risk", "transparency"]


@dataclass(frozen=True)
class ReasonEntry:
    """One triggered rule that contributed to the verdict.

    Mirrors `schemas.classification.ReasoningEntry` but stays a pure
    Python dataclass so the engine has zero dependency on Pydantic or the
    ORM. Tests assert on these directly.
    """

    rule_id: str
    rule_type: RuleType
    article: str
    name_it: str
    name_en: str


@dataclass(frozen=True)
class Verdict:
    """Full output of a classification run."""

    tier: RiskTier
    is_gpai: bool
    rules_version: str
    reasons: tuple[ReasonEntry, ...]

    def to_reasoning_dicts(self) -> list[dict[str, str]]:
        """JSON-ready form, ready to store in `classifications.reasoning`."""
        return [
            {
                "rule_id": r.rule_id,
                "rule_type": r.rule_type,
                "article": r.article,
                "name_it": r.name_it,
                "name_en": r.name_en,
            }
            for r in self.reasons
        ]


def _reason_from_rule(rule: Rule, rule_type: RuleType) -> ReasonEntry:
    return ReasonEntry(
        rule_id=rule.id,
        rule_type=rule_type,
        article=rule.article,
        name_it=rule.name_it,
        name_en=rule.name_en,
    )


def classify(answers: dict[str, bool], is_gpai: bool = False) -> Verdict:
    """Run the rule ladder and return a frozen Verdict.

    `answers` missing keys are treated as `False`. Unknown keys are ignored.
    The function is pure — same input, same output, always.
    """

    # -- Step 1: prohibited --------------------------------------------------
    # If ANY prohibited practice question is true → unacceptable. We collect
    # ALL triggered prohibited rules so the user sees every violation, not
    # just the first one.
    prohibited_hits = tuple(
        _reason_from_rule(rule, "prohibited")
        for rule in ANNEX.prohibited_practices
        if answers.get(rule.id) is True
    )
    if prohibited_hits:
        return Verdict(
            tier="unacceptable",
            is_gpai=is_gpai,
            rules_version=ANNEX.version,
            reasons=prohibited_hits,
        )

    # -- Step 2: high-risk (Annex III) --------------------------------------
    # High-risk triggers at the use-case level, not the category level. A
    # system can sit in "Education" without being high-risk (say, a tutoring
    # chatbot that neither admits nor evaluates). Report the *category* of
    # each triggered use case — it's the shape regulators and auditors think
    # in, not the micro-question id.
    #
    # Built as a tuple comprehension (not a list-then-cast) so the result is
    # immutable from construction: nothing in this function can mutate it
    # before it leaves on a Verdict, and the type system enforces it.
    high_risk_hits = tuple(
        ReasonEntry(
            rule_id=category.id,
            rule_type="high_risk",
            article=category.annex_ref,
            name_it=category.name_it,
            name_en=category.name_en,
        )
        for category in ANNEX.high_risk_categories
        if any(answers.get(uc.id) is True for uc in category.use_cases)
    )
    if high_risk_hits:
        return Verdict(
            tier="high",
            is_gpai=is_gpai,
            rules_version=ANNEX.version,
            reasons=high_risk_hits,
        )

    # -- Step 3: transparency (Art. 50) -------------------------------------
    transparency_hits = tuple(
        _reason_from_rule(rule, "transparency")
        for rule in ANNEX.transparency_triggers
        if answers.get(rule.id) is True
    )
    if transparency_hits:
        return Verdict(
            tier="limited",
            is_gpai=is_gpai,
            rules_version=ANNEX.version,
            reasons=transparency_hits,
        )

    # -- Step 4: default ----------------------------------------------------
    return Verdict(
        tier="minimal",
        is_gpai=is_gpai,
        rules_version=ANNEX.version,
        reasons=(),
    )
