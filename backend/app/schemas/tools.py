"""Pydantic schemas for the public free-tools API.

These endpoints sit under ``/api/v1/tools/*``, have no Bearer auth,
and are rate-limited per IP. They are meant for marketing-driven
self-serve traffic from ``annexkit.dev/tools/*`` pages.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.ai_system import ProviderInfo

# Pragmatic email regex — RFC 5322 strict is impractical; this catches
# 99% of typos without pulling email-validator as a hard dep.
_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$",
)


class AnnexIVGeneratorRequest(BaseModel):
    """Body of ``POST /api/v1/tools/annex-iv-generator``.

    The form on annexkit.dev/tools/annex-iv-generator collects:
      1. Purpose (free-form description)
      2. Annex III categories (multi-select from 8 categories)
      3. Article 5 prohibited practices (multi-select from 8)
      4. Article 50 transparency triggers (multi-select from 4)
      5. GPAI flag
      6. Provider info (legal_name, address, country, contact_email, ...)
      7. Email for lead capture

    The classifier runs against (2)+(3)+(4) deterministically; the PDF
    is generated in-memory and returned as the response body. The lead
    is persisted to the ``leads`` table.
    """

    model_config = ConfigDict(extra="forbid")

    purpose: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description=(
            "Free-form description of what the AI system does. Renders as Annex "
            "IV §1.1 'Intended purpose'."
        ),
    )
    annex_iii_categories: list[str] = Field(
        default_factory=list,
        description="Ids from annex_iii.json 'high_risk_categories'.",
    )
    prohibited_practices: list[str] = Field(
        default_factory=list,
        description="Ids from annex_iii.json 'prohibited_practices'.",
    )
    transparency_triggers: list[str] = Field(
        default_factory=list,
        description="Ids from annex_iii.json 'transparency_triggers'.",
    )
    is_gpai: bool = False
    provider_info: ProviderInfo = Field(default_factory=ProviderInfo)

    # Required — see B.1 design decision (email is the marketing capture).
    email: str = Field(
        ...,
        max_length=255,
        description=(
            "Email of the person generating the PDF. Stored in the ``leads`` "
            "table for follow-up; not used for auth."
        ),
    )

    @field_validator("email")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        v = v.strip()
        if not _EMAIL_RE.match(v):
            raise ValueError(
                f"{v!r} does not look like a valid email address."
            )
        return v.lower()
