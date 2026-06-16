"""AI System schemas.

The three-shape convention:
    - AISystemCreate : POST payload  (required fields enforced)
    - AISystemUpdate : PATCH payload (everything optional)
    - AISystemRead   : API response  (all fields populated, safe to expose)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# Mirror the tuple from the ORM model so invalid strings are rejected at
# the edge. Using Literal[] gives us compile-time checks AND runtime 422s.
DeploymentStatus = Literal["planned", "in_use", "decommissioned"]
OrgRole = Literal["provider", "deployer", "both", "distributor", "importer"]


class AISystemBase(BaseModel):
    """Fields shared between create/update/read. Keeps things DRY."""

    name: str = Field(min_length=1, max_length=255)
    vendor: str | None = Field(default=None, max_length=255)
    purpose: str | None = None
    data_processed: str | None = None
    deployment_status: DeploymentStatus | None = None
    org_role: OrgRole | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class AISystemCreate(AISystemBase):
    """POST /api/v1/systems payload."""


class AISystemUpdate(BaseModel):
    """PATCH /api/v1/systems/{id} payload. Everything is optional."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    vendor: str | None = Field(default=None, max_length=255)
    purpose: str | None = None
    data_processed: str | None = None
    deployment_status: DeploymentStatus | None = None
    org_role: OrgRole | None = None
    metadata_json: dict[str, Any] | None = None


class AISystemRead(AISystemBase):
    """Response body. Mirrors the ORM model but omits nothing sensitive."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Batch create — drives the /dashboard/systems/discover wizard.
# ---------------------------------------------------------------------------
# The discovery wizard walks the user through a questionnaire and ends on a
# review screen with N suggested systems. Rather than firing N sequential
# POSTs (slow, hard to handle partial failure cleanly), the client sends one
# batch request. The service pre-filters duplicates by name and returns two
# lists so the UI can say "created 8, skipped 2 because they already exist".

# Hard upper bound on batch size. 50 is well above the number of systems a
# PMI would realistically register in one go; it also keeps a single request
# cheap to validate and cheap to roll back if we ever add a full-transaction
# failure mode.
_BATCH_MAX_SYSTEMS = 50


class AISystemBatchCreate(BaseModel):
    """POST /api/v1/systems/batch payload.

    One request, N systems. Order is preserved in the response so the client
    can line up "created" rows with the original review cards.
    """

    systems: list[AISystemCreate] = Field(
        min_length=1,
        max_length=_BATCH_MAX_SYSTEMS,
        description="1..50 AI systems to create atomically (skip duplicates).",
    )


class AISystemBatchSkipped(BaseModel):
    """One entry in the ``skipped`` list of a batch response.

    Kept as a structured pair rather than a free-form string so the UI can
    localise the reason and group by cause without parsing text.
    """

    name: str
    reason: Literal["duplicate_name"]


class AISystemBatchResult(BaseModel):
    """POST /api/v1/systems/batch response body.

    Partial success is intentional: a wizard that silently refuses the whole
    batch because one name already existed would frustrate users who are
    re-running discovery after adding a couple of systems manually.
    """

    created: list[AISystemRead]
    skipped: list[AISystemBatchSkipped]
