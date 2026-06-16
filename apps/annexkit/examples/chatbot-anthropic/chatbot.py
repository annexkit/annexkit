"""End-to-end AnnexKit demo: chatbot -> collector -> Annex IV PDF (Anthropic).

Sibling to ``examples/chatbot-openai/``. Same shape, different LLM
provider + different Annex III category — so a side-by-side comparison
shows how AnnexKit handles multiple regulated AI systems in one tenant.

What this script does, in 4 steps:

  1. Validates ``ANNEXKIT_API_KEY`` + ``ANTHROPIC_API_KEY`` are set and
     the collector is reachable.
  2. Declares an AI system "cv-screener-anthropic" via PUT /api/v1/systems.
     Annex III §4 employment (CV screening) -> high-risk.
  3. Runs a small CV-screening conversation. Each turn goes through the
     SDK -> collector -> DB pipeline. The Anthropic Messages API powers
     the assistant; per Article 50, every reply opens by disclosing the
     AI nature.
  4. Fetches the Annex IV technical documentation in both Markdown
     and PDF formats and writes them to ``./out/``.

Run it:

    cp .env.example .env       # paste ANNEXKIT_API_KEY from `make seed`
                               # and your ANTHROPIC_API_KEY
    uv sync
    uv run python chatbot.py

Open the generated PDF to see the Annex IV that AnnexKit assembled from
the runtime telemetry recorded during the conversation.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

import annexkit


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
load_dotenv(override=True)  # demo .env wins over an empty shell var

COLLECTOR_URL = os.getenv("ANNEXKIT_COLLECTOR_URL", "http://localhost:8033")
API_KEY = os.environ.get("ANNEXKIT_API_KEY")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
SYSTEM_ID = "cv-screener-anthropic"
MODEL_NAME = "claude-haiku-4-5"
MODEL_VERSION = "claude-haiku-4-5-20251001"
OUT_DIR = Path(__file__).resolve().parent / "out"


# ---------------------------------------------------------------------------
# AI system declaration — Annex IV §1 fields for the demo
# ---------------------------------------------------------------------------
DECLARATION: dict[str, object] = {
    "system_id": SYSTEM_ID,
    "purpose": (
        "Conversational AI assistant that helps a recruiter pre-screen "
        "candidates for a software engineer role. Given a candidate "
        "summary, the assistant produces a structured shortlist note "
        "(strengths, gaps, suggested interview questions). Final "
        "hire/no-hire decisions are made by human recruiters."
    ),
    # Annex III §4: employment, workers management, recruitment.
    "annex_iii_categories": ["annex3_4_employment"],
    # Article 50: chatbot must disclose AI nature on every turn.
    "transparency_triggers": ["art50_chat_interaction"],
    "is_gpai": False,
    "provider_info": {
        "legal_name": "TopTalent S.r.l.",
        "address": "Via Manzoni 1, 20121 Milano (MI), Italia",
        "country": "IT",
        "contact_email": "compliance@toptalent.example",
        "system_version": "v0.3.0-beta",
        "software_environment": (
            f"Python 3.13, Anthropic {MODEL_VERSION}, "
            "AnnexKit SDK 0.1.0"
        ),
        "hardware_environment": "Local development host (demo)",
        "validation_methods": (
            "Manual review of 30 candidate-screening transcripts by the "
            "TopTalent compliance team. Bias audit against the EU "
            "non-discrimination checklist scheduled for Q3 2026."
        ),
        "notes": (
            "Architecture: prompt-engineered LLM with no fine-tuning, no "
            "retrieval. Pre-screening only — no autonomous decision "
            "authority. Article 26 deployer obligations apply (every "
            "shortlist note is reviewed by a human recruiter before any "
            "candidate is contacted). Annex III §4 high-risk because the "
            "system informs employment-related decisions."
        ),
    },
}


# ---------------------------------------------------------------------------
# LLM call (Anthropic Messages API)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are a CV pre-screening assistant for TopTalent's recruiting team. "
    "For each candidate summary the recruiter gives you, produce a "
    "structured note with: (1) a one-sentence fit verdict, (2) strengths "
    "for the software engineer role, (3) gaps to probe, and (4) two "
    "suggested interview questions. ALWAYS open by disclosing that you "
    "are an AI assistant (per EU AI Act Article 50). Final hire decisions "
    "are made by human recruiters."
)


def llm_call(user_message: str, history: list[dict[str, str]]) -> str:
    """One round-trip to Claude. Returns the assistant text."""
    from anthropic import Anthropic

    client = Anthropic()
    messages: list[dict[str, str]] = [
        *history,
        {"role": "user", "content": user_message},
    ]
    resp = client.messages.create(
        model=MODEL_VERSION,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages,  # type: ignore[arg-type]
        temperature=0.2,
    )
    # Claude returns content as a list of blocks; we use only text.
    parts = [block.text for block in resp.content if block.type == "text"]
    return "".join(parts).strip()


# ---------------------------------------------------------------------------
# Tracked conversation function — annexkit.session() captures model info
# ---------------------------------------------------------------------------
def screen_candidate(user_message: str, history: list[dict[str, str]]) -> str:
    """One screening turn — instrumented end-to-end via session().

    Uses session() (not @track) so we can attach model_provider/name/version
    to the span — the data points that show up in Annex IV §2.2.
    """
    with annexkit.session(
        system_id=SYSTEM_ID,
        risk_tier="auto",  # collector resolves "high" from declaration
        purpose=str(DECLARATION["purpose"]),
    ) as span:
        span.set_input(user_message)
        span.set_user_role("recruiter")

        reply = llm_call(user_message, history)

        span.set_model(provider="anthropic", name=MODEL_NAME, version=MODEL_VERSION)
        span.set_output(reply)
        span.add_metadata(history_turns=len(history) // 2)

        return reply


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
CONVERSATION_TURNS: list[str] = [
    "Candidate A: 5 years Python at a Milan SaaS, mostly Flask + REST APIs. "
    "Has built two production OpenAI integrations. Looking for a senior "
    "backend role. Asking salary EUR 55k.",
    "Candidate B: 8 years Java enterprise at a bank in Frankfurt, recently "
    "started learning Go and Kubernetes. No public AI/ML experience. Wants "
    "to move into AI infrastructure. EUR 80k expectations.",
    "Candidate C: 2 years total experience — first job was a Rails monolith, "
    "current job is a Vercel/Next.js shop. Self-taught machine learning on "
    "the side, has a small published HuggingFace model. EUR 45k.",
    "Candidate D: 12 years C++ at a German automotive OEM, AUTOSAR + safety "
    "critical. No web stack. Wants to retrain into MLOps. EUR 95k expectations.",
    "Candidate E: 6 years full-stack at a healthtech startup in Rome. Led "
    "GDPR compliance work for the engineering team. Comfortable with Python "
    "+ TypeScript + Postgres + Kubernetes. EUR 70k.",
]


def http_client() -> httpx.Client:
    return httpx.Client(
        base_url=COLLECTOR_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30.0,
    )


def declare_system(client: httpx.Client) -> dict[str, object]:
    resp = client.put("/api/v1/systems", json=DECLARATION)
    resp.raise_for_status()
    return resp.json()


def fetch_annex_iv(client: httpx.Client, fmt: str) -> bytes:
    resp = client.get(
        f"/api/v1/systems/{SYSTEM_ID}/annex-iv",
        params={"format": fmt},
    )
    resp.raise_for_status()
    return resp.content


def hr(label: str = "") -> None:
    if label:
        print(f"\n--- {label} {'-' * max(0, 60 - len(label))}")
    else:
        print("-" * 64)


def main() -> int:  # noqa: PLR0915 — linear orchestration is fine
    print("AnnexKit demo - chatbot-anthropic")
    print("=" * 35)
    print(f"Collector: {COLLECTOR_URL}")
    print(f"LLM:       Anthropic {MODEL_VERSION}")

    if not API_KEY:
        print("\nERROR: ANNEXKIT_API_KEY not set.")
        print("Run `make seed` from project root, then either:")
        print("    export ANNEXKIT_API_KEY=ak_xxx   (and re-run)")
        print("    or paste it into examples/chatbot-anthropic/.env")
        return 1

    if not ANTHROPIC_KEY:
        print("\nERROR: ANTHROPIC_API_KEY not set.")
        print("Get one at https://console.anthropic.com/ and either:")
        print("    export ANTHROPIC_API_KEY=sk-ant-xxx   (and re-run)")
        print("    or paste it into examples/chatbot-anthropic/.env")
        return 1

    print(f"API key:   {API_KEY[:11]}*** (suffix hidden)")

    annexkit.configure(api_key=API_KEY, collector_url=COLLECTOR_URL)

    # --- Health check ---
    try:
        with httpx.Client(timeout=5.0) as health:
            health.get(f"{COLLECTOR_URL}/health").raise_for_status()
    except Exception as exc:
        print(f"\nERROR: Collector at {COLLECTOR_URL} is not reachable.")
        print(f"  ({exc})")
        print("Run `make up` from project root first.")
        return 2

    OUT_DIR.mkdir(exist_ok=True)

    with http_client() as client:
        # --- Step 1: Declare ---
        hr("Step 1/4: Declare AI system")
        result = declare_system(client)
        print(f"  System ID:        {result['system_id']}")
        print(f"  Risk tier:        {str(result['risk_tier']).upper()}")
        print(f"  Rules version:    {result['rules_version']}")
        reasoning = result.get("reasoning") or []
        if reasoning:
            print("  Triggered rules:")
            for r in reasoning:  # type: ignore[union-attr]
                print(f"    - {r['rule_id']}  ({r['article']})")

        # --- Step 2: Conversations ---
        hr("Step 2/4: Run conversation")
        history: list[dict[str, str]] = []
        for i, user_msg in enumerate(CONVERSATION_TURNS, 1):
            preview_in = user_msg if len(user_msg) <= 90 else user_msg[:87] + "..."
            print(f"\n  [{i}/{len(CONVERSATION_TURNS)}] >>> {preview_in}")
            reply = screen_candidate(user_msg, history)
            preview_out = reply if len(reply) <= 160 else reply[:157] + "..."
            print(f"        <<< {preview_out}")
            history.append({"role": "user", "content": user_msg})
            history.append({"role": "assistant", "content": reply})

        # Make sure the HTTP exporter has flushed.
        annexkit.flush()

        # --- Step 3: Annex IV markdown ---
        hr("Step 3/4: Fetch Annex IV (markdown)")
        md = fetch_annex_iv(client, "md")
        md_path = OUT_DIR / f"annex-iv-{SYSTEM_ID}.md"
        md_path.write_bytes(md)
        print(f"  Saved {len(md):,} bytes to {md_path}")

        # --- Step 4: Annex IV PDF ---
        hr("Step 4/4: Fetch Annex IV (PDF)")
        pdf = fetch_annex_iv(client, "pdf")
        pdf_path = OUT_DIR / f"annex-iv-{SYSTEM_ID}.pdf"
        pdf_path.write_bytes(pdf)
        print(f"  Saved {len(pdf):,} bytes to {pdf_path}")

    hr()
    print("Demo complete.")
    print(f"  Markdown: {md_path}")
    print(f"  PDF:      {pdf_path}")
    print()
    print("Open the PDF to see the EU AI Act Annex IV technical")
    print("documentation generated for this AI system, populated from the")
    print(f"runtime telemetry of {len(CONVERSATION_TURNS)} Claude invocations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())



