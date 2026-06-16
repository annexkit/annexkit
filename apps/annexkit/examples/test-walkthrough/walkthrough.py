"""Three-persona end-to-end test walkthrough.

Walks the AnnexKit pipeline through three realistic paying-customer
profiles, one per pricing tier. Each persona declares its AI system(s)
via ``PUT /api/v1/systems``, ingests a handful of synthetic spans via
``POST /api/v1/spans``, then downloads its Annex IV documentation in
both Markdown and PDF form.

Personas:
  1. Velmara SaaS S.r.l. — Pro $49/mo
     One support chatbot. Article 50 transparency trigger. LIMITED risk.
  2. TechHire S.p.A. — Team $199/mo
     Two systems: cv-screener (HIGH, Annex III §4 employment) +
     interview-scheduler (LIMITED, Article 50). Multi-system tenant.
  3. Banca Esempio S.p.A. — Enterprise self-hosted €5K/yr
     Loan pre-screening chatbot. Annex III §5 essential services
     (HIGH risk) + Article 50. Full provider_info populated.

Run via:
    make walkthrough         # one-shot, seeds tenant + runs all
or:
    cp .env.example .env    # paste an api_key from `make seed`
    uv sync && uv run python walkthrough.py

Output (in ./out/):
    annex-iv-customer-support-bot.{md,pdf}
    annex-iv-cv-screener.{md,pdf}
    annex-iv-interview-scheduler.{md,pdf}
    annex-iv-loan-prescreen.{md,pdf}
"""

from __future__ import annotations

import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

import annexkit  # noqa: F401 — imported so the SDK auto-registers


load_dotenv()
COLLECTOR_URL = os.getenv("ANNEXKIT_COLLECTOR_URL", "http://localhost:8033")
API_KEY = os.environ.get("ANNEXKIT_API_KEY")
OUT_DIR = Path(__file__).resolve().parent / "out"


# ---------------------------------------------------------------------------
# Persona data structures
# ---------------------------------------------------------------------------
@dataclass
class SpanSeed:
    """One synthetic span to POST. Most fields default to sensible values."""

    system_id: str
    started_at: datetime
    ended_at: datetime
    latency_ms: int
    user_role: str
    model_provider: str
    model_name: str
    model_version: str | None = None
    sources: list[dict[str, str]] = field(default_factory=list)
    error: str | None = None
    input_chars: int = 200
    output_chars: int = 150


@dataclass
class Persona:
    code: str
    headline: str
    tier: str
    description: str
    declarations: list[dict[str, Any]]
    span_seeds: list[SpanSeed]


# ---------------------------------------------------------------------------
# Three persona definitions
# ---------------------------------------------------------------------------
def _t(day: int, hour: int = 10, minute: int = 0) -> datetime:
    """Helper: build a UTC timestamp on May `day` 2026 at `hour:minute`."""
    return datetime(2026, 5, day, hour, minute, tzinfo=UTC)


