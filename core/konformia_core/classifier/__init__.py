"""Deterministic Annex III risk classifier — the single source of truth.

Public API for the EU AI Act risk-tier engine. Both apps import from here:

    from konformia_core.classifier import classify, Verdict, ANNEX

The engine is rules-driven (``rules/eu/annex_iii.json``) and pure: same input,
same output, always. It NEVER declassifies — LLMs may advise on ambiguous
answers, never override the verdict (a CLAUDE.md non-negotiable).
"""

from __future__ import annotations

from konformia_core.classifier.annex import (
    ANNEX,
    AnnexRules,
    HighRiskCategory,
    HighRiskUseCase,
    Rule,
)
from konformia_core.classifier.engine import (
    VALID_RISK_TIERS,
    ReasonEntry,
    RiskTier,
    RuleType,
    Verdict,
    classify,
)

__all__ = [
    "ANNEX",
    "VALID_RISK_TIERS",
    "AnnexRules",
    "HighRiskCategory",
    "HighRiskUseCase",
    "ReasonEntry",
    "RiskTier",
    "Rule",
    "RuleType",
    "Verdict",
    "classify",
]
