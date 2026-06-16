"""Canonical Pydantic request/response schemas — the shared CONTRACTS.

Per the data-layer decision (see MIGRATION.md), core owns the contracts, not the
persistence: both apps map their own ORM to/from these schemas. core itself
stays free of SQLAlchemy.

NOTE: the AnnexKit SDK span schema (sdk/annexkit/schema.py) is a DELIBERATE copy
of the Evidence schema, not an import — it lets the SDK and collector version
independently. Keep them in sync with a contract TEST, never an import.
"""

from __future__ import annotations

from konformia_core.schemas.ai_system import (
    AISystemBase,
    AISystemCreate,
    AISystemRead,
    AISystemUpdate,
    DeploymentStatus,
    OrgRole,
)
from konformia_core.schemas.classification import (
    ClassificationCreate,
    ClassificationRead,
    ReasoningEntry,
    RiskTier,
)
from konformia_core.schemas.document import (
    DeclarationOfConformityInput,
    DocumentCreate,
    DocumentRead,
    DocumentType,
    FundamentalRightsImpactAssessmentInput,
    InstructionsForUseInput,
    PostMarketMonitoringPlanInput,
    RiskManagementSystemInput,
    RiskRegisterRow,
    SupplierClausesInput,
)
from konformia_core.schemas.evidence import (
    IngestResponse,
    IngestSource,
    IngestSpan,
)

__all__ = [  # noqa: RUF022 - grouped by domain on purpose, clearer than alphabetical
    # System (registry record)
    "AISystemBase",
    "AISystemCreate",
    "AISystemRead",
    "AISystemUpdate",
    "DeploymentStatus",
    "OrgRole",
    # Classification (verdict)
    "ClassificationCreate",
    "ClassificationRead",
    "ReasoningEntry",
    "RiskTier",
    # Documents / artifact inputs (the article-derived structures)
    "DocumentType",
    "DocumentCreate",
    "DocumentRead",
    "DeclarationOfConformityInput",
    "FundamentalRightsImpactAssessmentInput",
    "PostMarketMonitoringPlanInput",
    "RiskManagementSystemInput",
    "RiskRegisterRow",
    "SupplierClausesInput",
    "InstructionsForUseInput",
    # Evidence (the runtime span the collector ingests; the SDK mirrors it)
    "IngestSpan",
    "IngestSource",
    "IngestResponse",
]
