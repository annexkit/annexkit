# AUDIT — AnnexKit v0.1.x

> CTO-level technical audit. Read sections in order: Verdict → Findings → Detail.
> Date: 2026-05-23. Auditor: Claude Code (Opus 4.7).
> Scope: SDK (`sdk/`), backend (`backend/`), tests, migrations, infra-as-code in repo.
> Out of scope: frontend Next.js code (audit separately), live prod VPS.

---

## 0. Verdict

**The code is genuinely good.** Better than 90% of pre-1.0 SaaS codebases I've reviewed.
The 7 non-negotiables in `AGENTS.md` are encoded in code, not aspiration. Defence-in-depth is
real (3 layers on append-only audit log, 2 layers on cross-tenant isolation, constant-time
HMAC on auth, strict Pydantic everywhere). Test coverage is ~115 tests against ~4700 LOC
source — a healthy ratio with the right tests targeting the right invariants.

Three things to fix before scaling user count:
- **P1 SDK default points at a nonexistent host** (`collector.annexkit.dev` — see #F1)
- **P1 no rate limiting on public trust endpoints** (DOS-able, easy fix — #F2)
- **P1 audit-log Postgres trigger only verified live** (no CI smoke against real Postgres — #F3)

Plus a handful of P2 nice-to-haves. No P0 (zero shipstoppers).

---

## 1. Findings table

| # | Sev | Area | Title | File:line |
|---|---|---|---|---|
| F1 | **P1** | SDK | Default `collector_url` resolves to nonexistent host | [sdk/annexkit/config.py:29](sdk/annexkit/config.py#L29) |
| F2 | **P1** | Backend | No rate limiting on `/api/v1/trust/*` (no-auth, public) | [backend/app/api/trust.py](backend/app/api/trust.py), [backend/app/main.py:191](backend/app/main.py#L191) |
| F3 | **P1** | Tests | Postgres trigger `annexkit_audit_logs_immutable` only verified live, not in CI | [backend/tests/conftest.py:47](backend/tests/conftest.py#L47), [backend/alembic/versions/2026_05_07_1200_0001_initial.py:186](backend/alembic/versions/2026_05_07_1200_0001_initial.py#L186) |
| F4 | P2 | Backend | `app_version` hardcoded to `"0.1.0"` in `config.py` — not env-overridable | [backend/app/config.py:29](backend/app/config.py#L29) |
| F5 | P2 | SDK | Sync `@track` blocks function return on exporter HTTP call (5s timeout) | [sdk/annexkit/decorator.py:127](sdk/annexkit/decorator.py#L127), [sdk/annexkit/exporters/http.py:35](sdk/annexkit/exporters/http.py#L35) |
| F6 | P2 | SDK | HTTP exporter has no retry / no batching → spans dropped on transient failure | [sdk/annexkit/exporters/http.py:59](sdk/annexkit/exporters/http.py#L59) |
| F7 | P2 | Backend | `BodySizeLimitMiddleware` trusts `Content-Length` header (no streamed-bytes cap) | [backend/app/main.py:131](backend/app/main.py#L131) |
| F8 | P2 | Backend | Annex IV aggregator loads ALL spans into Python memory (>1M = OOM risk) | [backend/app/services/annex_iv_aggregator.py:113](backend/app/services/annex_iv_aggregator.py#L113) |
| F9 | P2 | Backend | Auth failure logs `client.host` directly — spoofable via `X-Forwarded-For` if reverse-proxy not enforced | [backend/app/api/auth.py:56](backend/app/api/auth.py#L56) |
| F10 | P2 | Backend | `RealMistralClient` module-global without lock (lazy init via `get_mistral`) | [backend/app/services/mistral_client.py:160](backend/app/services/mistral_client.py#L160) |
| F11 | P2 | Backend | CORS `allow_methods=["*"]` + `allow_headers=["*"]` is broad | [backend/app/main.py:194](backend/app/main.py#L194) |
| F12 | P2 | Backend | No DB connection-pool tuning (defaults 5+10, OK now, hits ceiling at ~100 concurrent) | [backend/app/database.py:31](backend/app/database.py#L31) |
| F13 | P2 | Backend | `annex_iii.json` rules have `description_it` but no `description_en` — PDF EN-only mode will be impoverished | [backend/app/data/annex_iii.json](backend/app/data/annex_iii.json) |
| F14 | P3 | Backend | No backup automation (runbook §6 TODO). Audit-grade product without scheduled `pg_dump` is risky | (infra) |
| F15 | P3 | Repo | `docker-compose.prod.yml` lives only on VPS — single point of failure (will be fixed by task 0.4a) | (missing file) |
| F16 | P3 | Backend | No `frontend` test suite (per AGENTS.md trade-off table) — Vitest in M3 | [frontend/](frontend/) |

---

## 2. The seven non-negotiables — verified against code

| # | Non-negotiable | Verdict | Evidence |
|---|---|---|---|
| 1 | Risk Engine is deterministic, never declassifies | ✅ **VERIFIED** | [risk_engine.py:81](backend/app/services/risk_engine.py#L81) — pure Python, frozen `Verdict`, strict precedence ladder returns immediately on first hit. No `else` path can downgrade. Tests in [test_risk_classifier.py](backend/tests/test_risk_classifier.py). |
| 2 | Audit log is append-only | ✅ **VERIFIED, 3 layers** | (a) [audit_service.py](backend/app/services/audit_service.py) exposes only `record()` — pinned by [test_audit_service_contract.py:28](backend/tests/test_audit_service_contract.py#L28). (b) No repository / service exposes update/delete. (c) Postgres trigger [`annexkit_audit_logs_immutable`](backend/alembic/versions/2026_05_07_1200_0001_initial.py#L186) raises on UPDATE/DELETE. Caveat: see **F3** — trigger not exercised in CI. |
| 3 | EU data residency | ✅ **VERIFIED (config)** | [config.py:58](backend/app/config.py#L58) Mistral La Plateforme (Paris) for advisor. Hetzner Falkenstein per runbook §0. No US-hosted call paths in code. Code-side trust is correct; live-side trust is operational (runbook §0). |
| 4 | Thin controllers, fat services | ✅ **VERIFIED** | All routes [api/](backend/app/api/) are ≤140 lines; all dispatch to [services/](backend/app/services/). Spot-checked [spans.py:43](backend/app/api/spans.py#L43) (5 lines of logic) and [systems.py:47](backend/app/api/systems.py#L47) (10 lines). |
| 5 | Types on everything (`from __future__ import annotations`) | ✅ **VERIFIED** | Every file inspected has it. Mapped columns use SQLAlchemy 2.0 `Mapped[...]`. Pydantic models with `extra="forbid"`. |
| 6 | Disclaimer permanent | ✅ **VERIFIED** | [annex_iv.md.jinja:32](backend/app/templates/annex_iv.md.jinja#L32) bilingual disclaimer at top of every PDF. README/AGENTS/SECURITY repeat. Trust API docstring also notes it. |
| 7 | Privacy-by-default in spans (SHA-256 hash) | ✅ **VERIFIED** | [_hashing.py](sdk/annexkit/_hashing.py) SHA-256 hex with deterministic JSON serialisation. [decorator.py:174-175](sdk/annexkit/decorator.py#L174) hashes both input and output before span construction. Plaintext logging is documented as v0.2 opt-in — not vapor, intentional deferral. |

---

## 3. Detail — P1 findings

### F1 — SDK default `collector_url` resolves to nonexistent host (P1)

**File**: [sdk/annexkit/config.py:29](sdk/annexkit/config.py#L29)
```python
DEFAULT_COLLECTOR_URL = "https://collector.annexkit.dev"
```

**Problem**: The runbook §2.2 shows the actual live Cloudflare DNS records as `A @` and `A www` for `annexkit.dev` only — no `collector` CNAME / A record. Caddy proxies based on `annexkit.dev`/`www.annexkit.dev` (Caddyfile §2.5 in runbook), not `collector.*`. So out-of-the-box:

```bash
pip install annexkit
export ANNEXKIT_API_KEY=ak_xxx
# decorator runs → HTTP exporter POSTs to https://collector.annexkit.dev/api/v1/spans
# → DNS resolution fails / Cloudflare 404
```

Users must override `ANNEXKIT_COLLECTOR_URL=https://annexkit.dev` for the SDK to talk to the
hosted collector. This breaks the "pip install + decorator = done" demo flow used in the
README and `COSA_E_ANNEXKIT.md` Mario story.

**Fix options** (pick one):
1. Add `collector.annexkit.dev` CNAME → `annexkit.dev` on Cloudflare and a Caddyfile block
   (cleanest — preserves "collector" subdomain as the canonical SDK endpoint, leaves
   `annexkit.dev` free for marketing/trust).
2. Change `DEFAULT_COLLECTOR_URL` to `"https://annexkit.dev"` and bump SDK to 0.1.1 (faster
   but ties SDK endpoint to the marketing host forever).

**Recommendation**: Option 1. Update DNS + Caddy first, leave SDK default as-is. Verify with
`curl https://collector.annexkit.dev/health` returns 200 before merging.

### F2 — No rate limiting on public trust endpoints (P1)

**Files**: [backend/app/api/trust.py](backend/app/api/trust.py) (no rate limit), [backend/app/main.py:191](backend/app/main.py#L191) (no rate-limit middleware mounted)

**Problem**: `/api/v1/trust/{slug}`, `/{slug}/systems`, `/{slug}/systems/{system_id}` are intentionally unauthenticated (slug = public URL). Without rate limiting, a single attacker can:
- DOS the public trust page (each request does 1–N indexed Postgres queries)
- Enumerate slugs via timing (mitigated by opaque 404, but still)
- Burn Hetzner CPU budget at low cost

The roadmap in [AGENTS.md / README "Planned for v0.2"] and runbook §6 both list rate limiting as TODO. **It should be P1 done before any marketing push**, not v0.2 — the moment HN traffic lands on a trust page, this is exposed.

**Fix**: Add `slowapi` (FastAPI-friendly Flask-Limiter clone). 60 req/min per IP on trust endpoints is sane. Single PR, ~20 LOC.

```python
# main.py
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# trust.py decorators
@router.get("/{slug}")
@limiter.limit("60/minute")
async def get_overview(...): ...
```

Cloudflare provides a coarse fallback (their default rate limit is ~10K req/5min/IP), but per-endpoint app-layer limit is the right place.

### F3 — Postgres append-only trigger not exercised in CI (P1)

**Files**: [backend/tests/conftest.py:47](backend/tests/conftest.py#L47) (SQLite in-memory), [backend/alembic/versions/2026_05_07_1200_0001_initial.py:186](backend/alembic/versions/2026_05_07_1200_0001_initial.py#L186) (trigger skipped on SQLite)

**Problem**: The Postgres trigger `annexkit_audit_logs_immutable` is the third (and only DB-layer) defence of the append-only invariant. But:
- Tests use SQLite in-memory (good for speed, fine for service-layer contracts).
- The trigger creation is guarded by `if is_postgres` in the migration.
- Therefore: **no CI check ever runs `UPDATE audit_logs SET ...` against real Postgres to verify the trigger raises**.

If someone accidentally drops the trigger creation in a future migration, or a Postgres version change breaks PL/pgSQL syntax, CI is silent. The audit-service contract tests catch service-layer regressions (great) but not DB-layer regressions.

**Fix**: Add a single Postgres-integration test that spins up `testcontainers-python` Postgres, runs migrations, then asserts `UPDATE audit_logs ...` raises and `DELETE FROM audit_logs ...` raises. ~50 LOC, ~10s CI overhead. Skip with `pytest -m "not pg_integration"` for local fast loop.

```python
# tests/test_audit_trigger_postgres.py
@pytest.mark.pg_integration
async def test_audit_trigger_rejects_update():
    # uses testcontainers postgres + migrations
    with pytest.raises(asyncpg.PostgresError, match="append-only"):
        await pg.execute("UPDATE audit_logs SET action='tampered' WHERE id=1")
```

---

## 4. Detail — P2 findings (briefer)

- **F4** `app_version` hardcoded — should read `os.getenv("APP_VERSION", "0.1.0")` so Konformia-style `APP_VERSION=0.1.0+sha-stamp` from `make prod-deploy` propagates into `/health`. Fixes during task 0.4b.
- **F5** Sync `@track` exporter blocks return — add a thread-pool exporter in v0.2 (background daemon thread + queue). Workaround for users today: call `annexkit.configure(disabled=True)` in test runs.
- **F6** No retry / no batching — known v0.2 work, documented. Spans dropped silently on network blip = audit-trail holes. Mitigation: bump exporter timeout to 10s and add 1 retry, ~15 LOC.
- **F7** `Content-Length` trust — uvicorn caps streamed bytes via `--limit-max-request-size` but the AnnexKit Dockerfile doesn't set it. Add `--limit-max-request-size 2097152` to the uvicorn command. Belt-and-braces.
- **F8** Aggregator OOM at >1M spans — documented in [annex_iv_aggregator.py:23-25](backend/app/services/annex_iv_aggregator.py#L23). M2 plan: materialised view. For now, add a hard cap: `LIMIT 100_000` + warning log if hit. Better than OOM.
- **F9** `client.host` spoofing — only matters if Caddy passes through untrusted `X-Forwarded-For`. Cloudflare → Caddy → backend already strips this (Cloudflare sets `CF-Connecting-IP`). For belt-and-braces, switch to FastAPI's `request.client.host` after configuring uvicorn `--forwarded-allow-ips` properly.
- **F10** Mistral client global without lock — FastAPI workers are async single-thread per process, so the race window is the import-time `_real_client = None` → first request lazy init. Negligible in practice. Add a `threading.Lock()` if multi-threaded workers ever ship.
- **F11** Broad CORS — `allow_origins=settings.cors_origins` is correctly hardened, but `allow_methods=["*"]` could be narrowed to `["GET", "POST", "PUT"]` and `allow_headers=["*"]` to `["Authorization", "Content-Type", "X-Request-Id"]`. Minor.
- **F12** Pool sizing — at ~50 active customers (estimate per MONETIZZAZIONE.md M9) with ~10 req/sec each, you'll saturate the default pool. Bump to `pool_size=20, max_overflow=20` in `create_async_engine`.
- **F13** Missing `description_en` — when v0.2 multilingual lands (per `AnnexKit-v0.2-Multilang-Plan.md`), the English single-language PDF will fall back to just `name_en` without the longer description. Plan PR: add `description_en` to all rules in `annex_iii.json`. One-evening translation pass.

---

## 5. What's NOT a bug but worth noting

- **Wire `metadata` → ORM `extras` rename** ([span_service.py:108](backend/app/services/span_service.py#L108)) is well-documented — `Base.metadata` SQLAlchemy collision. Keep the comment near the rename forever.
- **`StrictUndefined` in Jinja** ([annex_iv_renderer.py:30](backend/app/services/annex_iv_renderer.py#L30)) is the right call for an audit-grade doc — silent empty strings would be a quality regression bug.
- **API key prefix design** ([api_key.py](backend/app/services/api_key.py)) — base32-ish alphabet excludes ambiguous chars (`0/O`, `1/l/I`), 120 bits of entropy, HMAC not bcrypt with the rationale documented. Textbook.
- **Cross-tenant isolation tests** ([test_cross_tenant_isolation.py](backend/tests/test_cross_tenant_isolation.py)) — 8 tests including opaque-404 differential, path-traversal `system_id` rejection. This is the kind of test most pre-1.0 products skip.
- **`expire_on_commit=False` + Python-side defaults on `updated_at`** ([common.py:70-77](backend/app/models/common.py#L70)) — the comment explains the MissingGreenlet bug they hit. Without this, async routes mutating-then-returning an ORM row break.
- **`down_revision` chain is clean** — 0001 → 0002 → 0003 → 0004 with separate migrations per logical change. No squashing of unrelated migrations.
- **Idempotent span ingest with TOCTOU race protection** ([span_service.py:115](backend/app/services/span_service.py#L115)) — `IntegrityError` rescue with rollback + re-fetch. Production-grade.

---

## 6. Recommendations — prioritised

**Before the next batch of marketing pushes** (P1, ~1 day total):
1. Fix F1 (DNS + Caddy for `collector.annexkit.dev`) — 30 min
2. Fix F2 (rate limit trust endpoints) — 2h
3. Fix F3 (CI Postgres trigger test) — 2h

**Before the first paid customer goes live** (P2, ~2 days total):
4. F4 (`APP_VERSION` env override) — bundled in task 0.4b
5. F6 (HTTP exporter 1 retry + 10s timeout) — 1h
6. F8 (aggregator hard cap + warning) — 1h
7. F12 (DB pool size 20+20) — 5 min
8. F14 (automated backups — cron + offsite) — 2h
9. F7 (uvicorn `--limit-max-request-size`) — 5 min

**Before pushing past 50 paying customers** (P3, ongoing):
10. F5 (async exporter in v0.2)
11. F13 (`description_en` translations)
12. F16 (frontend Vitest)

---

## 7. Code-quality signal

What I look for and what I found:

| Signal | Verdict |
|---|---|
| Comments explain WHY, not WHAT | ✅ Excellent — every non-obvious choice has a "Why:" paragraph |
| Tests pin invariants, not implementations | ✅ `test_audit_service_contract.py` introspects module namespace; `test_cross_tenant_isolation.py` pins the contract not the SQL |
| Errors are typed (custom exception classes) | ✅ `MistralNotConfiguredError`, `UnknownAnnexIIICategoryError`, etc. mapped to 422/503 at route layer |
| Service boundaries are clean | ✅ No route handler touches DB directly; no service writes audit log via raw SQL |
| Async correctness | ✅ No `time.sleep`, all `httpx` async or `asyncio.to_thread`, no blocking calls on the event loop |
| Migration discipline | ✅ One change per migration, no `--autogenerate` slop, each migration has rationale in docstring |
| Production hardening | ✅ Fail-fast on insecure `SECRET_KEY` / CORS at startup |
| Defence in depth | ✅ Auth = constant-time HMAC + indexed JOIN + revocation; audit-log = service + no API + Postgres trigger |
| Documentation of what's NOT yet done | ✅ Every deferral has a milestone (M2, M3, M4...) — no silent gaps |

---

_End of audit. Next deliverable: the anti-vapor audit (claim vs code) — see `ANTI_VAPOR.md` when generated._
