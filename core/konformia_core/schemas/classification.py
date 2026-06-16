"""Pydantic schemas for Classification.

We expose three shapes:
  - `ClassificationCreate`: input to `POST /systems/{id}/classifications`.
    Just the answers; the server decides the tier.
  - `ClassificationRead`: the full record as returned by the API.
  - `ReasoningEntry`: typed view of a single row inside `reasoning[]` —
    kept separate so the frontend can render it safely.

The questionnaire structure itself (the questions to ask) is served by a
different schema (see `schemas/questionnaire.py`).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from konformia_core.classifier import VALID_RISK_TIERS, RiskTier


class ReasoningEntry(BaseModel):
    """One triggered rule explaining the classification verdict."""

    rule_id: str
    rule_type: Literal["prohibited", "high_risk", "transparency"]
    article: str
    name_it: str
    name_en: str


class ClassificationCreate(BaseModel):
    """What the frontend sends to classify a system.

    `answers` is a flat {question_id: bool}. Every relevant id is listed in
    `annex_iii.json`. Extra ids are ignored by the engine; missing ids are
    treated as `false`. `is_gpai` is a separate flag because it's orthogonal
    to the risk tier.
    """

    model_config = ConfigDict(extra="forbid")

    answers: dict[str, bool] = Field(default_factory=dict)
    is_gpai: bool = False


class ClassificationRead(BaseModel):
    """What the API returns for a classification record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ai_system_id: uuid.UUID
    org_id: uuid.UUID
    tier: RiskTier
    is_gpai: bool
    rules_version: str
    answers: dict[str, bool]
    reasoning: list[ReasoningEntry]
    created_at: datetime
    created_by: uuid.UUID | None


# Safety net: if VALID_RISK_TIERS ever drifts from the Literal above, fail
# loudly at import time rather than at runtime on a specific classification.
assert set(VALID_RISK_TIERS) == {"unacceptable", "high", "limited", "minimal"}
