# chatbot-anthropic — end-to-end AnnexKit demo (Anthropic Claude)

A CV pre-screening chatbot that walks through the **complete AnnexKit
loop** in one runnable script, with Anthropic Claude as the underlying
LLM:

1. Declare an AI system (high-risk, **Annex III §4 employment**).
2. Run a 5-turn candidate-screening conversation, with each turn
   instrumented via `annexkit.session(...)`.
3. Each invocation flows through the SDK → collector → Postgres,
   carrying SHA-256 hashes of input/output, model identifiers
   (`anthropic` / `claude-haiku-4-5` / `claude-haiku-4-5-20251001`),
   latency, user role.
4. Fetch the Annex IV technical documentation in Markdown + PDF —
   fully populated from the conversation that just happened.

By the end the script writes:

```
out/annex-iv-cv-screener-anthropic.md   (full bilingual document)
out/annex-iv-cv-screener-anthropic.pdf  (audit-grade PDF)
```

This is the sibling of [`../chatbot-openai/`](../chatbot-openai/). Same
shape, different LLM provider, different Annex III category. Run both
to see how AnnexKit handles multiple regulated AI systems in one tenant.

## Prerequisites

You need:
- The AnnexKit collector running (persists spans + generates Annex IV)
- A tenant API key the demo will use
- An Anthropic API key

From the **project root**:

```bash
make up           # start Postgres + collector
make seed         # mint a test tenant + print its api_key
```

Copy the `api_key=ak_...` line.

## Configure

```bash
cd examples/chatbot-anthropic
cp .env.example .env
```

Edit `.env`:

```
ANNEXKIT_API_KEY=ak_xxx       # from `make seed`
ANTHROPIC_API_KEY=sk-ant-xxx  # from https://console.anthropic.com/
```

## Run

```bash
uv sync                    # installs annexkit (local SDK), anthropic, httpx, dotenv
uv run python chatbot.py
```

You'll see something like:

```text
AnnexKit demo - chatbot-anthropic
===================================
Collector: http://localhost:8033
LLM:       Anthropic claude-haiku-4-5-20251001
API key:   ak_9g744qph*** (suffix hidden)

--- Step 1/4: Declare AI system -----------------------------
  System ID:        cv-screener-anthropic
  Risk tier:        HIGH
  Rules version:    1.0.0
  Triggered rules:
    - annex3_4_employment       (Annex III, §4)
    - art50_chat_interaction    (Article 50)

--- Step 2/4: Run conversation ------------------------------

  [1/5] >>> Candidate A: 5 years Python at a Milan SaaS...
        <<< I am an AI assistant. Fit: strong fit for senior backend...
  [2/5] >>> Candidate B: 8 years Java enterprise...
        <<< I am an AI assistant. Fit: borderline — strong enterprise...
  ...

--- Step 3/4: Fetch Annex IV (markdown) ---------------------
  Saved 8,247 bytes to .../out/annex-iv-cv-screener-anthropic.md

--- Step 4/4: Fetch Annex IV (PDF) --------------------------
  Saved 73,041 bytes to .../out/annex-iv-cv-screener-anthropic.pdf

----------------------------------------------------------------
Demo complete.
  Markdown: .../out/annex-iv-cv-screener-anthropic.md
  PDF:      .../out/annex-iv-cv-screener-anthropic.pdf
```

## What's actually instrumented

The `screen_candidate()` function uses
[`annexkit.session(...)`](../../sdk/annexkit/session.py) so it can
attach `model_provider` / `model_name` / `model_version` to the span —
those are the fields that show up in Annex IV §2.2 "Models in use".

```python
def screen_candidate(user_message, history):
    with annexkit.session(
        system_id="cv-screener-anthropic",
        risk_tier="auto",
        purpose=DECLARATION["purpose"],
    ) as span:
        span.set_input(user_message)
        span.set_user_role("recruiter")

        reply = llm_call(user_message, history)  # calls Claude

        span.set_model(
            provider="anthropic",
            name="claude-haiku-4-5",
            version="claude-haiku-4-5-20251001",
        )
        span.set_output(reply)
        span.add_metadata(history_turns=len(history) // 2)
        return reply
```

The Anthropic-specific bit is small:

```python
from anthropic import Anthropic

def llm_call(user_message, history):
    client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[*history, {"role": "user", "content": user_message}],
        temperature=0.2,
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()
```

Privacy-by-default: the actual prompt + response are SHA-256 hashed
before they leave your host. The collector never sees plaintext.

## What to look at in the generated Annex IV

The PDF is the headline output. Things to spot:

| Section | What you'll see |
|---|---|
| Cover page | **HIGH RISK** badge. |
| Executive summary | Auto-generated paragraph naming the system, the tier, the invocation count (5), the error rate (0%), the active status. |
| §1.2 Persons responsible | TopTalent S.r.l., Milano address, IT country, contact email. |
| §1.4 Risk classification | Triggered rules table — `annex3_4_employment` + `art50_chat_interaction`. |
| §2.2 Models in use | `anthropic / claude-haiku-4-5 / claude-haiku-4-5-20251001` × 5 invocations. |
| §3.3 Latency performance | Real p50/p95/p99 from the 5 Claude calls. |
| Appendix A | Compliance gap analysis: §1.2 / §1.3 / §2.4 should be `auto`, §6 / §7 / §9 still `manual`. |
| Appendix C | 5 sample trace_ids — cross-reference in the collector. |

## OpenAI vs Anthropic comparison

Run both demos against the same tenant:

```bash
cd examples/chatbot-openai && uv run python chatbot.py
cd ../chatbot-anthropic    && uv run python chatbot.py
```

Then in the trust API:

```bash
curl http://localhost:8033/api/v1/trust/dev-xxx/systems | jq
```

You'll see **two** declared AI systems for the same tenant —
`loan-screener-bot` (OpenAI, Annex III §5) and `cv-screener-anthropic`
(Anthropic, Annex III §4). That's the multi-system world a real
provider would inhabit.

## Cleanup

```bash
docker compose down       # stops the collector
rm -rf out/               # remove generated docs
```

The seeded tenant + API key persist in the DB until you
`docker compose down -v` (drops the volume). To start fresh:
`make db-reset`.
