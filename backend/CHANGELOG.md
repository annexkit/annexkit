# Changelog — `annexkit-backend`

All notable changes to the AnnexKit collector backend are documented
here. The backend is **AGPL-3.0** (see [`LICENSE`](LICENSE)) and
deployed via the project's [`docker-compose.yml`](../docker-compose.yml)
or directly from this directory's [`Dockerfile`](Dockerfile).

The backend is *not* published to a package manager — it ships as a
container image. Self-hosters track this changelog to know what
changed between commits they pulled.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning is [SemVer](https://semver.org/) — the first official tag
will be cut at launch (M1 of the roadmap). Until then, this changelog
groups changes by the day-of-MVP milestone they landed in.

## [Unreleased]

All work since the project started lives here until the first tag is
cut. If you self-host, you're tracking `main`; this section is your
release-notes-equivalent.

### Day 1 — Initial scaffolding

- Repository structure: `backend/` + `sdk/` + `frontend/` (added M3) +
  `examples/` + `docs/`.
- Regulatory invariants in place from the first commit:
  `risk_engine.py` deterministic classifier, `audit_log.py` model
  + INSERT-only service, `annex_iii.json` rule dataset, EU-hosted
  `mistral_client.py`, async SQLAlchemy 2.0 setup.
- FastAPI skeleton with `/health` + `/api/v1/ping`.
- Docker Compose dev stack (Postgres 16 + backend on port 8033).
- Async Alembic migration environment.

### Day 3 — Span ingest endpoint + auth + append-only audit log

- New ORM models: `Tenant`, `ApiKey` (HMAC-SHA256 hashed at rest),
  `Span` (one row per LLM invocation tracked by the SDK).
- `audit_log.py` model: append-only by service contract +
  Postgres trigger `annexkit_audit_logs_immutable` that raises on
  any UPDATE/DELETE at the DB layer.
- New endpoint `POST /api/v1/spans` — Bearer auth via
  `Authorization: Bearer ak_...`, validates with Pydantic strict
  schema, persists span + writes one audit log entry in the same
  transaction.
- New endpoint `GET /api/v1/ping` (versioned smoke test).
- Initial migration `0001_initial`: creates tenants + api_keys +
  audit_logs + spans + the APPEND-ONLY trigger (Postgres only;
  SQLite tests skip the trigger).
- 18 backend tests (in-memory SQLite via `aiosqlite` for hermetic
  CI without Docker).

### Day 1-3 audit pass — idempotency + DX hardening

- **Idempotent span ingest** (`uq_spans_tenant_trace_span` unique
  constraint via migration `0002_span_idempotency`): SDK retries
  no longer create duplicate rows. Service-level SELECT-then-INSERT
  + audit-log skip on duplicate.
- Auth dep folded into one JOIN (was 2 queries).
- New body-size middleware: 413 on Content-Length > 1 MiB.
- New request-id middleware: every response carries
  `X-Request-Id`.
- Structured INFO log on every span ingest (collector is no
  longer "blind").
- Lint clean (ruff): 11 issues fixed across backend and SDK.
- New Makefile targets: `make health`, `make seed`, `make smoke`.
- `scripts/seed_tenant.py` for dev tenant creation.
- `backend/uv.lock` committed for reproducibility.

### Day 4 — Risk classifier integration + AI Systems API

- New ORM model `AISystem`: per-tenant declaration of an AI
  system + classifier output. Unique on `(tenant_id, system_id)`.
- New service `risk_classifier.py`: thin wrapper over
  `risk_engine.classify` translating AnnexKit's declarative wire
  format (Annex III categories, prohibited rule ids, transparency
  trigger ids) into the engine's question→answer dict. Validates
  every cited id against `annex_iii.json`; raises typed errors on
  unknown ids.
- New service `ai_system_service.upsert(...)`: idempotent
  declaration with re-classification on every upsert. Audit log
  entries on create + update.
- New endpoints: `PUT /api/v1/systems` (upsert),
  `GET /api/v1/systems` (list), `GET /api/v1/systems/{system_id}`.
- `span_service.ingest` now resolves `risk_tier="auto"` from the
  declaration (when one exists for the tenant + system_id).
- Migration `0003_ai_systems` creates the table.
- +20 tests (39 total backend) covering classifier translation,
  upsert idempotency, list scoping, span-classification
  resolution.

### Day 5 — Annex IV generator (top-design audit-grade)

- New endpoint `GET /api/v1/systems/{system_id}/annex-iv?format=md|pdf`.
- Markdown + PDF rendering via Jinja2 + WeasyPrint.
- Bilingual EN/IT throughout (cover, headings, glossary,
  reasoning rule labels).
- 9 Annex IV sections + 4 appendices (compliance gap analysis,
  glossary, sample evidence span trace_ids, document control
  + sign-off block).
- New `provider_info` JSONB column on `ai_systems` for
  Annex IV §1(b)-(d) provider details (legal name, address,
  country, contact, system version, environment, validation
  methods, notes). Migration `0004_provider_info`.
- New `annex_iv_aggregator.py` service: percentile latencies
  (p50/p95/p99), windowed stats (24h/7d/30d/all-time), error
  breakdown by class, sample evidence (10 most recent spans),
  active/inactive flag, gap analysis (16 Annex IV requirements
  marked AUTO/PARTIAL/MANUAL).
- Audit log entry `annex_iv.generated` on every PDF/MD render
  (with document_id + format + request_id).

### Day 6 — End-to-end demo

(no backend changes — `examples/chatbot-openai/` exercises the
existing collector via the SDK)

### Day 7 — Launch readiness + public trust API + frontend + audit pass

- **Public trust-center API** (`/api/v1/trust/{slug}*`) — three
  endpoints with NO auth, slug-keyed:
  - `GET /api/v1/trust/{slug}` — overview
  - `GET /api/v1/trust/{slug}/systems` — list
  - `GET /api/v1/trust/{slug}/systems/{system_id}` — detail
- **Whitelist redaction** in `trust_service.py`: only
  `legal_name`, `address`, `country`, `authorised_representative`,
  `system_version`, `software_environment`,
  `hardware_environment` exposed publicly. `contact_email`,
  `validation_methods`, `notes` redacted.
- 7 trust-API tests pinning the redaction contract.
- AGPL-3.0 LICENSE file landed at `backend/LICENSE`.
- **Security hardening pass**:
  - `system_id` regex `^[A-Za-z0-9._-]+$` enforced on
    `IngestSpan` and `AISystemDeclaration` (closes path traversal
    in Content-Disposition, control-char injection in audit logs).
  - Failed auth now logs at WARN with reason category +
    `request_id` + client IP. Five reason classes:
    `missing_header`, `malformed_key`, `unknown_or_revoked_key`.
  - Trust API returns single opaque `{"detail": "Not found"}` for
    all 404 cases (closes differential-error tenant enumeration).
  - `scripts/seed_tenant.py` hard-guards against `ENV != "dev"`.
  - `span_service.ingest` catches `IntegrityError` on the unique
    constraint and re-fetches the row that won the race (closes
    TOCTOU between SELECT and INSERT under concurrent retries).
- **Cross-tenant isolation tests** (8 new tests in
  `test_cross_tenant_isolation.py`) — pinning the single most
  important contract for an EU compliance product:
  - Span POSTed by tenant A is owned by A regardless of payload
    spoofing.
  - Two tenants can declare the same `system_id`.
  - Tenant A cannot read/list/Annex-IV tenant B's systems.
  - Public trust pages don't cross-pollinate.
  - 404s are byte-identical (no info leak).
  - System-id charset enforcement rejects path traversal,
    spaces, quotes, NUL bytes.
- 64 backend tests passing + 1 PDF skipped on host (Cairo/Pango
  not installed).

## Roadmap (cut from this section into v0.2.0 when shipped)

Track [`docs/ANNEXKIT_PLAN.md`](../docs/ANNEXKIT_PLAN.md) §8 for
the full M2-M12 roadmap. Backend-relevant items:

- Mistral advisor for ambiguous declarations (Day 4.5)
- Rate limiting on `/api/v1/trust/*` via `slowapi`
- CRA SBOM module (reuse trust center for software bills of
  materials)
- Multi-region deploy + read replicas (M6+)
- SOC 2 Type I lite (via OpenStatus / similar) (M10)
- Public Annex IV download (redacted) at
  `/api/v1/trust/{slug}/systems/{id}/annex-iv` (M3)
