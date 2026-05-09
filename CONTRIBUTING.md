# Contributing to AnnexKit

Thank you for opening this file. AnnexKit is a young open-core project
and we welcome thoughtful PRs.

## Before you start

  1. Read [`AGENTS.md`](AGENTS.md) — it documents the seven
     non-negotiables (deterministic classifier, append-only audit log,
     EU residency, thin controllers/fat services, types everywhere,
     permanent disclaimer, privacy-by-default spans). PRs that
     contradict these are unlikely to land.
  2. Read [`docs/ANNEXKIT_PLAN.md`](docs/ANNEXKIT_PLAN.md) for the
     12-month strategy + roadmap. A PR that doesn't fit somewhere on
     that plan needs a strong "why now" in the description.
  3. Skim the [README](README.md) for setup. `make up && make demo-seed`
     gets you a working stack in two commands.

## Development setup

```bash
git clone https://github.com/annexkit/annexkit
cd annexkit
cp .env.example .env
make up                 # docker compose: db + backend + frontend
make demo-seed          # smoke-tests the full pipeline
```

Test suites:

```bash
make backend-test       # 56 tests, ~0.4s
make sdk-test           # 48 tests, ~0.05s
```

Lint:

```bash
make lint               # ruff across backend + sdk
```

The frontend doesn't yet have a test suite (planned for M2). Type
errors are caught by `next build` in the Docker build stage and by
`tsc --noEmit` if you have Node installed locally.

## Commit conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

  * `feat(scope): subject` — new functionality.
  * `fix(scope): subject` — bug fix.
  * `chore(scope): subject` — dependency bumps, tooling, refactors
    with no behaviour change.
  * `docs(scope): subject` — documentation only.

Scopes we use: `sdk`, `backend`, `frontend`, `examples`, `docs`,
`launch`, `ci`. New scopes are welcome if they don't overlap with an
existing one.

The commit body should answer **why** more than **what** — the diff
already tells the reader what changed. Two good rules:

  * Lead with the user-visible change: "Span ingest now idempotent on
    (tenant, trace, span)" beats "Add unique constraint to spans".
  * Mention rollback if non-trivial: "to undo, drop the unique index
    via migration 0002 downgrade".

## PR checklist

Before requesting review:

  - [ ] `make lint` passes (no ruff errors).
  - [ ] `make backend-test && make sdk-test` passes.
  - [ ] If you added a new endpoint: tests cover the happy path AND
        at least one auth-failure path.
  - [ ] If you added a new ORM column: a migration exists, both
        `upgrade()` and `downgrade()` are implemented, and the
        downgrade is tested by squashing + re-applying locally.
  - [ ] If you touched any public surface (SDK API, REST endpoint,
        trust page): the README quickstart still works.
  - [ ] If you wrote a new service / model / endpoint: it's mentioned
        in the relevant CHANGELOG (only the SDK has one today —
        backend + frontend get one when we cut their first release).

## Architecture rules of thumb

  * **Routes validate + dispatch, services do the work.** A route
    handler that opens a DB transaction or calls Mistral directly is
    a bug.
  * **`extra="forbid"` on every Pydantic schema** unless you have a
    specific reason (we use `extra="allow"` only on `ProviderInfo`
    because it's a free-form vendor field). New schemas without
    `extra=` get bounced.
  * **No `time.sleep`, no blocking HTTP** in the backend. Use
    `httpx.AsyncClient`, `asyncio.sleep`, etc.
  * **No `os.environ` reads outside `app/config.py` (backend) or
    `annexkit/config.py` (SDK).** Settings flow through one typed
    object so tests can override.

## What we won't merge

  * Adding US-only services for PII handling. EU residency is
    non-negotiable.
  * Lowering audit-log durability (e.g. moving `audit_logs` to a
    queue without WAL).
  * Anything that lets the deterministic classifier *declassify* a
    high-risk system based on LLM advice.
  * Removing the disclaimer from any UI surface that produces
    compliance output.

## Disclosure of security issues

See [`SECURITY.md`](SECURITY.md) — please don't open public issues
for vulnerabilities.

## License

By contributing you agree your contribution is licensed under the
license of the directory it lands in (`sdk/` is MIT, everything else
is AGPL-3.0). The `LICENSE` files at the project root + each subdir
are the source of truth.