PERSONAS: list[Persona] = [
    # ----- Persona 1: Velmara SaaS — Pro $49/mo -------------------------------
    Persona(
        code="velmara",
        headline="Velmara SaaS S.r.l. — customer-support chatbot",
        tier="Pro — $49/month",
        description=(
            "A small SaaS company. One LLM-powered customer-support "
            "chatbot answering shipping, returns, and account questions. "
            "Article 50 transparency trigger applies (chatbot interaction); "
            "no Annex III categories, so the system classifies as LIMITED "
            "risk. Typical solo / small team customer profile."
        ),
        declarations=[
            {
                "system_id": "customer-support-bot",
                "purpose": (
                    "Conversational AI assistant that answers customer "
                    "questions about shipping status, returns policy, "
                    "and account management for Velmara SaaS users."
                ),
                "annex_iii_categories": [],
                "transparency_triggers": ["art50_chat_interaction"],
                "is_gpai": False,
                "provider_info": {
                    "legal_name": "Velmara SaaS S.r.l.",
                    "address": "Via dell'Indipendenza 22, 40121 Bologna (BO), Italia",
                    "country": "IT",
                    "contact_email": "compliance@velmara-saas.example",
                    "system_version": "v1.2.0",
                    "software_environment": (
                        "Python 3.12, FastAPI 0.110, OpenAI gpt-4o-mini, "
                        "Postgres 15"
                    ),
                    "hardware_environment": "Hetzner CX21, 4 vCPU, 8 GB RAM",
                    "validation_methods": (
                        "Manual review of 200 transcript samples by the "
                        "customer-success team. CSAT score tracked monthly."
                    ),
                    "notes": (
                        "Architecture: prompt-engineered LLM with "
                        "retrieval-augmented generation over a static FAQ "
                        "knowledge base of 47 articles."
                    ),
                },
            },
        ],
        span_seeds=[
            SpanSeed(
                system_id="customer-support-bot",
                started_at=_t(1, 9, 15),
                ended_at=_t(1, 9, 15) + timedelta(milliseconds=820),
                latency_ms=820,
                user_role="customer",
                model_provider="openai",
                model_name="gpt-4o-mini",
                model_version="2024-11-20",
                sources=[{"uri": "kb://faq/shipping-times", "version": "v2"}],
            ),
            SpanSeed(
                system_id="customer-support-bot",
                started_at=_t(2, 11, 30),
                ended_at=_t(2, 11, 30) + timedelta(milliseconds=940),
                latency_ms=940,
                user_role="customer",
                model_provider="openai",
                model_name="gpt-4o-mini",
                model_version="2024-11-20",
                sources=[{"uri": "kb://faq/return-policy", "version": "v3"}],
            ),
            SpanSeed(
                system_id="customer-support-bot",
                started_at=_t(3, 14, 45),
                ended_at=_t(3, 14, 45) + timedelta(milliseconds=1100),
                latency_ms=1100,
                user_role="customer",
                model_provider="openai",
                model_name="gpt-4o-mini",
                model_version="2024-11-20",
                sources=[{"uri": "kb://faq/account-management", "version": "v1"}],
            ),
            SpanSeed(
                system_id="customer-support-bot",
                started_at=_t(4, 8, 0),
                ended_at=_t(4, 8, 0) + timedelta(milliseconds=720),
                latency_ms=720,
                user_role="customer",
                model_provider="openai",
                model_name="gpt-4o-mini",
                model_version="2024-11-20",
                sources=[{"uri": "kb://faq/shipping-times", "version": "v2"}],
            ),
            SpanSeed(
                system_id="customer-support-bot",
                started_at=_t(4, 16, 22),
                ended_at=_t(4, 16, 22) + timedelta(milliseconds=2400),
                latency_ms=2400,
                user_role="customer",
                model_provider="openai",
                model_name="gpt-4o-mini",
                model_version="2024-11-20",
                error="openai.APIError: rate limit exceeded",
            ),
            SpanSeed(
                system_id="customer-support-bot",
                started_at=_t(5, 10, 5),
                ended_at=_t(5, 10, 5) + timedelta(milliseconds=890),
                latency_ms=890,
                user_role="employee",
                model_provider="openai",
                model_name="gpt-4o-mini",
                model_version="2024-11-20",
                sources=[{"uri": "kb://faq/return-policy", "version": "v3"}],
            ),
        ],
    ),
    # ----- Persona 2: TechHire — Team $199/mo ------------------------------
    Persona(
        code="techhire",
        headline="TechHire S.p.A. — HR-tech, two AI systems",
        tier="Team — $199/month",
        description=(
            "A 30-person HR-tech scaleup. Two AI systems running in "
            "production: a CV pre-ranker (HIGH risk under Annex III §4 "
            "employment) and an interview-scheduling chatbot (LIMITED, "
            "Article 50). Demonstrates a multi-system tenant — each "
            "system gets its own Annex IV PDF."
        ),
        declarations=[
            {
                "system_id": "cv-screener",
                "purpose": (
                    "Pre-ranks incoming CVs against role profiles, "
                    "outputs a top-20 shortlist for human recruiter "
                    "review. Final hiring decisions are made by humans."
                ),
                "annex_iii_categories": ["annex3_4_employment"],
                "transparency_triggers": [],
                "is_gpai": False,
                "provider_info": {
                    "legal_name": "TechHire S.p.A.",
                    "address": "Via Tortona 27, 20144 Milano (MI), Italia",
                    "country": "IT",
                    "contact_email": "compliance@techhire.example",
                    "system_version": "v3.1.4",
                    "software_environment": (
                        "Python 3.13, ranking head over frozen "
                        "sentence-transformers/all-mpnet-base-v2, "
                        "Postgres 16 + pgvector"
                    ),
                    "hardware_environment": (
                        "AWS eu-west-1, m7i.large, 8 GB RAM. "
                        "GDPR-compliant data residency."
                    ),
                    "validation_methods": (
                        "Holdout test set of 5,000 historical CVs "
                        "evaluated against human-graded shortlists. "
                        "Q1 2026 baseline: precision@20 = 0.78, "
                        "recall = 0.71. Adverse-impact testing across "
                        "gender + age groups (no statistically "
                        "significant disparity at p < 0.05)."
                    ),
                    "notes": (
                        "Architecture: ranking head fine-tuned monthly "
                        "on anonymised feedback from recruiters. "
                        "Embedding model frozen and updated quarterly "
                        "under provider sign-off. Pre-screening only — "
                        "no autonomous hiring decision authority."
                    ),
                },
            },
            {
                "system_id": "interview-scheduler",
                "purpose": (
                    "Conversational AI that schedules first-round "
                    "interviews between shortlisted candidates and "
                    "TechHire recruiters. Picks meeting slots from "
                    "Google Calendar availability."
                ),
                "annex_iii_categories": [],
                "transparency_triggers": ["art50_chat_interaction"],
                "is_gpai": False,
                "provider_info": {
                    "legal_name": "TechHire S.p.A.",
                    "address": "Via Tortona 27, 20144 Milano (MI), Italia",
                    "country": "IT",
                    "contact_email": "compliance@techhire.example",
                    "system_version": "v1.0.2",
                    "software_environment": (
                        "Python 3.13, Anthropic Claude Sonnet, "
                        "Google Calendar API"
                    ),
                    "hardware_environment": (
                        "AWS eu-west-1, t3.small. "
                        "GDPR-compliant data residency."
                    ),
                    "notes": (
                        "Light wrapper around Anthropic Claude with "
                        "Calendar integration. AI nature disclosed to "
                        "candidates per Article 50."
                    ),
                },
            },
        ],
        span_seeds=[
            # cv-screener — 4 spans
            SpanSeed(
                system_id="cv-screener",
                started_at=_t(1, 9, 0),
                ended_at=_t(1, 9, 0) + timedelta(milliseconds=180),
                latency_ms=180,
                user_role="recruiter",
                model_provider="huggingface",
                model_name="sentence-transformers/all-mpnet-base-v2",
                model_version="2.7.0",
                sources=[
                    {"uri": "kb://role-profiles/senior-backend-eng", "version": "v4"},
                ],
                input_chars=3500,
                output_chars=200,
            ),
            SpanSeed(
                system_id="cv-screener",
                started_at=_t(1, 9, 15),
                ended_at=_t(1, 9, 15) + timedelta(milliseconds=210),
                latency_ms=210,
                user_role="recruiter",
                model_provider="huggingface",
                model_name="sentence-transformers/all-mpnet-base-v2",
                model_version="2.7.0",
                sources=[
                    {"uri": "kb://role-profiles/senior-backend-eng", "version": "v4"},
                ],
                input_chars=4200,
                output_chars=200,
            ),
            SpanSeed(
                system_id="cv-screener",
                started_at=_t(2, 14, 22),
                ended_at=_t(2, 14, 22) + timedelta(milliseconds=195),
                latency_ms=195,
                user_role="recruiter",
                model_provider="huggingface",
                model_name="sentence-transformers/all-mpnet-base-v2",
                model_version="2.7.0",
                sources=[
                    {"uri": "kb://role-profiles/data-scientist", "version": "v3"},
                ],
                input_chars=3800,
                output_chars=200,
            ),
            SpanSeed(
                system_id="cv-screener",
                started_at=_t(3, 11, 8),
                ended_at=_t(3, 11, 8) + timedelta(milliseconds=170),
                latency_ms=170,
                user_role="recruiter",
                model_provider="huggingface",
                model_name="sentence-transformers/all-mpnet-base-v2",
                model_version="2.7.0",
                sources=[
                    {"uri": "kb://role-profiles/senior-backend-eng", "version": "v4"},
                ],
                input_chars=2900,
                output_chars=200,
            ),
            # interview-scheduler — 4 spans
            SpanSeed(
                system_id="interview-scheduler",
                started_at=_t(2, 10, 0),
                ended_at=_t(2, 10, 0) + timedelta(milliseconds=1450),
                latency_ms=1450,
                user_role="candidate",
                model_provider="anthropic",
                model_name="claude-sonnet-4-5",
                model_version="20250929",
                sources=[],
                input_chars=180,
                output_chars=240,
            ),
            SpanSeed(
                system_id="interview-scheduler",
                started_at=_t(2, 10, 5),
                ended_at=_t(2, 10, 5) + timedelta(milliseconds=1320),
                latency_ms=1320,
                user_role="candidate",
                model_provider="anthropic",
                model_name="claude-sonnet-4-5",
                model_version="20250929",
                sources=[],
            ),
            SpanSeed(
                system_id="interview-scheduler",
                started_at=_t(3, 16, 30),
                ended_at=_t(3, 16, 30) + timedelta(milliseconds=1180),
                latency_ms=1180,
                user_role="candidate",
                model_provider="anthropic",
                model_name="claude-sonnet-4-5",
                model_version="20250929",
                sources=[],
            ),
            SpanSeed(
                system_id="interview-scheduler",
                started_at=_t(4, 14, 0),
                ended_at=_t(4, 14, 0) + timedelta(milliseconds=1620),
                latency_ms=1620,
                user_role="candidate",
                model_provider="anthropic",
                model_name="claude-sonnet-4-5",
                model_version="20250929",
                sources=[],
            ),
        ],
    ),
    # ----- Persona 3: Banca Esempio — Enterprise €5K/yr --------------------
    Persona(
        code="banca-esempio",
        headline="Banca Esempio S.p.A. — loan pre-screening (regulated)",
        tier="Enterprise self-hosted — €5,000 / year",
        description=(
            "An Italian retail bank. Single AI system: a loan-eligibility "
            "pre-screener for SME loans up to €100K. HIGH risk under "
            "Annex III §5 essential services (credit decisioning) plus "
            "Article 50 transparency. Full provider_info, "
            "validation methodology, and notes populated — what a "
            "regulator-presentation-grade declaration looks like."
        ),
        declarations=[
            {
                "system_id": "loan-prescreen",
                "purpose": (
                    "Conversational AI assistant that pre-screens small-"
                    "and-medium-business owners against the bank's "
                    "published eligibility criteria for loans of EUR "
                    "10,000 to EUR 100,000. Surfaces a "
                    "preliminary recommendation; final loan decisions "
                    "are made by qualified human underwriters, who "
                    "receive the AI's output as one input alongside "
                    "credit score and financial documentation."
                ),
                "annex_iii_categories": ["annex3_5_essential_services"],
                "transparency_triggers": ["art50_chat_interaction"],
                "is_gpai": False,
                "provider_info": {
                    "legal_name": "Banca Esempio S.p.A.",
                    "address": "Via del Corso 138, 00186 Roma (RM), Italia",
                    "country": "IT",
                    "contact_email": "ai-compliance@banca-esempio.example",
                    "authorised_representative": (
                        "Dott.ssa Maria Rossi — Chief Compliance Officer, "
                        "via del Corso 138, 00186 Roma (RM), Italia"
                    ),
                    "system_version": "v2.4.1",
                    "software_environment": (
                        "Python 3.13, Mistral La Plateforme (mistral-large-2411), "
                        "internal policy KB (Postgres 16 + pgvector), "
                        "AnnexKit SDK 0.1.0. Deployed on AWS eu-central-1 "
                        "(Frankfurt) — PSD2 + GDPR + NIS2 compliant."
                    ),
                    "hardware_environment": (
                        "AWS eu-central-1 (Frankfurt), m7i.xlarge x 2 "
                        "(active-active), 32 GB RAM each. Encryption "
                        "at rest (KMS) + in transit (TLS 1.3)."
                    ),
                    "validation_methods": (
                        "Quarterly back-testing against 12 months of "
                        "human-underwriter decisions (n=1,847 in Q1 2026). "
                        "Approval-rate parity tested across protected "
                        "characteristics (region, age, business sector) "
                        "with 95% confidence intervals; max disparity "
                        "observed: 3.2 percentage points (within "
                        "fair-lending tolerance). Adversarial prompt "
                        "testing performed monthly by internal red team. "
                        "Audit trail retained for 7 years per Bank of "
                        "Italy circular 285."
                    ),
                    "notes": (
                        "Pre-screening only — no autonomous credit "
                        "authority. Every applicant whose pre-screen "
                        "is negative receives written notice with "
                        "reasoning + appeal contact (Art. 22 GDPR). "
                        "Human-in-the-loop on every approval > EUR "
                        "25,000. AI nature disclosed at session start "
                        "(Article 50 IT/EN). Operates under Bank of "
                        "Italy cir. 285 + EBA AI guidelines + "
                        "internal AI governance committee oversight."
                    ),
                },
            },
        ],
        span_seeds=[
            SpanSeed(
                system_id="loan-prescreen",
                started_at=_t(1, 9, 0),
                ended_at=_t(1, 9, 0) + timedelta(milliseconds=1840),
                latency_ms=1840,
                user_role="loan_applicant",
                model_provider="mistral",
                model_name="mistral-large-2411",
                model_version="2411",
                sources=[
                    {"uri": "kb://policy/eligibility-criteria", "version": "v3"},
                    {"uri": "kb://policy/required-documents", "version": "v2"},
                ],
                input_chars=380,
                output_chars=520,
            ),
            SpanSeed(
                system_id="loan-prescreen",
                started_at=_t(1, 11, 22),
                ended_at=_t(1, 11, 22) + timedelta(milliseconds=2100),
                latency_ms=2100,
                user_role="loan_applicant",
                model_provider="mistral",
                model_name="mistral-large-2411",
                model_version="2411",
                sources=[
                    {"uri": "kb://policy/eligibility-criteria", "version": "v3"},
                    {"uri": "kb://policy/loan-amounts", "version": "v1"},
                ],
                input_chars=410,
                output_chars=480,
            ),
            SpanSeed(
                system_id="loan-prescreen",
                started_at=_t(2, 10, 15),
                ended_at=_t(2, 10, 15) + timedelta(milliseconds=1950),
                latency_ms=1950,
                user_role="loan_applicant",
                model_provider="mistral",
                model_name="mistral-large-2411",
                model_version="2411",
                sources=[
                    {"uri": "kb://policy/required-documents", "version": "v2"},
                    {"uri": "kb://policy/approval-timeline", "version": "v1"},
                ],
                input_chars=320,
                output_chars=600,
            ),
            SpanSeed(
                system_id="loan-prescreen",
                started_at=_t(3, 14, 5),
                ended_at=_t(3, 14, 5) + timedelta(milliseconds=2350),
                latency_ms=2350,
                user_role="loan_applicant",
                model_provider="mistral",
                model_name="mistral-large-2411",
                model_version="2411",
                sources=[
                    {"uri": "kb://policy/eligibility-criteria", "version": "v3"},
                ],
                error="httpx.TimeoutException: read timeout after 30s",
            ),
            SpanSeed(
                system_id="loan-prescreen",
                started_at=_t(3, 14, 7),
                ended_at=_t(3, 14, 7) + timedelta(milliseconds=1720),
                latency_ms=1720,
                user_role="loan_applicant",
                model_provider="mistral",
                model_name="mistral-large-2411",
                model_version="2411",
                sources=[
                    {"uri": "kb://policy/eligibility-criteria", "version": "v3"},
                ],
                input_chars=380,
                output_chars=540,
            ),
            SpanSeed(
                system_id="loan-prescreen",
                started_at=_t(4, 9, 30),
                ended_at=_t(4, 9, 30) + timedelta(milliseconds=2080),
                latency_ms=2080,
                user_role="loan_applicant",
                model_provider="mistral",
                model_name="mistral-large-2411",
                model_version="2411",
                sources=[
                    {"uri": "kb://policy/loan-amounts", "version": "v1"},
                    {"uri": "kb://policy/approval-timeline", "version": "v1"},
                ],
                input_chars=290,
                output_chars=460,
            ),
            SpanSeed(
                system_id="loan-prescreen",
                started_at=_t(5, 11, 10),
                ended_at=_t(5, 11, 10) + timedelta(milliseconds=1890),
                latency_ms=1890,
                user_role="loan_officer",
                model_provider="mistral",
                model_name="mistral-large-2411",
                model_version="2411",
                sources=[
                    {"uri": "kb://policy/required-documents", "version": "v2"},
                ],
                input_chars=520,
                output_chars=380,
            ),
            SpanSeed(
                system_id="loan-prescreen",
                started_at=_t(6, 16, 0),
                ended_at=_t(6, 16, 0) + timedelta(milliseconds=2240),
                latency_ms=2240,
                user_role="loan_applicant",
                model_provider="mistral",
                model_name="mistral-large-2411",
                model_version="2411",
                sources=[
                    {"uri": "kb://policy/eligibility-criteria", "version": "v3"},
                    {"uri": "kb://policy/loan-amounts", "version": "v1"},
                ],
                input_chars=440,
                output_chars=580,
            ),
        ],
    ),
]


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def http_client() -> httpx.Client:
    return httpx.Client(
        base_url=COLLECTOR_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=20.0,
    )


