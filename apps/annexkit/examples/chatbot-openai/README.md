# chatbot-openai — end-to-end AnnexKit demo

A loan-eligibility chatbot that walks through the **complete AnnexKit
loop** in one runnable script:

1. Declare an AI system (high-risk, Annex III §5 essential services).
2. Run a 5-turn conversation, with each turn instrumented via
   `annexkit.session(...)`.
3. Each invocation flows through the SDK → collector → Postgres,
   carrying SHA-256 hashes of input/output, retrieval source URIs,
   model identifiers, latency, user role, free-form metadata.
4. Fetch the Annex IV technical documentation in Markdown + PDF —
   fully populated from the conversation that just happened.

By the end the script writes:

```
out/annex-iv-loan-screener-bot.md   (~ 8 KB, full bilingual document)
out/annex-iv-loan-screener-bot.pdf  (~ 70 KB, audit-grade PDF)
```

## Prerequisites

You need the AnnexKit collector running (it persists the spans and
generates the Annex IV) and a tenant API key the demo will use.

From the **project root**:

```bash
make up           # start Postgres + collector
make seed         # mint a test tenant + print its api_key
```

Copy the `api_key=ak_...` line and either:

  * `export ANNEXKIT_API_KEY=ak_...` in your shell, **or**
  * paste it into `examples/chatbot-openai/.env` (copied from
    `.env.example` first).

## Run

```bash
cd examples/chatbot-openai
cp .env.example .env       # paste the api_key
uv sync                    # installs annexkit (from local SDK), httpx, openai, dotenv
uv run python chatbot.py
```

You'll see something like:

```text
AnnexKit demo - chatbot-openai
================================
Collector: http://localhost:8033
API key:   ak_5i9qwx67xx*** (suffix hidden)

--- Step 1/4: Declare AI system -----------------------------
  System ID:        loan-screener-bot
  Risk tier:        HIGH
  Rules version:    1.0.0
  Triggered rules:
    - annex3_5_essential_services  (Annex III, §5)
    - art50_chat_interaction       (Article 50)

--- Step 2/4: Run conversation ------------------------------
  LLM: deterministic stub (set OPENAI_API_KEY for real calls)

  [1/5] >>> Hi, I'd like to apply for a small business loan.
        <<< Welcome to SmallBiz Loans. I am an AI assistant — ...
  [2/5] >>> I run a bakery in Milan, established 2022, ...
        <<< I am an AI assistant. Based on what you've ...
  ...

--- Step 3/4: Fetch Annex IV (markdown) ---------------------
  Saved 8,247 bytes to .../out/annex-iv-loan-screener-bot.md

--- Step 4/4: Fetch Annex IV (PDF) --------------------------
  Saved 73,041 bytes to .../out/annex-iv-loan-screener-bot.pdf

----------------------------------------------------------------
Demo complete.
  Markdown: .../out/annex-iv-loan-screener-bot.md
  PDF:      .../out/annex-iv-loan-screener-bot.pdf
```

## What's actually instrumented

The `chat()` function uses
[`annexkit.session(...)`](../../sdk/annexkit/session.py) instead of
the simpler `@track` decorator because it does retrieval-augmented
generation: each turn cites two policy excerpts as sources, which the
session API can record explicitly via `span.attach_source(...)`.

```python
def chat(user_message, history):
    with annexkit.session(
        system_id="loan-screener-bot",
        risk_tier="auto",
        purpose=DECLARATION["purpose"],
    ) as span:
        span.set_input(user_message)
        span.set_user_role("loan_applicant")

        retrieved = retrieve(user_message, KB)
        for doc in retrieved:
            span.attach_source(uri=f"kb://policy/{doc.id}", version=doc.version)

        reply, model_info = llm_call(user_message, history, retrieved)
        span.set_model(**model_info)
        span.set_output(reply)
        span.add_metadata(retrieved_count=len(retrieved))

        return reply
```

## OpenAI vs stub

By default the demo uses a deterministic rule-based stub so it runs
without external dependencies (or money). Set `OPENAI_API_KEY` and the
demo invokes `gpt-4o-mini` for each turn instead.

The Annex IV document looks the same either way — only the
`model_provider` field on the spans changes (`openai` vs `stub`).
That's the privacy-by-default contract: the document never reproduces
the actual user/model text — only hashes + char counts + source URIs.

## What to look at in the generated Annex IV

The PDF is the headline output. Things to spot:

| Section | What you'll see |
|---|---|
| Cover page | Big **HIGH RISK** badge in red-orange. |
| Executive summary | Auto-generated paragraph naming the system, the tier, the invocation count, the error rate, and the active/inactive status. |
| §1.2 Persons responsible | Populated from `provider_info` ("SmallBiz Loans S.r.l.", Milano address, IT, contact email). |
| §1.4 Risk classification | Triggered rules table with both `name_en` and `name_it`. |
| §2.2 Models in use | The provider/model/version of the spans this demo just ingested. |
| §2.3 Retrieval sources | Five `kb://policy/*` URIs with citation counts and versions. |
| §3.3 Latency performance | p50/p95/p99 per 24h/7d/30d/all-time window. |
| Appendix A | Compliance gap analysis: which §s are auto-populated vs which still need provider input. |
| Appendix C | Sample evidence: the most recent span trace_ids — cross-reference these in the collector. |
| Appendix D | Sign-off block with signature lines. |

## Cleanup

```bash
docker compose down       # from project root, stops the collector
rm -rf out/               # remove generated docs
```

The seeded tenant + API key persist in the DB until you `docker
compose down -v` (drops the volume). To start fresh: `make db-reset`.
