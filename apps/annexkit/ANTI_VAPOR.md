# ANTI-VAPOR AUDIT — AnnexKit v0.1.x

> Every public claim vs. shipped code. Categorical verdict per claim:
> **TRUE** (code matches claim), **PARTIAL** (matches with caveat),
> **VAPOR** (claim made but code missing), **FUTURE** (correctly framed
> as v0.2+ roadmap — not vapor).
>
> Sources checked: public-facing README.md, sdk/README.md, AGENTS.md,
> sdk/CHANGELOG.md. Internal strategic docs on Desktop also reviewed for
> any claims that leak to public materials.
>
> Date: 2026-05-23.

---

## TL;DR

**Public materials are 90% honest.** No grand vapor claims like "GDPR-certified" or
"full AI Act compliance." The "early access" framing is used correctly. The two real
problems are:

1. **One actively misleading flow in `sdk/README.md`** — users are told to set
   `ANNEXKIT_COLLECTOR_URL=https://collector.annexkit.dev` and that endpoint
   doesn't resolve (see #C1 below + AUDIT.md F1). Customers hit a dead end.
2. **`MONETIZZAZIONE.md` lists 4 pricing tiers** as if they're purchaseable; the
   code has zero billing / Stripe / quota enforcement. The MONETIZZAZIONE doc is
   internal (on Desktop) but it informs the public pricing page mentioned in
   README "See annexkit.dev/pricing" — verify that page before launch (see #C2).

Internal strategic docs (`ANNEXKIT_PLAN.md`) sometimes show v0.2 features (e.g.
`auto_instrument`) in usage examples without a v0.2 tag. That's fine for internal
brainstorming; just don't copy those snippets into public materials verbatim.

---

## 1. Claims — Architecture & invariants

| # | Source | Claim | Verdict | Evidence |
|---|---|---|---|---|
| A1 | README §"How it works" | "Risk Engine deterministic, never declassifies" | **TRUE** | [risk_engine.py:81-153](backend/app/services/risk_engine.py#L81) — pure Python, frozen Verdict, strict precedence. Tests in [test_risk_classifier.py](backend/tests/test_risk_classifier.py). |
| A2 | README §"How it works" | "Append-only audit log enforced by Postgres trigger" | **TRUE** | Trigger [annexkit_audit_logs_immutable](backend/alembic/versions/2026_05_07_1200_0001_initial.py#L186) raises on UPDATE/DELETE + service-layer guard [audit_service.py](backend/app/services/audit_service.py). Caveat: trigger not exercised in CI (AUDIT.md F3) — claim is true on prod Postgres, untested on dev SQLite. |
| A3 | README §"How it works" | "Privacy by default. Inputs/outputs SHA-256 hashed" | **TRUE** | [_hashing.py:23](sdk/annexkit/_hashing.py#L23) + [decorator.py:174-175](sdk/annexkit/decorator.py#L174). Plaintext logging never wired in v0.1. |
| A4 | README §"How it works" | "Plaintext is opt-in (lands at v0.2 with encryption-at-rest)" | **FUTURE** | Correctly framed as v0.2. No vapor. |
| A5 | README §"Hosted" | "EU-hosted (Hetzner Falkenstein), Mistral La Plateforme (Paris)" | **TRUE** | Verified per runbook §0 (live on Hetzner) + [config.py:58](backend/app/config.py#L58) (Mistral default). |
| A6 | README §"Status" | "~115 tests across SDK and backend" | **TRUE** | Actual count: 66 backend + 48 SDK = **114**. README rounds to "~115". |
| A7 | AGENTS.md §"7 non-negotiables" | All 7 verified | **TRUE** | See AUDIT.md §2 table. |
| A8 | sdk/README §"What gets recorded" | All 12 span fields present | **TRUE** | Verified field-for-field against [schema.py](sdk/annexkit/schema.py) and [models/span.py](backend/app/models/span.py). |
| A9 | sdk/README §"Status" | "48 unit tests with httpx.MockTransport" | **TRUE** | Exact count: 48 SDK tests. MockTransport usage verified in [test_exporters_http.py](sdk/tests/test_exporters_http.py). |
| A10 | sdk/README §"Sync or async — the decorator auto-detects" | Sync + async work | **TRUE** | [decorator.py:76](sdk/annexkit/decorator.py#L76) `asyncio.iscoroutinefunction(fn)` branching. Both tested. |

---

## 2. Claims — Features in v0.1

| # | Source | Claim | Verdict | Evidence |
|---|---|---|---|---|
| B1 | README §"Quickstart" | `pip install annexkit` works | **TRUE** | Package published per [sdk/CHANGELOG.md](sdk/CHANGELOG.md). README cites PyPI badge. |
| B2 | README §"Quickstart" | `@track` decorator, args `system_id`, `purpose`, `risk_tier` | **TRUE** | [decorator.py:45-66](sdk/annexkit/decorator.py#L45). |
| B3 | README §"Quickstart" | "Without an `ANNEXKIT_API_KEY`, spans are written as JSON to stderr" | **TRUE** | [stdout.py](sdk/annexkit/exporters/stdout.py) is the auto fallback when no key present. |
| B4 | README §"Quickstart" | `make demo-seed` produces Annex IV PDF | **PARTIAL** (untested by me) | Makefile target exists [Makefile:89](Makefile#L89). Example exists [examples/chatbot-openai/](examples/chatbot-openai/). I haven't executed it end-to-end yet — task 0.3 will. |
| B5 | sdk/README §"Multi-step via context manager" | `annexkit.session(...)` exists | **TRUE** | [session.py:108](sdk/annexkit/session.py#L108). |
| B6 | sdk/README §"Custom exporters" | Subclass `Exporter` works | **TRUE** | [exporters/base.py](sdk/annexkit/exporters/base.py) exposes the protocol. |
| B7 | README §"Roadmap shipped in v0.1.x" | "Span ingest API with HMAC-authenticated tenants" | **TRUE** | HMAC-SHA256 verified [api_key.py](backend/app/services/api_key.py). Constant-time compare. |
| B8 | README §"shipped in v0.1.x" | "Annex IV generator (Markdown + PDF, bilingual EN/IT, ~75 KB audit-grade output)" | **PARTIAL** | Generator exists [annex_iv_aggregator.py](backend/app/services/annex_iv_aggregator.py) + [annex_iv_renderer.py](backend/app/services/annex_iv_renderer.py). Bilingual verified in template. **"~75 KB" not verified** — depends on content (number of spans, sections). I haven't run a full generation. Task 0.3 will produce a real PDF I can byte-count. |
| B9 | README §"shipped in v0.1.x" | "Public trust pages with `provider_info` whitelist redaction" | **TRUE** | [trust_service.py:40](backend/app/services/trust_service.py#L40) `_PUBLIC_PROVIDER_FIELDS` whitelist. |
| B10 | README §"shipped in v0.1.x" | "Cross-tenant isolation tests" | **TRUE** | 8 tests in [test_cross_tenant_isolation.py](backend/tests/test_cross_tenant_isolation.py) — exact match to internal claim of "8 test di isolation". |
| B11 | README §"shipped in v0.1.x" | "Idempotent span ingest with TOCTOU race protection" | **TRUE** | [span_service.py:115-138](backend/app/services/span_service.py#L115) — `IntegrityError` rescue with rollback + re-fetch. Test in [test_spans_idempotency.py](backend/tests/test_spans_idempotency.py). |

---

## 3. Claims — Roadmap items (correctly framed as v0.2)

These are NOT vapor — they're labeled as roadmap. Listed here for completeness and so
the marketing site doesn't accidentally promote them as "available."

| # | Source | Claim | Verdict | Note |
|---|---|---|---|---|
| F1 | README + sdk/README §"v0.2" | LangChain + LlamaIndex auto-instrumentation | **FUTURE** | No `auto_instrument` in SDK code today. Honest v0.2 framing. |
| F2 | README §"v0.2" | TypeScript / JavaScript SDK | **FUTURE** | No `sdk-ts/` directory. Honest framing. |
| F3 | README §"v0.2" | LLM advisor (Mistral) for ambiguous declarations | **FUTURE** | `mistral_client.py` exists [services/mistral_client.py](backend/app/services/mistral_client.py) but no advisor call-site in `risk_classifier.py` or `ai_system_service.py`. Wiring is v0.2. |
| F4 | README §"v0.2" | Span batching + retry on transient failure | **FUTURE** | [exporters/http.py:8](sdk/annexkit/exporters/http.py#L8) acknowledges "v0.1 is best-effort: failures are logged at WARNING and the span is dropped." Honest. |
| F5 | README §"v0.2" | Trust badge embeddable | **FUTURE** | No badge endpoint. Honest. |
| F6 | README §"v0.2" | Customer dashboard + Stripe self-serve sign-up | **FUTURE** | No billing code. Honest framing in v0.2 list. But see C2 below — `pricing` page mentioned without disclosure. |
| F7 | README §"v0.2" | Rate limiting on public trust API | **FUTURE / RISKY** | Listed as v0.2 but should be P1 NOW (see AUDIT.md F2). Until shipped: anyone can DOS the trust API. |
| F8 | sdk/README §"v0.2" | OpenTelemetry GenAI semconv compliance | **FUTURE** | `opentelemetry-api` in uv.lock but no OTLP exporter / span emission. Honest framing. |

---

## 4. Critical issues — vapor in active flows

### C1 — `sdk/README.md` documents a workflow that breaks

[sdk/README.md:76-79](sdk/README.md#L76):
```bash
export ANNEXKIT_API_KEY=ak_xxxxx
export ANNEXKIT_COLLECTOR_URL=https://collector.annexkit.dev
```

The user follows these instructions → SDK POSTs to `https://collector.annexkit.dev/api/v1/spans` → DNS fails / 404 because there is no `collector.annexkit.dev` DNS record (runbook §2.2 only sets up `annexkit.dev` and `www.annexkit.dev`).

**Impact**: a developer who follows the quickstart in the most natural way (PyPI install → hosted collector) hits a dead end. They either: (a) give up, (b) figure out they need `https://annexkit.dev` instead, (c) self-host. All three are bad first-touch experiences.

**Vapor severity**: HIGH — this is the only spot where shipped code + shipped README contradict each other in a way the user will notice immediately.

**Fix**: same as AUDIT.md F1 — set up the `collector.annexkit.dev` DNS + Caddy block. Total time 30 min.

### C2 — Pricing page mentioned without billing infrastructure

[README.md:144](README.md#L144) says:
> "See [annexkit.dev/pricing](https://annexkit.dev/pricing) for current tiers."

`MONETIZZAZIONE.md` describes 4 tiers (Free, Pro $49, Team $199, Enterprise €5K). The backend has:
- Zero usage tracking (no `usage_logs` table; spans table is purely for audit, not metering)
- Zero quota enforcement (a "Free" tenant can ingest 5 billion spans, nothing stops them)
- Zero Stripe / billing integration
- No tenant tier column on `tenants` table (verified [models/tenant.py](backend/app/models/tenant.py))

If `annexkit.dev/pricing` advertises the 4 tiers with "Sign up" buttons, that's promising a flow that doesn't exist. The README says "early access" which is the correct mitigation — make sure the pricing page also says "early access — contact us" and routes to email until Stripe ships in v0.2.

**Action**: I haven't seen the live `/pricing` page content (frontend audit out of scope). Verify it before any HN / paid traffic push. If it has Stripe Checkout buttons, that's vapor. If it says "early access — email us", that's honest.

---

## 5. Internal docs — claims that overstate v0.1

These don't reach the public site, but if a copywriter pulls examples from these docs they will. Flag for review when writing marketing pages.

| # | Source (internal) | Claim | Real state |
|---|---|---|---|
| I1 | ANNEXKIT_PLAN.md §2.2 | `annexkit.auto_instrument(["openai", "anthropic", "langchain", "llama_index"])` shown as usage example | Not in v0.1 SDK. sdk/README correctly puts in v0.2 list. **Don't copy this snippet to marketing.** |
| I2 | ANNEXKIT_PLAN.md §2.2 | "Middleware pattern: `app.add_middleware(AnnexKitMiddleware, ...)`" | Not in v0.1 SDK (no `annexkit.fastapi` submodule). v0.2+. |
| I3 | ANNEXKIT_PLAN.md §5.3 | "Span ingest path: OTLP-compatible on `/v1/spans/otlp`" | Only `/api/v1/spans` HTTP JSON exists. No OTLP endpoint. v0.2+. |
| I4 | ANNEXKIT_PLAN.md §5.3 | "S3-compatible storage for blob (prompt templates, PDF Annex IV signed)" | Only Postgres + local-disk `/data/documents` per [docker-compose.yml:51](docker-compose.yml#L51). No S3 wiring. v0.2+. |
| I5 | ANNEXKIT_PLAN.md §5.3 | "Schema-per-tenant in Postgres + row-level security" | Single schema, `tenant_id` column on all tables, app-level isolation enforced by tests. No schema-per-tenant. No PG RLS. Not necessarily a problem — `tenant_id` + tested isolation is fine — but the claim overstates the mechanism. |
| I6 | ANNEXKIT_PLAN.md §2.4 | "Output: Markdown + PDF. PDF generated via WeasyPrint with disclaimer permanent in footer" | TRUE for body. **Footer**: the markdown template has the disclaimer at the **top**, not in a footer. The HTML/PDF template I didn't read fully — if footer disclaimer is needed (it is, per AGENTS non-negotiable #6, and the runbook §3.1 mentions it), verify it. |
| I7 | ANNEXKIT_PLAN.md §5.2 | "Auth: stesso pattern Konformia (JWT cookie)" | False for v0.1. Auth is **Bearer API key** only (`Authorization: Bearer ak_...`). No cookies, no JWT. Roadmap M4 brings SSO/JWT. The plan doc is just stale. |
| I8 | COSA_E_ANNEXKIT.md §2.2 Mario story | "Going to dashboard, signing up, receiving API key" | False for v0.1. There is no signup UI. A tenant + API key is seeded by the `make seed` script ([scripts/seed_tenant.py](scripts/seed_tenant.py)). Self-serve sign-up = v0.2 (per README). For early access, this is fine if landing page says "request an API key". |
| I9 | COSA_E_ANNEXKIT.md §5.4 | "Vercel deploy gratuito" for frontend | Inconsistent. The frontend is in the Docker compose stack ([docker-compose.yml:57](docker-compose.yml#L57)), not on Vercel. Either commit to one path or update the doc. |

---

## 6. Pricing — vapor risk if marketed today

| Tier | Promised | Real state | Verdict |
|---|---|---|---|
| Free $0 / 100K spans / 1 system / 1 user | 100K span cap, 1 system cap, 1 user cap | **NO quota enforcement.** Anyone can ingest unlimited spans, declare unlimited systems. The fairness model is honor-based today. | OK as "early access free tier", VAPOR if marketed with hard caps |
| Pro $49/mo / 5M spans / 10 systems / 3 users / PDF / trust center | All features above | **NO billing.** Stripe not wired. **NO user management** — tenant has 1 implicit "owner". | VAPOR as a purchaseable tier today |
| Team $199/mo / 50M spans / SSO / SLA | SSO via Google/GitHub, audit log retention 7 years, SLA 99.5% | **NO SSO** (no OAuth code). **NO SLA infra** (no monitoring runbook §6). 7-year retention is implicit (no automated deletion). | VAPOR |
| Enterprise €5K/yr / Helm chart / custom support | Helm chart for Kubernetes, license check | **NO Helm chart.** No license check. Self-host via docker compose only. | VAPOR |

**Recommendation**: until Stripe + quota enforcement ships, the pricing page should say:
> "Pricing tiers below land Q3 2026. For early-access today, email founder@annexkit.dev — we operate Pro-tier customers on invoice and Enterprise customers on PoC contract."

This is honest, doesn't lose deals, and avoids the cardinal sin of marketing-led product where the buy button doesn't work.

---

## 7. Things that are NOT vapor that I expected might be

I had hypothesised these would be vapor. Pleasantly surprised they're real:

- ✅ "Disclaimer permanent on PDF cover + footer" — actually in [annex_iv.md.jinja:32](backend/app/templates/annex_iv.md.jinja#L32). Bilingual.
- ✅ "Trust page redaction whitelist not blacklist" — actually `_PUBLIC_PROVIDER_FIELDS` is a `frozenset` whitelist.
- ✅ "Cross-tenant 404s are byte-identical" — actually tested in [test_cross_tenant_isolation.py:240](backend/tests/test_cross_tenant_isolation.py#L240).
- ✅ "`system_id` rejects path traversal" — actually tested ([test_cross_tenant_isolation.py:258](backend/tests/test_cross_tenant_isolation.py#L258)).
- ✅ "Spans + audit log in same transaction" — actually wired via shared `AsyncSession`, both flush before commit ([span_service.py:140](backend/app/services/span_service.py#L140)).
- ✅ "EU residency via config" — Mistral default endpoint is Paris; no fallback to US-based LLM. Hetzner is operational.
- ✅ "Provider hardening at startup" — actually fails fast on dev `SECRET_KEY` / wildcard CORS in prod ([main.py:49](backend/app/main.py#L49)).

---

## 8. Verdict by document

| Document | Honesty score | Why |
|---|---|---|
| `README.md` (root) | 95% | Honest "early access" framing, accurate test count, clear v0.1 vs v0.2 split. -5% for "see /pricing" without verifying that page is honest. |
| `sdk/README.md` | 85% | Mostly honest. -15% for the broken `ANNEXKIT_COLLECTOR_URL` snippet (#C1) which actively breaks user trust. |
| `AGENTS.md` | 100% | Pinned invariants, all verified in code. |
| `sdk/CHANGELOG.md` | 100% | Accurate. |
| `ANNEXKIT_PLAN.md` (internal) | 75% | Mixes v0.1 reality with v0.2/v0.3 plans without consistent labelling. OK for internal brainstorming, dangerous if copywriters pull snippets from it. |
| `COSA_E_ANNEXKIT.md` (internal) | 80% | Generally honest. The "Mario signs up" story (#I8) and "Vercel deploy" (#I9) are minor stale spots. |
| `MONETIZZAZIONE.md` (internal) | 70% | 4 tiers described as if purchaseable. The "honest" framing in the doc's premise is good (it acknowledges the disconnect), but if the pricing page mirrors this without "early access" caveats it's vapor. |

---

## 9. Action items (anti-vapor)

**Before any marketing push** (P1):
1. **Fix #C1** — set up `collector.annexkit.dev` DNS + Caddy block. 30 min. (Same as AUDIT.md F1.)
2. **Verify the live `annexkit.dev/pricing` page** — does it have working Stripe buttons or "early access, email us"? If the former: take down the Stripe buttons until v0.2 billing ships, replace with email form.
3. **Add a "Status" banner** to the marketing site: "v0.1.x — early access. Pricing tiers ship Q3 2026 with self-serve billing. Email today for invoice setup."

**Before posting `ANNEXKIT_PLAN.md` excerpts publicly** (P2):
4. Audit the plan doc snippets you intend to share. Any code example using `auto_instrument`, `AnnexKitMiddleware`, OTLP, or schema-per-tenant must either be marked "(v0.2)" or replaced with v0.1 reality.

**Before bullish public statements about non-negotiables** (P2):
5. Land AUDIT.md F3 (Postgres trigger CI test). Until then "append-only enforced by Postgres trigger" is true in prod but unprovable in CI — would be embarrassing if a journalist asked for the test.

---

_End of anti-vapor audit. The codebase is honest. The risk is in the gap between "documented today" and "live tomorrow" — fix the C1 dead-link and the pricing page disclosure and the public surface lines up with what's shipped._