def declare(client: httpx.Client, declaration: dict[str, Any]) -> dict[str, Any]:
    resp = client.put("/api/v1/systems", json=declaration)
    resp.raise_for_status()
    return resp.json()


def ingest_span(client: httpx.Client, seed: SpanSeed) -> None:
    """POST one span using the seed."""
    payload: dict[str, Any] = {
        "trace_id": uuid.uuid4().hex,
        "span_id": uuid.uuid4().hex[:16],
        "system_id": seed.system_id,
        "deployment": "prod",
        "risk_tier": "auto",
        "started_at": seed.started_at.isoformat(),
        "ended_at": seed.ended_at.isoformat(),
        "latency_ms": seed.latency_ms,
        "model_provider": seed.model_provider,
        "model_name": seed.model_name,
        "model_version": seed.model_version,
        "input_hash": uuid.uuid4().hex + uuid.uuid4().hex,
        "input_chars": seed.input_chars,
        "output_hash": uuid.uuid4().hex + uuid.uuid4().hex,
        "output_chars": seed.output_chars,
        "sources": seed.sources,
        "user_role": seed.user_role,
        "error": seed.error,
        "metadata": {},
        "sdk_version": "0.1.0",
        "sdk_lang": "python",
    }
    resp = client.post("/api/v1/spans", json=payload)
    resp.raise_for_status()


