# AnnexKit

> EU AI Act compliance pipeline for developers.

AnnexKit turns runtime telemetry from your LLM-powered code into
audit-ready Annex IV technical documentation under
[Reg. (EU) 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
("AI Act"). One decorator on your inference call. The collector
classifies the AI system against the Annex III risk tiers, persists
an append-only audit log, and renders a PDF (Markdown also available)
that a customer's procurement team or an external auditor can ask
for.

```python
from annexkit import track

@track(
    system_id="loan-screener",
    risk_tier="auto",
    purpose="pre-screen credit applications",
)
def screen(applicant):
    return openai.chat.completions.create(...).choices[0].message.content
```

That is the entire user-side integration. Article 12 logging,
Article 11 + Annex IV documentation, Article 13 transparency
disclosures — all derive from the spans the SDK ships and the
declarations the tenant makes via `PUT /api/v1/systems`.

## Status

Pre-1.0 (`v0.1.x`). The SDK + collector + Annex IV generator + public
trust pages are operational and covered by ~115 tests across SDK and
backend. The hosted service at
[annexkit.dev](https://annexkit.dev) is in early access; the
self-host path is via `docker compose up`.

## Quickstart

### 1. Install the SDK

```bash
pip install annexkit
```

### 2. Decorate a function

```python
from annexkit import track

@track(system_id="my-system", purpose="describe what this AI does")
def call_llm(prompt: str) -> str:
    return openai.chat.completions.create(...).choices[0].message.content
```

Without an `ANNEXKIT_API_KEY` set, spans are written as JSON to
stderr — useful for local development. Set the env var to ship them
to the collector.

### 3. Run the demo

```bash
git clone https://github.com/annexkit/annexkit
cd annexkit
make up                # local stack: Postgres + collector + frontend
make demo-seed         # seed a tenant + run the loan-screener chatbot
```

When it finishes you will have an Annex IV PDF in
`examples/chatbot-openai/out/`.

## How it works

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR APPLICATION                                            │
│    @annexkit.track(...) on each LLM call                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  ANNEXKIT COLLECTOR  (FastAPI, Postgres 16, EU-hosted)       │
│   • Span ingest (privacy-by-default — SHA-256 of I/O)        │
│   • Annex III risk classifier (deterministic, never declass.)│
│   • Append-only audit log (Postgres trigger enforces)        │
│   • Annex IV generator (Markdown + PDF, bilingual EN/IT)     │
│   • Public trust page (slug-addressable, redacted)           │
└─────────────────────────────────────────────────────────────┘
```

Three architectural invariants:

1. **The classifier is deterministic.** Rules are driven by
   `backend/app/data/annex_iii.json`. LLM advisors (planned) can
   suggest categories but never lower a tier.
2. **The audit log is append-only.** A Postgres trigger raises on
   UPDATE or DELETE, plus the service layer never exposes mutation.
3. **Privacy by default.** Inputs and outputs are SHA-256 hashed
   before leaving the host. Plaintext is opt-in (lands at v0.2 with
   encryption-at-rest on the collector).

## Why this exists

The EU AI Act enters full force on **2 August 2026**. Every team
running an LLM in production needs Article 11 (technical
documentation), Article 12 (logging), Article 13 (transparency to
deployers), and Article 72 (post-market monitoring) evidence.

The current options force a choice between:

- **LLM observability** (LangSmith, Langfuse, Confident AI) — strong
  on tracing and evals; no AI Act mapping.
- **AI governance platforms** (Credo AI, Holistic AI, Saidot) —
  proper coverage; €100K+/year, enterprise sales-led, US-headquartered.
- **Manual** — engineers + lawyers reverse-engineering Annex IV from
  application logs, weeks per system.

AnnexKit fills the gap: developer-first, self-serve, EU-hosted,
sub-€100/month starting tier, open-core.

## Hosted vs self-hosted

The collector and trust-center frontend are open-source under
AGPL-3.0. You have two paths:

### Self-host

`docker compose up`. The repository ships a complete production
configuration (Postgres 16, FastAPI, Next.js trust center). You
operate it, you keep the data, you renew the SSL.

### Hosted at annexkit.dev

We operate the collector for you on EU infrastructure (Hetzner
Falkenstein), with EU-hosted LLM advisor (Mistral La Plateforme,
Paris). Pricing tiers cover 100K to unlimited spans per month with
1 to unlimited declared AI systems.

See [annexkit.dev/pricing](https://annexkit.dev/pricing) for current
tiers.

## Project layout

| Directory | Purpose | License |
|---|---|---|
| [`sdk/`](sdk/) | Python SDK published to PyPI as `annexkit`. | MIT |
| [`backend/`](backend/) | FastAPI collector + Annex IV API + trust API. | AGPL-3.0 |
| [`frontend/`](frontend/) | Next.js 16 trust-center pages. | AGPL-3.0 |
| [`examples/`](examples/) | Runnable end-to-end demos. | MIT |
| [`docs/`](docs/) | Reference documentation. | — |

[`AGENTS.md`](AGENTS.md) documents the project shape and the seven
architectural non-negotiables that PRs are reviewed against.

## Examples

Two end-to-end runnable scenarios:

- [`examples/chatbot-openai/`](examples/chatbot-openai/) — a single
  loan-screening chatbot demo with retrieval-augmented generation.
  Real OpenAI when `OPENAI_API_KEY` is set, deterministic stub
  otherwise.
- [`examples/test-walkthrough/`](examples/test-walkthrough/) — three
  paying-customer personas (Pro, Team, Enterprise) walked through
  declaration, span ingest, and Annex IV generation. Eight output
  files (4 PDFs + 4 Markdown).

Plus three minimal SDK-only examples in
[`sdk/examples/`](sdk/examples/) that print spans on stderr without
needing the collector running.

## Documentation

| Topic | Where |
|---|---|
| Project architecture + non-negotiables | [`AGENTS.md`](AGENTS.md) |
| Contributing guide | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Security policy + invariants | [`SECURITY.md`](SECURITY.md) |
| SDK API + quickstart | [`sdk/README.md`](sdk/README.md) |
| SDK changelog | [`sdk/CHANGELOG.md`](sdk/CHANGELOG.md) |
| Backend architecture | [`backend/README.md`](backend/README.md) |
| Backend changelog | [`backend/CHANGELOG.md`](backend/CHANGELOG.md) |
| Trust-center frontend | [`frontend/README.md`](frontend/README.md) |

## Roadmap

Shipped in `v0.1.x`:

- Span ingest API with HMAC-authenticated tenants
- Append-only audit log with Postgres trigger enforcement
- Deterministic Annex III risk classifier (rules + bilingual labels)
- Annex IV generator (Markdown + PDF, bilingual EN/IT, ~75 KB
  audit-grade output per system)
- Public trust pages with `provider_info` whitelist redaction
- Cross-tenant isolation tests
- Idempotent span ingest with TOCTOU race protection

Planned for `v0.2`:

- LangChain + LlamaIndex auto-instrumentation
- TypeScript / JavaScript SDK
- LLM advisor for ambiguous declarations (Mistral La Plateforme,
  hard guardrail: never declassifies)
- Span batching + retry on transient failure
- Trust badge embeddable into customer footers
- Customer dashboard + Stripe self-serve sign-up
- Rate limiting on public trust API

## Contributing

PRs are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for setup,
commit conventions, and the architecture rules of thumb. Security
reports: see [`SECURITY.md`](SECURITY.md).

## License

The repository is dual-licensed:

| Component | License | What it means |
|---|---|---|
| `sdk/` | **MIT** | Drop into any codebase; no copyleft. |
| `backend/` | **AGPL-3.0** | Self-host freely; if you expose modifications as a network service, publish your source. |
| `frontend/` | **AGPL-3.0** | Same as backend. |
| `examples/` | **MIT** | Same as the SDK they depend on. |

This is the same arrangement Sentry, PostHog, and MinIO use.
[`LICENSE`](LICENSE) at the root has the rationale.

## Disclaimer

AnnexKit is not a law firm. The Annex IV documents and risk
classifications it produces are technical artefacts; legal
interpretation is the responsibility of your legal team or external
counsel.
