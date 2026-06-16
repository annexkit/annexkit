"""End-to-end AnnexKit demo: chatbot -> collector -> Annex IV PDF.

What this script does, in 4 steps:

  1. Validates ``ANNEXKIT_API_KEY`` is set + the collector is reachable.
  2. Declares an AI system "loan-screener-bot" via PUT /api/v1/systems.
     Annex III §5 essential services (loan eligibility) -> high-risk.
  3. Runs a small loan-eligibility conversation. Each turn goes
     through the SDK -> collector -> DB pipeline. Retrieval-augmented
     generation is simulated against a tiny in-memory KB; the cited
     sources are attached to each span via ``span.attach_source``.
  4. Fetches the Annex IV technical documentation in both Markdown
     and PDF formats and writes them to ``./out/``.

Run it (see ``README.md`` for the make-target shortcut):

    cp .env.example .env       # then paste an api_key from `make seed`
    uv sync
    uv run python chatbot.py

Read the generated PDF to see what the AnnexKit collector produces
from the runtime telemetry recorded during the conversation.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
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
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
SYSTEM_ID = "loan-screener-bot"
OUT_DIR = Path(__file__).resolve().parent / "out"


# ---------------------------------------------------------------------------
# AI system declaration — the Annex IV §1 fields the demo will populate
# ---------------------------------------------------------------------------
DECLARATION: dict[str, object] = {
    "system_id": SYSTEM_ID,
    "purpose": (
        "Conversational AI assistant that helps small-business owners "
        "self-assess their eligibility for loans up to EUR 100K. The "
        "assistant retrieves relevant excerpts from a static policy "
        "knowledge base and produces preliminary recommendations. Final "
        "loan decisions are made by human underwriters."
    ),
    # §5 essential services covers loan-related credit decisioning.
    "annex_iii_categories": ["annex3_5_essential_services"],
    # Article 50 transparency: a chatbot must disclose AI nature.
    "transparency_triggers": ["art50_chat_interaction"],
    "is_gpai": False,
    "provider_info": {
        "legal_name": "SmallBiz Loans S.r.l.",
        "address": "Corso Garibaldi 12, 20121 Milano (MI), Italia",
        "country": "IT",
        "contact_email": "compliance@smallbizloans.example",
        "system_version": "v0.5.0-beta",
        "software_environment": (
            "Python 3.13, OpenAI gpt-4o-mini, in-memory keyword KB, "
            "AnnexKit SDK 0.1.0"
        ),
        "hardware_environment": "Local development host (demo)",
        "validation_methods": (
            "Manual review of 50 transcript samples by the compliance team. "
            "Automated factuality benchmark against policy docs scheduled "
            "for Q3 2026."
        ),
        "notes": (
            "Architecture: prompt-engineered LLM with retrieval-augmented "
            "generation over a static policy knowledge base. No fine-tuning. "
            "Pre-screening only — no autonomous decision authority. Article "
            "26 deployer obligations apply (the live product would route "
            "every recommendation through a human underwriter)."
        ),
    },
}


# ---------------------------------------------------------------------------
# Synthetic knowledge base — realistic enough to look like a real RAG demo
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class KBDoc:
    id: str
    version: str
    text: str


KB: list[KBDoc] = [
    KBDoc(
        "eligibility-criteria",
        "v3",
        "Eligibility: business must be registered for at least 12 months, "
        "have at least EUR 30,000 annual revenue, and operate in an EU "
        "member state. Bankruptcy in the last 5 years disqualifies.",
    ),
    KBDoc(
        "required-documents",
        "v2",
        "Required documents: tax returns from the last 2 fiscal years, "
        "bank statements from the last 6 months, business registration "
        "certificate (visura camerale for IT), and a 2-page business plan.",
    ),
    KBDoc(
        "loan-amounts",
        "v1",
        "Loan amounts: minimum EUR 10,000, maximum EUR 100,000. Interest "
        "rates 5.5% to 9.2% APR depending on risk tier and term length "
        "(12 to 60 months).",
    ),
    KBDoc(
        "approval-timeline",
        "v1",
        "Standard approval: 5 to 7 business days after complete "
        "documentation is received. Express review (24 to 48 hours) is "
        "available for an additional 1.5% fee.",
    ),
    KBDoc(
        "compliance-disclosure",
        "v2",
        "This service uses AI for preliminary eligibility assessment. "
        "Final loan decisions are made by qualified human underwriters. "
        "Per EU AI Act Article 50, all chatbot interactions disclose the "
        "AI nature.",
    ),
]


def retrieve(query: str, kb: list[KBDoc], top_k: int = 2) -> list[KBDoc]:
    """Naive keyword-overlap retrieval — good enough for the demo.

    Real prods plug this into vector search (pgvector / Qdrant / etc.).
    """
    q_terms = {t.strip(".,?!").lower() for t in query.split()}
    scored: list[tuple[KBDoc, int]] = []
    for doc in kb:
        d_terms = {t.strip(".,?!").lower() for t in doc.text.split()}
        scored.append((doc, len(q_terms & d_terms)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [d for d, s in scored[:top_k] if s > 0] or scored[:1]


# ---------------------------------------------------------------------------
# LLM (real OpenAI when OPENAI_API_KEY is set, else deterministic stub)
# ---------------------------------------------------------------------------
def llm_call(
    user_message: str,
    history: list[dict[str, str]],
    retrieved: list[KBDoc],
) -> tuple[str, dict[str, str]]:
    """Return ``(assistant_reply, model_info)``.

    ``model_info`` keys are exactly what ``span.set_model(**)`` expects.
    """
    if OPENAI_KEY:
        from openai import OpenAI

        client = OpenAI()
        kb_context = "\n\n".join(
            f"[{d.id} v{d.version}]\n{d.text}" for d in retrieved
        )
        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are a loan eligibility advisor for SmallBiz Loans. "
                    "Help users assess eligibility for small business loans. "
                    "ALWAYS open by disclosing that you are an AI assistant "
                    "(per EU AI Act Article 50). Ground every claim in the "
                    "provided policy excerpts. Final loan decisions are "
                    "made by human underwriters.\n\n"
                    f"Policy excerpts:\n{kb_context}"
                ),
            },
            *history,
            {"role": "user", "content": user_message},
        ]
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,  # type: ignore[arg-type]
            temperature=0.2,
        )
        return (
            resp.choices[0].message.content or "",
            {"provider": "openai", "name": "gpt-4o-mini"},
        )

    return (
        _stub_response(user_message, retrieved),
        {"provider": "stub", "name": "rule-based"},
    )


def _stub_response(user_message: str, retrieved: list[KBDoc]) -> str:
    """Deterministic stub for users without OPENAI_API_KEY."""
    msg = user_message.lower()
    refs = ", ".join(f"{d.id} v{d.version}" for d in retrieved)
    refs_clause = f" (Sources: {refs}.)" if refs else ""

    if "documents" in msg or ("what" in msg and "need" in msg):
        return (
            "I am an AI assistant. You'll need: tax returns from the last 2 "
            "fiscal years, bank statements from the last 6 months, your "
            "visura camerale, and a 2-page business plan." + refs_clause
        )
    if "how long" in msg or "timeline" in msg or "approval" in msg:
        return (
            "I am an AI assistant. Standard approval takes 5-7 business "
            "days after complete documentation. Express review (24-48 "
            "hours) is available for a 1.5% additional fee." + refs_clause
        )
    if "eligible" in msg or "qualify" in msg:
        return (
            "I am an AI assistant. Based on what you've shared, you appear "
            "to meet the basic eligibility criteria (business older than "
            "12 months, EU-resident). A human underwriter will confirm "
            "after reviewing your documents." + refs_clause
        )
    if "amount" in msg or "much" in msg or "borrow" in msg:
        return (
            "I am an AI assistant. We offer loans from EUR 10,000 to EUR "
            "100,000 with interest rates 5.5% to 9.2% APR based on risk "
            "tier and term length (12 to 60 months)." + refs_clause
        )
    if "loan" in msg or "apply" in msg:
        return (
            "Welcome to SmallBiz Loans. I am an AI assistant — final "
            "decisions are made by human underwriters. To assess "
            "eligibility, could you share: type of business, location, "
            "and annual revenue?" + refs_clause
        )
    return (
        "I am an AI assistant. I can help with eligibility, required "
        "documents, loan amounts, and approval timelines. What would you "
        "like to know?" + refs_clause
    )


# ---------------------------------------------------------------------------
# Tracked conversation function — the AnnexKit instrumentation lives here
# ---------------------------------------------------------------------------
def chat(user_message: str, history: list[dict[str, str]]) -> str:
    """One conversation turn — instrumented end-to-end via session()."""
    with annexkit.session(
        system_id=SYSTEM_ID,
        risk_tier="auto",  # collector resolves from the declaration
        purpose=str(DECLARATION["purpose"]),
    ) as span:
        span.set_input(user_message)
        span.set_user_role("loan_applicant")

        retrieved = retrieve(user_message, KB)
        for doc in retrieved:
            span.attach_source(uri=f"kb://policy/{doc.id}", version=doc.version)

        reply, model_info = llm_call(user_message, history, retrieved)

        span.set_model(**model_info)
        span.set_output(reply)
        span.add_metadata(
            retrieved_count=len(retrieved),
            history_turns=len(history) // 2,
        )

        return reply


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
CONVERSATION_TURNS: list[str] = [
    "Hi, I'd like to apply for a small business loan.",
    "I run a bakery in Milan, established 2022, annual revenue around EUR 120,000.",
    "I'm looking for EUR 40,000 to buy new ovens. Am I eligible?",
    "What documents do I need to apply?",
    "How long does the approval take?",
]


def http_client() -> httpx.Client:
    return httpx.Client(
        base_url=COLLECTOR_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=20.0,
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
    """Clean section divider — no emojis, project rule."""
    if label:
        print(f"\n--- {label} {'-' * max(0, 60 - len(label))}")
    else:
        print("-" * 64)


def main() -> int:  # noqa: PLR0915 — orchestration script, linear is fine
    print("AnnexKit demo - chatbot-openai")
    print("=" * 32)
    print(f"Collector: {COLLECTOR_URL}")

    if not API_KEY:
        print("\nERROR: ANNEXKIT_API_KEY not set.")
        print()
        print("From the project root, run:")
        print("    make seed")
        print("Copy the api_key line, then either:")
        print("    export ANNEXKIT_API_KEY=ak_xxx       (and re-run)")
        print("    or paste it into examples/chatbot-openai/.env")
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
        print()
        print("From the project root, run:")
        print("    make up")
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
        print(
            "  LLM: OpenAI gpt-4o-mini (real)"
            if OPENAI_KEY
            else "  LLM: deterministic stub (set OPENAI_API_KEY for real calls)"
        )

        history: list[dict[str, str]] = []
        for i, user_msg in enumerate(CONVERSATION_TURNS, 1):
            print(f"\n  [{i}/{len(CONVERSATION_TURNS)}] >>> {user_msg}")
            reply = chat(user_msg, history)
            preview = reply if len(reply) <= 140 else reply[:137] + "..."
            print(f"        <<< {preview}")
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
    print("runtime telemetry the SDK collected during the conversation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