def fetch_annex_iv(client: httpx.Client, system_id: str, fmt: str) -> bytes:
    resp = client.get(
        f"/api/v1/systems/{system_id}/annex-iv", params={"format": fmt}
    )
    resp.raise_for_status()
    return resp.content


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
def hr(label: str = "") -> None:
    if label:
        print(f"\n=== {label} {'=' * max(0, 70 - len(label))}")
    else:
        print("=" * 74)


def run_persona(client: httpx.Client, persona: Persona) -> list[Path]:
    """Run one persona end-to-end. Returns the list of saved PDF paths."""
    hr(persona.headline)
    print(f"  Tier: {persona.tier}")
    print(f"  {persona.description}")
    print()

    # 1. Declare each AI system.
    for decl in persona.declarations:
        result = declare(client, decl)
        print(
            f"  [PUT  /api/v1/systems] {result['system_id']:<24} "
            f"-> tier {result['risk_tier'].upper()}, "
            f"rules v{result['rules_version']}"
        )

    # 2. Ingest spans.
    span_count_by_system: dict[str, int] = {}
    for seed in persona.span_seeds:
        ingest_span(client, seed)
        span_count_by_system[seed.system_id] = (
            span_count_by_system.get(seed.system_id, 0) + 1
        )
    print()
    for system_id, n in span_count_by_system.items():
        print(f"  [POST /api/v1/spans]    {system_id:<24} -> {n} spans ingested")

    # 3. Download Annex IV in MD + PDF for each system.
    print()
    saved: list[Path] = []
    for decl in persona.declarations:
        system_id = decl["system_id"]
        for fmt in ("md", "pdf"):
            content = fetch_annex_iv(client, system_id, fmt)
            path = OUT_DIR / f"annex-iv-{system_id}.{fmt}"
            path.write_bytes(content)
            saved.append(path)
            print(
                f"  [GET annex-iv format={fmt}] {system_id:<24} "
                f"-> {len(content):>7,} bytes  saved {path.name}"
            )

    return saved


