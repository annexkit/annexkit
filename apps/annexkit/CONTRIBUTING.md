# Contributing to AnnexKit

Thanks for opening this file. AnnexKit is open-core EU AI Act compliance
infrastructure — the kind of project that benefits enormously from extra
eyes on regulatory edge cases, security primitives, and developer
ergonomics.

A PR doesn't need to be large to be useful. Typo fixes, a clearer
docstring, a test that hardens an existing service, an annotation in the
risk classifier — all welcome.

---

## What AnnexKit is, in 30 seconds

A Python SDK + FastAPI collector + Next.js trust center that turns
runtime LLM telemetry into audit-ready
[Annex IV](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
technical documentation under EU Reg. 2024/1689. Developer-first,
EU-hosted, open-core. The deep dive is in [`README.md`](README.md);
the architectural commitments are in [`AGENTS.md`](AGENTS.md). Read
**AGENTS.md before opening a non-trivial PR** — it documents seven
non-negotiables that reviewers enforce.

## Repository layout

| Path | What lives here | License |
|---|---|---|
| [`sdk/`](sdk/) | Python SDK published on PyPI as `annexkit` | MIT |
| [`backend/`](backend/) | FastAPI collector + Annex IV PDF generator | AGPL-3.0 |
| [`frontend/`](frontend/) | Next.js 16 public trust center | AGPL-3.0 |
| [`examples/`](examples/) | Runnable end-to-end demos | MIT |
| [`scripts/`](scripts/) | Operational scripts (tenant seeding, etc.) | — |

---

## Quickstart for contributors

From `git clone` to a working stack in under 2 minutes:

```bash
git clone https://github.com/annexkit/annexkit
cd annexkit
cp .env.example .env
make up                  # docker compose: db + backend + frontend
make demo-seed           # smoke test — seeds a tenant + generates a PDF
```

When `make demo-seed` finishes, you'll have:

- Postgres 16 + pgvector running on `localhost:5438`
- FastAPI collector on `http://localhost:8033` ([Swagger](http://localhost:8033/docs))
- Next.js trust center on `http://localhost:3000`
- An Annex IV PDF in `examples/chatbot-openai/out/`

`make help` lists every command. Common ones: `make logs`, `make
db-shell`, `make restart`, `make smoke`.

---

## Tooling

| Layer | Tool | Why |
|---|---|---|
| **Python deps** | [uv](https://github.com/astral-sh/uv) | Fast, reproducible, lockfile-first |
| **Python lint + format** | [Ruff](https://docs.astral.sh/ruff/) | One tool replaces black + isort + flake8 |
| **Python tests** | [pytest](https://docs.pytest.org/) | Async support via `pytest-asyncio` |
| **Schema migrations** | [Alembic](https://alembic.sqlalchemy.org/) | Async-aware, autogenerate-friendly |
| **JS deps** | [npm](https://docs.npmjs.com/) with `package-lock.json` | Standard for the Next.js ecosystem |
| **JS lint** | ESLint via Next.js config | Catches React + a11y issues at build |
| **JS types** | TypeScript strict mode | `npm run typecheck` |
| **Containers** | Docker Compose | Identical dev + prod stack shape |
| **CI** | GitHub Actions (`.github/workflows/ci.yml`) | Lint + test + typecheck on every PR |

You don't need any of these installed on the host for the demo —
`make up` handles it inside Docker. For local TDD without rebuilding
the image:

```bash
cd backend && uv sync && uv run pytest -v
cd sdk     && uv sync && uv run pytest -v
cd frontend && npm install && npm run typecheck && npm run build
```

---

## Running tests + lint locally

```bash
# Backend — 66 tests, ~1s
make backend-test

# SDK — 48 tests, ~0.05s
make sdk-test

# Lint + format-check (both subprojects)
make lint
```

The frontend doesn't yet have a unit-test suite. Type errors are caught
by `npm run typecheck` and `next build` — both run in CI.

To auto-format Python before committing:

```bash
make fmt   # ruff format on backend + sdk
```

---

## What CI enforces

Every push to `main` and every pull request runs three jobs:

1. **SDK · Python** — `uv sync --frozen`, `ruff check`, `ruff format --check`, `pytest`
2. **Backend · FastAPI** — same as SDK plus a real `pgvector/pgvector:pg16` service container, `alembic upgrade head`, full pytest suite
3. **Frontend · Next.js** — `npm ci`, `npm run typecheck`, `npm run build`

A PR cannot merge with red CI. The workflow file is
[`.github/workflows/ci.yml`](.github/workflows/ci.yml); the PR template
is [`.github/pull_request_template.md`](.github/pull_request_template.md)
and is auto-applied when you open a PR.

---

## The seven non-negotiables

Reviewers reject PRs that violate any of these. The reasoning lives in
[`AGENTS.md`](AGENTS.md); the short form:

1. **Deterministic risk classifier.** Rules in `annex_iii.json`. LLM
   advisors may suggest categories on ambiguous inputs; they may never
   lower a tier the rules raised.
2. **Append-only audit log.** Postgres `TRIGGER` on `audit_logs`
   rejects `UPDATE` / `DELETE`. The service layer must never expose
   mutation.
3. **EU data residency.** Hetzner (Falkenstein / Helsinki) for hosting,
   Mistral (Paris) for any LLM advisor calls. No US-only services
   touch PII or telemetry payloads.
4. **Thin controllers, fat services.** Route handlers validate and
   dispatch; business logic lives in `app/services/`.
5. **Types on everything.** `from __future__ import annotations` +
   full hints in Python; `strict: true` in TypeScript.
6. **Permanent disclaimer.** Every UI surface that produces compliance
   output displays *"AnnexKit is not a law firm / AnnexKit non è uno
   studio legale"*.
7. **Privacy by default.** The SDK SHA-256-hashes inputs and outputs
   before they leave the host. Plaintext retention is opt-in per AI
   system and (when shipped) encrypted at rest.

---

## Commit conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(sdk): add async session manager
fix(backend): handle empty system_id in PUT /api/v1/systems
chore(ci): pin actions/checkout to v4.2
docs(readme): clarify hosted vs self-host pricing
perf(frontend): defer non-critical font load
```

**Scopes** in use today: `sdk`, `backend`, `frontend`, `examples`,
`scripts`, `ci`, `docs`, `brand`. New scopes are welcome if they
don't overlap.

**Commit message body** should answer **why**, not what (the diff
already shows what). Two rules of thumb:

- Lead with the user-visible change. "Span ingest is now idempotent
  on `(tenant, trace, span)`" beats "Add unique constraint".
- Mention the rollback path if non-trivial. "To undo: drop the unique
  index via migration 0002 downgrade".

History is rewritten only for the **most recent unpublished commits**
(amend, interactive rebase before push). Once on `main`, history is
immutable.

---

## PR checklist

Before requesting review:

- [ ] `make lint` passes locally
- [ ] `make backend-test && make sdk-test` passes locally
- [ ] If you added a new HTTP endpoint: tests cover the happy path
      and at least one auth-failure path
- [ ] If you added a new ORM column: an Alembic migration exists with
      both `upgrade()` and `downgrade()` implemented
- [ ] If you touched a public surface (SDK API, REST endpoint, trust
      page, Annex IV PDF template): the demo (`make demo-seed`) still
      runs end-to-end
- [ ] If user-facing: the relevant `CHANGELOG.md` has an entry
      (`sdk/CHANGELOG.md` or `backend/CHANGELOG.md`)
- [ ] The permanent disclaimer is untouched (or the change is approved
      separately)
- [ ] None of the seven non-negotiables above are weakened

The PR template prompts for these explicitly.

---

## What we won't merge

- **Anything that lowers audit-log durability** (e.g. moving
  `audit_logs` to an in-memory queue without WAL persistence).
- **Anything that lets the classifier declassify a high-risk system
  based on LLM advice.** Advisors suggest; they don't decide.
- **US-only services for PII or telemetry handling.** EU residency is
  not a soft preference — it's part of the value proposition.
- **Removing the disclaimer** from any UI surface that produces
  compliance output.
- **Skipping git hooks** (`--no-verify`), **bypassing migrations**, or
  **force-pushing to `main`** (history rewrites happen on a feature
  branch, then merge with `--ff-only`).

---

## Areas where help is especially welcome

If you're looking for something concrete to work on, these are real
needs ranked by impact-per-effort:

- **TypeScript / JavaScript SDK** (`@annexkit/node`). Same wire format
  as the Python SDK, same env-var conventions. Unlocks Next.js / Express
  / Cloudflare Workers users.
- **LangChain + LlamaIndex auto-instrumentation**.
  `annexkit.auto_instrument(["langchain"])` should wrap `LLMChain.run`
  and equivalents without manual `@track` decoration.
- **OpenTelemetry GenAI semconv compliance.** Emit OTel-native spans
  alongside the AnnexKit-specific extensions so a single collector can
  feed both pipelines.
- **Span batching + retry** in the HTTP exporter (`sdk/annexkit/exporters/http.py`).
  Currently each span POSTs synchronously; under high-frequency systems
  this is wasteful.
- **Bilingual (EN/IT) test coverage for the Annex IV renderer**.
  Catching a rendering regression in IT-only would matter.
- **Trust-page accessibility audit.** A WCAG AA pass against
  `/trust/[slug]` would land cleanly.

For each of these, an issue describing your approach before opening a
PR helps avoid wasted work.

---

## Disclosure of security issues

See [`SECURITY.md`](SECURITY.md). **Please don't open public issues**
for vulnerabilities — email <security@annexkit.dev>.

---

## License

Contributions land under the license of the directory they live in:

| Directory | License |
|---|---|
| `sdk/`, `examples/` | MIT |
| `backend/`, `frontend/` | AGPL-3.0 |

The `LICENSE` file at the project root and at each subproject root is
the source of truth. By submitting a PR you confirm you have the
right to license the contribution under that file.

---

## A note about scope

This is early-access infrastructure. We're solo-maintained at the
time of writing, which means:

- PR review is best-effort within 3-5 working days
- Larger architectural proposals benefit from a GitHub issue first
- We say **no** more often than yes, especially to feature creep —
  AnnexKit deliberately doesn't try to be every compliance tool

That's not unfriendly; it's how a small project ships a tight product.
A "we don't merge this" reply usually comes with a "but here's where it
could live" suggestion.

Thanks for reading this far.
