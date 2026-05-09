"""Singleton loader for `app/data/annex_iii.json`.

The file is parsed once at import time and exposed as an immutable
`AnnexRules` object. Re-reading JSON on every request would be silly —
the file is ~8KB and never changes between deploys.

If the file is ever edited at runtime (dev only), restart the process.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# The JSON lives next to this file's grandparent: app/data/annex_iii.json.
_ANNEX_PATH = Path(__file__).resolve().parents[1] / "data" / "annex_iii.json"


@dataclass(frozen=True)
class Rule:
    """One prohibited practice, transparency trigger, or GPAI marker."""

    id: str
    article: str
    name_it: str
    name_en: str
    description_it: str
    question_it: str


@dataclass(frozen=True)
class HighRiskUseCase:
    id: str
    question_it: str


@dataclass(frozen=True)
class HighRiskCategory:
    id: str
    annex_ref: str
    name_it: str
    name_en: str
    description_it: str
    use_cases: tuple[HighRiskUseCase, ...]


@dataclass(frozen=True)
class AnnexRules:
    """Parsed, immutable view of `annex_iii.json`."""

    version: str
    regulation: str
    prohibited_practices: tuple[Rule, ...]
    high_risk_categories: tuple[HighRiskCategory, ...]
    transparency_triggers: tuple[Rule, ...]
    gpai: Rule
    # Raw dict kept for endpoints that want to return the tree as-is.
    raw: dict[str, Any]


def _parse_rule(d: dict[str, Any]) -> Rule:
    # Single place where dict -> Rule translation happens. All Rule sources
    # (prohibited / transparency / gpai) share the same shape, so we reuse.
    return Rule(
        id=d["id"],
        article=d.get("article", ""),
        name_it=d["name_it"],
        name_en=d["name_en"],
        description_it=d.get("description_it", ""),
        question_it=d["question_it"],
    )


def _load() -> AnnexRules:
    with _ANNEX_PATH.open(encoding="utf-8") as f:
        raw = json.load(f)

    categories = tuple(
        HighRiskCategory(
            id=c["id"],
            annex_ref=c["annex_ref"],
            name_it=c["name_it"],
            name_en=c["name_en"],
            description_it=c["description_it"],
            use_cases=tuple(
                HighRiskUseCase(id=u["id"], question_it=u["question_it"])
                for u in c["use_cases"]
            ),
        )
        for c in raw["high_risk_categories"]
    )

    return AnnexRules(
        version=raw["version"],
        regulation=raw["regulation"],
        prohibited_practices=tuple(_parse_rule(p) for p in raw["prohibited_practices"]),
        high_risk_categories=categories,
        transparency_triggers=tuple(
            _parse_rule(t) for t in raw["transparency_triggers"]
        ),
        gpai=_parse_rule(raw["gpai"]),
        raw=raw,
    )


# One global instance. Import this, never re-parse.
ANNEX: AnnexRules = _load()