def main() -> int:
    print("AnnexKit — three-persona end-to-end test walkthrough")
    print("=" * 74)
    print(f"Collector: {COLLECTOR_URL}")

    if not API_KEY:
        print("\nERROR: ANNEXKIT_API_KEY not set.")
        print()
        print("From the project root, run:")
        print("    make seed")
        print("Copy the api_key line, then either:")
        print("    export ANNEXKIT_API_KEY=ak_...      (and re-run)")
        print("    or paste it into examples/test-walkthrough/.env")
        print()
        print("Or use the one-shot:")
        print("    make walkthrough")
        return 1

    print(f"API key:   {API_KEY[:11]}*** (suffix hidden)")
    OUT_DIR.mkdir(exist_ok=True)

    # Health check.
    try:
        with httpx.Client(timeout=5.0) as health:
            health.get(f"{COLLECTOR_URL}/health").raise_for_status()
    except Exception as exc:
        print(f"\nERROR: Collector at {COLLECTOR_URL} is not reachable.")
        print(f"  ({exc})")
        print("  Run `make up` from the project root to start it.")
        return 2

    all_saved: list[Path] = []
    with http_client() as client:
        for persona in PERSONAS:
            all_saved.extend(run_persona(client, persona))

    # Summary.
    hr("Walkthrough complete")
    print(f"\n  {len(PERSONAS)} personas walked end-to-end")
    print(
        f"  {sum(len(p.declarations) for p in PERSONAS)} AI systems declared"
    )
    print(f"  {sum(len(p.span_seeds) for p in PERSONAS)} spans ingested")
    print(f"  {len(all_saved)} output files saved to {OUT_DIR}/")
    print()
    pdf_files = [p for p in all_saved if p.suffix == ".pdf"]
    md_files = [p for p in all_saved if p.suffix == ".md"]
    print(f"  PDFs ({len(pdf_files)}):")
    for p in pdf_files:
        print(f"    - {p.name}  ({p.stat().st_size:,} bytes)")
    print(f"\n  Markdown copies ({len(md_files)}):")
    for p in md_files:
        print(f"    - {p.name}  ({p.stat().st_size:,} bytes)")
    print()
    print("  Next: open each PDF to inspect. The same content is also")
    print("  rendered as Markdown for easy diffing / grepping.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
