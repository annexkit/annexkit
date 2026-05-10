# AnnexKit — Project brief

> Source of truth for anyone writing code on AnnexKit. Read this
> whole file before opening a PR. The conventions here are enforced
> in code review.

## What AnnexKit is

**EU AI Act compliance pipeline for developers.** SDK + collector + Annex IV
generator + public trust center.

A developer integrating LLMs into a product can:

1. Install the SDK (`pip install annexkit`) and instrument LLM calls with one
   decorator.
2. Stream telemetry (model id, prompt template, retrieval sources, output
   hash, user role, latency) to the AnnexKit collector.
3. Get every "AI system" automatically classified against the EU AI Act risk
   tiers (unacceptable / high / limited / minimal).
4. Auto-generate audit-ready Annex IV technical documentation as Markdown
   or PDF.
5. Publish a public trust center listing AI systems and their conformity
   evidence.

Target buyer: CTO / AI lead / ML engineer of an EU scaleup with LLMs in
production who must show AI Act conformity from **2 August 2026**. Not a
lawyer. Not a DPO. A developer.

## Product shape

- **Three-package monorepo** in one git repo, one deploy cadence:
  - `sdk/` — Python SDK (`annexkit`, MIT, PyPI)
  - `backend/` — FastAPI collector + Annex IV API (AGPL-3.0)
  - `frontend/` — Next.js 16 public trust center (AGPL-3.0)
  - `examples/chatbot-openai/` — end-to-end demo (MIT)
- **Backend**: Python 3.13 + FastAPI + SQLAlchemy 2.0 async + Postgres 16
  (pgvector reserved for prompt-template semantic matching later).
- **SDK**: Python 3.10+ (broad compatibility), Pydantic 2, httpx async transport.
- **Frontend**: Next.js 16 (App Router, Turbopack, React 19) + Tailwind 4.
  Server components only — no client islands yet.
- **Infra dev**: Docker Compose (db + backend + frontend).
- **Infra prod**: Hetzner VPS (Falkenstein), Docker Compose, Cloudflare in
  front.

## Non-negotiables

These encode hard-won regulatory + audit invariants. Do NOT relax them
without a documented PR.

1. **Risk Engine is deterministic.** Classification logic is rules driven
   by `backend/app/data/annex_iii.json`. LLMs only advise on ambiguous
   cases, never to *declassify* a system.
2. **Audit log is append-only.** No endpoint, no migration, no script that
   UPDATEs or DELETEs from `audit_logs`. Ever. A Postgres trigger enforces
   this at the DB level (installed by the initial migration).
3. **EU data residency.** Hosting in Falkenstein/Helsinki, LLM advisor via
   Mistral La Plateforme (Paris). No US-only services for PII or telemetry
   payloads.
4. **Thin controllers, fat services.** Route handlers validate + dispatch,
   nothing else. All business logic lives in `backend/app/services/`.
5. **Types on everything.** `from __future__ import annotations` + full
   type hints in Python.
6. **Disclaimer is permanent.** Every Annex IV PDF, trust center page,
   dashboard surface that gives compliance output must say
   "AnnexKit is not a law firm / AnnexKit non è uno studio legale".
7. **Privacy-by-default in spans.** Input/output content is **never**
   logged in plaintext by default. The SDK hashes inputs/outputs (SHA-256)
   before transport. Plaintext logging is opt-in per AI system, encrypted
   at rest.

## Architectural patterns

- **Pydantic schemas** for every request/response (`backend/app/schemas/`).
- **ORM models** never leave the service layer — convert to a Pydantic
  `Read` schema before returning from a route.
- **Async everywhere**. No `time.sleep`, no blocking HTTP. Use `httpx`
  async for external calls.
- **Dependencies via FastAPI `Depends()`** — pass `AsyncSession`,
  `Settings`, and the authenticated tenant this way so tests can override.

## Folder layout

```
AnnexKit/
├── README.md              Public-facing overview + quickstart
├── CLAUDE.md              You are here
├── Makefile               `make help` lists everything
├── docker-compose.yml     Dev stack (db + collector backend)
├── .env.example           Copy to `.env` before `make up`
├── docs/
│   └── ANNEXKIT_PLAN.md   Strategic plan + 12-month roadmap
├── sdk/                   Python SDK (publishable package `annexkit`)
└── backend/               FastAPI collector + Annex IV API
```

## Sprint plan

Driven by `docs/ANNEXKIT_PLAN.md` Section 7 (MVP Day 1-7) and Section 8
(12-month roadmap). Status tracked in `README.md` under **Roadmap**. Each
sprint checkpoint updates that section.

## Contracts you inherit

- Commits use **Conventional Commits**: `feat(sdk): add @track decorator`,
  `fix(backend): handle empty system_id`, `docs(plan): clarify M3 milestone`.
- PRs must run `make lint` + `make backend-test` + `make sdk-test` green
  before merge.
- Never skip git hooks (`--no-verify`) or bypass migrations.

## Useful entry points

- Health: `GET /health`
- Versioned ping: `GET /api/v1/ping`
- OpenAPI/Swagger: `http://localhost:8033/docs` once `make up` is running.
- SDK quickstart: see `sdk/README.md`.

