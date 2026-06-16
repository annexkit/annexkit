"""Pydantic schemas for generated compliance documents.

We expose:
  - `DocumentCreate`: minimal input — pick a `document_type` and (for the
    Declaration of Conformity) a structured `doc_input` block carrying
    provider/signatory metadata. The server picks the latest classification
    automatically.
  - `DocumentRead`: metadata returned after generation and in listings.
    The PDF bytes themselves are served by a separate streaming route.

The actual PDF isn't serialised into JSON — it's downloaded via its own
endpoint that returns `application/pdf` with the correct headers.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from konformia_core.schemas.classification import RiskTier

# Forward-compat enum-like Literal. New types live next to the existing
# value; the model layer's VALID_DOCUMENT_TYPES mirrors this exactly.
DocumentType = Literal[
    "annex_iv",
    "declaration_of_conformity",
    "fria",
    "post_market_plan",
    "risk_management_system",
    "supplier_clauses",
    "instructions_for_use",
]


# --- DoC-specific input -----------------------------------------------------
# These fields are echoed verbatim onto the rendered Allegato V certificate.
# They're collected from the user at generation time because they're not
# already on `ai_systems` or `organizations` (the legal address can differ
# from the operational one, the signatory name is human, etc.). We capture
# a snapshot so the certificate stays self-describing even if the org
# updates its profile later.

# A short non-empty string. Trimmed length validation lives in Pydantic.
_NonEmptyStr = Annotated[str, Field(min_length=1, max_length=255)]


class DeclarationOfConformityInput(BaseModel):
    """Provider + signatory metadata for an Allegato V certificate.

    Mirrors the EU AI Act Annex V shape (Art. 47):
      - provider identity (legal name + address + VAT/tax id)
      - identification of the AI system (name + version + identifiers)
      - reference to applicable Union legislation (defaults filled in)
      - harmonised standards / common specifications applied (optional list)
      - notified body involvement (optional — only for systems requiring it)
      - person empowered to sign + place + date

    The date is the server's `now()` at generation time — we don't accept
    it from the client to prevent backdating.
    """

    model_config = ConfigDict(extra="forbid")

    # Provider section ------------------------------------------------------
    provider_legal_name: _NonEmptyStr
    provider_address: _NonEmptyStr
    provider_vat_number: Annotated[str, Field(min_length=1, max_length=64)]

    # System identification (free-form: serial number, internal SKU, etc.).
    # The system's display name and tier already come from the AISystem row.
    system_identifiers: Annotated[str, Field(min_length=1, max_length=255)]

    # Optional: harmonised standards applied (e.g. "ISO/IEC 42001:2023").
    # Empty list = "none claimed" — rendered as a placeholder on the PDF.
    harmonised_standards: list[Annotated[str, Field(min_length=1, max_length=255)]] = (
        Field(default_factory=list)
    )

    # Optional: applicable Union legislation beyond the AI Act itself.
    # Defaults filled in by the renderer when omitted.
    applicable_legislation: list[Annotated[str, Field(min_length=1, max_length=255)]] = (
        Field(default_factory=list)
    )

    # Notified body details — only required when the conformity assessment
    # involved one (high-risk Annex III + certain conformity routes). Both
    # nullable so we don't force the user to fabricate a body when the
    # internal-control route was used.
    notified_body_name: Annotated[str, Field(max_length=255)] | None = None
    notified_body_id: Annotated[str, Field(max_length=64)] | None = None
    notified_body_certificate: Annotated[str, Field(max_length=255)] | None = None

    # Signatory: who signs the declaration.
    signatory_name: _NonEmptyStr
    signatory_role: _NonEmptyStr  # e.g. "Amministratore Delegato"
    place_of_issue: _NonEmptyStr  # e.g. "Milano, Italia"


class FundamentalRightsImpactAssessmentInput(BaseModel):
    """Inputs for a FRIA — Fundamental Rights Impact Assessment.

    Art. 27 of Regulation (EU) 2024/1689 obliges *deployers* of certain
    high-risk AI systems (notably those listed in Annex III paragraphs
    5(b) and 5(c) for public-sector use, plus credit-scoring and
    life/health insurance under 5(b) regardless of sector) to perform an
    impact assessment **before** first putting the system into use. We
    collect the six pieces the article itself enumerates verbatim.

    The form is structurally analogous to the DoC: it ends up rendered
    onto a formal Italian PDF that the deployer's DPO / compliance lead
    files. We don't mark fields beyond a free-text length cap because
    every section is a narrative description, not a checkbox.
    """

    model_config = ConfigDict(extra="forbid")

    # Art. 27(1)(a): description of deployer's processes in which the
    # high-risk AI system will be used, in line with its intended purpose.
    deployment_processes: Annotated[str, Field(min_length=1, max_length=4000)]

    # Art. 27(1)(b): period of time and frequency of intended use.
    deployment_period_and_frequency: Annotated[
        str, Field(min_length=1, max_length=2000)
    ]

    # Art. 27(1)(c): categories of natural persons and groups likely to
    # be affected.
    affected_persons_categories: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 27(1)(d): specific risks of harm likely to impact those
    # categories.
    specific_risks_of_harm: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 27(1)(e): description of human-oversight measures (technical +
    # organisational) the deployer has in place.
    human_oversight_measures: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 27(1)(f): measures to be taken if the risks materialise —
    # internal governance + complaint mechanisms.
    measures_if_risks_materialise: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Compiler / responsible role — not strictly required by Art. 27 but
    # a courtesy field that ends up on the PDF "compiled by" line so the
    # filed assessment names a human accountable for it.
    compiled_by_name: Annotated[str, Field(min_length=1, max_length=255)]
    compiled_by_role: Annotated[str, Field(min_length=1, max_length=255)]


class PostMarketMonitoringPlanInput(BaseModel):
    """Inputs for a post-market monitoring plan (Art. 72).

    Art. 72 of Regulation (EU) 2024/1689 obliges the *provider* of a
    high-risk AI system to draw up — before placing the system on the
    market — a written plan describing how they will systematically
    collect, document, and analyse data on the system's performance
    throughout its lifetime. The Commission will publish a template via
    implementing act (not yet released as of 2026); until then this
    schema captures the substantive sections any reasonable plan must
    include, derived directly from Art. 72(1) and (2) plus Recital 155.

    Each field is a free-text narrative — same shape as the FRIA — so
    the deployer can copy from existing ISO 9001 / ISO 13485 / IEC
    62304 post-market frameworks where they already exist.
    """

    model_config = ConfigDict(extra="forbid")

    # Art. 72(1): a description of the monitoring methodology.
    monitoring_methodology: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Sources of data the provider will draw on (e.g. user feedback,
    # incident logs, performance telemetry, periodic re-evaluation).
    data_sources: Annotated[str, Field(min_length=1, max_length=4000)]

    # Concrete metrics tracked + thresholds that trigger an action.
    # KPIs typical for AI systems: drift, accuracy delta vs. baseline,
    # false-positive rate, calibration error.
    kpis_and_thresholds: Annotated[str, Field(min_length=1, max_length=4000)]

    # How often the plan is reviewed (quarterly, on each model retrain,
    # after every serious incident — Art. 72(1) requires a defined
    # cadence).
    review_cadence: Annotated[str, Field(min_length=1, max_length=2000)]

    # Roles + responsibilities — who owns the plan, who reviews KPIs,
    # who escalates.
    roles_and_responsibilities: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Corrective-action process — the loop from "KPI breached" to
    # "fix shipped + filed". Maps to Art. 20 (corrective actions on
    # non-conforming systems).
    corrective_actions_process: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Compiler / responsible role. Same courtesy field as FRIA; ends up
    # on the PDF "compiled by" line so the filed plan names a human
    # accountable for it.
    compiled_by_name: Annotated[str, Field(min_length=1, max_length=255)]
    compiled_by_role: Annotated[str, Field(min_length=1, max_length=255)]


class RiskRegisterRow(BaseModel):
    """One row of the FMEA-style risk register inside an Art. 9 RMS doc.

    Severity / likelihood are constrained to the standard FMEA 1-5 scale
    so the rendered table stays computable (we draw a heat-map cell per
    row). The mitigation field is a short narrative — the "what we did
    about it" column.
    """

    model_config = ConfigDict(extra="forbid")

    risk_description: Annotated[str, Field(min_length=1, max_length=500)]
    affected_party: Annotated[str, Field(min_length=1, max_length=300)]
    likelihood: Annotated[int, Field(ge=1, le=5)]
    severity: Annotated[int, Field(ge=1, le=5)]
    mitigation: Annotated[str, Field(min_length=1, max_length=1000)]
    residual_risk: Annotated[str, Field(min_length=1, max_length=500)]


class RiskManagementSystemInput(BaseModel):
    """Inputs for an Art. 9 Risk Management System dossier.

    Art. 9 Reg. UE 2024/1689 obliges the *provider* of a high-risk AI
    system to establish, implement, document and maintain a continuous
    iterative risk-management process throughout the system's lifecycle.

    The schema captures both the narrative obligations (methodology,
    test procedures, ongoing review) AND a structured register
    (FMEA-style table) so the document doubles as the actual operational
    artefact, not just a description of it.
    """

    model_config = ConfigDict(extra="forbid")

    # Art. 9(2)(a): identification + analysis of the known and the
    # reasonably foreseeable risks.
    risk_identification_methodology: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 9(2)(b)+(c): risk-mitigation design choices + residual risk
    # acceptance.
    mitigation_design_choices: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 9(2)(d): testing procedures used to verify the system meets
    # the intended purpose with acceptable residual risk.
    testing_procedures: Annotated[str, Field(min_length=1, max_length=4000)]

    # Art. 9(2): the iterative process — when the RMS gets re-run.
    iterative_review_process: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # The structured register itself. Constrained to a max so a single
    # document doesn't blow up the rendering pipeline.
    risk_register: Annotated[list[RiskRegisterRow], Field(max_length=50)] = (
        Field(default_factory=list)
    )

    # Compiler / responsible role.
    compiled_by_name: Annotated[str, Field(min_length=1, max_length=255)]
    compiled_by_role: Annotated[str, Field(min_length=1, max_length=255)]


class SupplierClausesInput(BaseModel):
    """Inputs for the Art. 25 + Art. 26 contractual-clauses template.

    The output is a draft set of clauses the *deployer* (the user)
    attaches to a procurement contract when sourcing a high-risk AI
    system from a third-party *provider*. The clauses bind the provider
    to obligations that flow upstream from the deployer's own AI Act
    compliance:

      * Documentation transfer (Annex IV)
      * Risk management cooperation (Art. 9)
      * Post-market monitoring data sharing (Art. 72)
      * Serious-incident notification (Art. 73)
      * DoC issuance (Art. 47)
      * Cooperation on FRIA (Art. 27)
    """

    model_config = ConfigDict(extra="forbid")

    # Counterparty (the AI provider) details.
    supplier_legal_name: Annotated[str, Field(min_length=1, max_length=255)]
    supplier_address: Annotated[str, Field(min_length=1, max_length=500)]
    supplier_vat_number: Annotated[str, Field(min_length=1, max_length=64)]
    supplier_contact_email: Annotated[str, Field(min_length=1, max_length=255)]

    # Reference of the existing or proposed master contract (PO, MSA, etc.).
    contract_reference: Annotated[str, Field(min_length=1, max_length=255)]

    # Optional bespoke addendum — anything specific to negotiate.
    additional_concerns: Annotated[str, Field(max_length=4000)] | None = None

    # Compiled by — same convention as the other doc types.
    compiled_by_name: Annotated[str, Field(min_length=1, max_length=255)]
    compiled_by_role: Annotated[str, Field(min_length=1, max_length=255)]


class InstructionsForUseInput(BaseModel):
    """Inputs for the Art. 13 "instructions for use" document.

    Art. 13(3) Reg. UE 2024/1689 obliges *providers* of high-risk AI
    systems to deliver, together with the system, instructions for use
    that contain a specific list of items. The schema mirrors that list
    one field per sub-paragraph so the rendered PDF can reference each
    article verbatim.

    Most fields are mandatory because the article phrases them as
    obligations ("the instructions for use shall contain..."). A few are
    typed as optional because they only apply in specific situations:

      * explainability — only when the system supports it
      * specific groups — only when the system targets specific
        cohorts
      * pre-determined changes — only if the provider declared any at
        the conformity assessment
      * log collection mechanisms — only when the system actually
        produces the Art. 12 logs the deployer needs to interpret
      * authorized representative — only when the provider is
        established outside the EU and has appointed one (Art. 22)
    """

    model_config = ConfigDict(extra="forbid")

    # Art. 13(3)(b)(i): intended purpose. Already on the AISystem row but
    # the article requires it inside the instructions document itself, and
    # the "purpose-as-described-by-the-provider-to-the-deployer" can be
    # narrower than the marketing-level purpose stored on the system.
    intended_purpose: Annotated[str, Field(min_length=1, max_length=4000)]

    # Art. 13(3)(b)(ii): accuracy + metric used.
    accuracy_metrics_and_level: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 13(3)(b)(ii): robustness (resilience to errors, faults,
    # inconsistencies, adversarial inputs).
    robustness_measures: Annotated[str, Field(min_length=1, max_length=4000)]

    # Art. 13(3)(b)(ii): cybersecurity measures (Art. 15(5)).
    cybersecurity_measures: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 13(3)(b)(ii): known/foreseeable circumstances that may impact
    # the expected level of accuracy/robustness/cybersecurity.
    accuracy_impacting_circumstances: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 13(3)(b)(iii): foreseeable misuse + risks to health, safety,
    # fundamental rights.
    foreseeable_misuse_and_risks: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 13(3)(b)(iv): explainability. Optional — not every system has
    # output-explanation capabilities.
    explainability_capabilities: Annotated[str, Field(max_length=4000)] | None = (
        None
    )

    # Art. 13(3)(b)(v): performance on specific groups when relevant.
    performance_on_specific_groups: Annotated[
        str, Field(max_length=4000)
    ] | None = None

    # Art. 13(3)(b)(vi): input-data specifications + relevant info on
    # training/validation/testing datasets.
    input_data_specifications: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 13(3)(b)(vii): how the deployer should interpret the output.
    output_interpretation_guide: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 13(3)(c): pre-determined changes (only if any were declared at
    # the initial conformity assessment).
    predetermined_changes: Annotated[str, Field(max_length=4000)] | None = None

    # Art. 13(3)(d): human-oversight measures referred to in Art. 14.
    human_oversight_measures: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 13(3)(e): computational + hardware resources needed.
    computational_and_hardware_resources: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 13(3)(e): expected lifetime + maintenance/care measures
    # (including software-update cadence).
    expected_lifetime_and_maintenance: Annotated[
        str, Field(min_length=1, max_length=4000)
    ]

    # Art. 13(3)(f) + Art. 12: how the deployer collects/stores/interprets
    # the automatic logs the system produces.
    log_collection_mechanisms: Annotated[
        str, Field(max_length=4000)
    ] | None = None

    # Art. 22: authorized representative (only for non-EU providers).
    authorized_representative_block: Annotated[
        str, Field(max_length=1000)
    ] | None = None

    # Compiler / responsible role. Same convention as the other narrative
    # documents — ends up on the PDF "compiled by" line so the deployer
    # knows whom to contact at the provider for clarifications.
    compiled_by_name: Annotated[str, Field(min_length=1, max_length=255)]
    compiled_by_role: Annotated[str, Field(min_length=1, max_length=255)]


class DocumentCreate(BaseModel):
    """Body for POST /systems/{id}/documents.

    Shapes today:
      - `document_type="annex_iv"` (default): no extra body required.
      - `document_type="declaration_of_conformity"`: must include
        `doc_input` with the Allegato V provider/signatory block.
      - `document_type="fria"`: must include `fria_input` with the
        Art. 27 narrative block.
      - `document_type="post_market_plan"`: must include `pmp_input`
        with the Art. 72 narrative block.
      - `document_type="risk_management_system"`: must include
        `rms_input` with the Art. 9 narrative + register block.
      - `document_type="supplier_clauses"`: must include `scl_input`
        with the Art. 25+26 supplier block.
      - `document_type="instructions_for_use"`: must include `ifu_input`
        with the Art. 13 narrative block.

    Conditional-required validation lives in the service layer so we can
    return a 422 with a clear message rather than fighting Pydantic's
    discriminator syntax.
    """

    model_config = ConfigDict(extra="forbid")

    document_type: DocumentType = "annex_iv"
    doc_input: DeclarationOfConformityInput | None = None
    fria_input: FundamentalRightsImpactAssessmentInput | None = None
    pmp_input: PostMarketMonitoringPlanInput | None = None
    rms_input: RiskManagementSystemInput | None = None
    scl_input: SupplierClausesInput | None = None
    ifu_input: InstructionsForUseInput | None = None


class DocumentRead(BaseModel):
    """The document metadata returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ai_system_id: uuid.UUID
    org_id: uuid.UUID
    classification_id: uuid.UUID | None
    document_type: DocumentType
    sha256_hash: str
    file_size: int
    tier: RiskTier
    is_gpai: bool
    rules_version: str
    generated_at: datetime
    generated_by: uuid.UUID | None
    # Free-form metadata snapshot (DoC provider/signatory block). NULL for
    # legacy Annex IV rows. Typed as `dict[str, Any]` here because the
    # shape varies by document_type and we don't want to force callers to
    # discriminate at the type level — a simple dict is enough for the UI.
    details: dict[str, Any] | None = None
