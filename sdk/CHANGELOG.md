# Changelog — `annexkit` Python SDK

All notable changes to the `annexkit` Python SDK are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning is [SemVer](https://semver.org/) — pre-1.0 minors may break.

The SDK is shipped under MIT (see [`LICENSE`](LICENSE)). Releases are
published to PyPI as `annexkit` once the founder cuts the first
official tag.

## [Unreleased]

Targeted for the next minor (v0.2.0) — see
[`docs/ANNEXKIT_PLAN.md`](../docs/ANNEXKIT_PLAN.md) M2 milestones.

### Planned

- **Mistral advisor for ambiguous declarations** — when a
  declaration's `purpose` is set but `annex_iii_categories` is
  empty, the SDK can ask the collector for AI-suggested categories
  via Mistral La Plateforme. Hard guardrail: never declassifies.
- **LangChain + LlamaIndex auto-instrumentation** —
  `annexkit.auto_instrument(["langchain"])` so `LLMChain.run()` and
  similar are traced without a manual `@track` decoration.
- **TypeScript / JavaScript SDK** (`@annexkit/node`) — port of the
  Python SDK so Next.js, Express, and Cloudflare Workers can ingest
  spans. Same wire format, same env-var conventions.
- **Async HTTP exporter** — `httpx.AsyncClient` instead of
  `httpx.Client` wrapped via `asyncio.to_thread`. Saves a thread
  per export under heavy concurrency.
- **Span batching** — accumulate up to N spans for up to M seconds
  before POSTing. Cuts round-trips by ~60x for high-frequency
  systems.
- **Retry on transient failure** — exponential backoff on 5xx and
  network errors. Today the HTTP exporter drops on failure with a
  WARN log.
- **OpenTelemetry GenAI semconv compliance** — emit OTel-native
  spans alongside the AnnexKit-specific extensions, so a single
  collector can feed both AnnexKit and existing OTel pipelines.

### Deployment notes (already in effect against v0.5.x backend)

- The v0.5.x backend now enforces a regex on `system_id`:
  `^[A-Za-z0-9._-]+$`. SDKs that emit special characters (spaces,
  quotes, slashes) will see HTTP 422 from the collector. v0.1.0
  SDKs are otherwise wire-compatible. Action: rename any
  `system_id` to fit `[A-Za-z0-9._-]+`. Same restriction applies
  to `trace_id`, `span_id`, `parent_span_id` (hex tokens — already
  satisfied by `uuid.uuid4().hex`).

## [0.1.3] — 2026-05-23

### Fixed

- **Default `ANNEXKIT_COLLECTOR_URL` now points to `https://annexkit.dev`** —
  previously the default was `https://collector.annexkit.dev`, but that
  subdomain was never set up on Cloudflare DNS. Users following the
  quickstart with just `pip install annexkit` + `ANNEXKIT_API_KEY=...`
  would silently POST to a host that doesn't resolve. The hosted
  collector lives at `https://annexkit.dev/api/v1/spans` (no
  subdomain), so the default now matches reality.

### Migration

If you previously set `ANNEXKIT_COLLECTOR_URL=https://collector.annexkit.dev`
to work around this, you can now drop that line — the default works
out of the box. No code changes required if you were already setting
the URL explicitly.

## [0.1.2] — 2026-05-10

### Fixed

- **`annexkit.__version__` now matches the installed package version.**
  v0.1.1 shipped with a hardcoded `SDK_VERSION = "0.1.0"` constant in
  `_state.py` while `pyproject.toml` already said `0.1.1`. The two had
  drifted because they were two parallel sources of truth.
- Replaced the constant with a runtime read of the package metadata
  via `importlib.metadata.version("annexkit")`. From now on
  `pyproject.toml` is the only place to bump versions; `__version__`
  follows. Source-tree (uninstalled) imports fall back to
  `0.0.0+dev` so the dev case is visually obvious.

### Tests

- `test_version_exposed` no longer pins an exact version string;
  asserts SemVer-ish regex instead, so future bumps don't break the
  test suite.

## [0.1.1] — 2026-05-10

PyPI listing polish — no code changes, no behaviour changes. The
0.1.0 listing still ships and is fully compatible.

### Changed

- **README rewritten for the PyPI page.** Drops repo-relative links
  (`../CLAUDE.md`, `../README.md` etc. that 404 on PyPI), adds
  shields.io badges (PyPI version, Python versions, license, GitHub
  stars), updates the status section from "Day 2 of MVP" to
  `v0.1.x` early access, leads with concrete value before the field
  table, adds a "Links" section in dev-tool convention.
- **Author email** updated from `hello@annexkit.dev` to
  `founder@annexkit.dev` to match the email aliases configured on
  Cloudflare Email Routing.

## [0.1.0] — 2026-05-07

First functional release. Day 2 of the MVP roadmap (see
[`docs/ANNEXKIT_PLAN.md`](../docs/ANNEXKIT_PLAN.md) §7).

### Added

- `@track(system_id, ...)` decorator — works on sync and async
  functions (auto-detected). Captures inputs/outputs (SHA-256
  hashed), start/end timestamps, latency, exception (if any),
  model details when set explicitly.
- `annexkit.session(...)` — context manager for non-function code
  paths. Yields a `SpanHandle` with `set_input` / `set_output` /
  `attach_source` / `set_model` / `set_user_role` / `set_error` /
  `add_metadata`.
- `annexkit.configure(...)` — runtime override for `api_key`,
  `collector_url`, `exporter`, `disabled`, `deployment`. Accepts
  a string exporter name or a custom `Exporter` instance.
- `annexkit.flush()` / `annexkit.shutdown()` — graceful drain
  and resource release for the HTTP exporter.
- `Span`, `Source`, `SpanHandle`, `Exporter`, `StdoutExporter`,
  `HttpExporter` — public types for adapter authors.
- Exporters:
  - `StdoutExporter` — JSON lines to stderr (default when no API
    key set).
  - `HttpExporter` — synchronous `httpx.Client` POST to
    `${ANNEXKIT_COLLECTOR_URL}/api/v1/spans`.
- Configuration via env (`ANNEXKIT_API_KEY`,
  `ANNEXKIT_COLLECTOR_URL`, `ANNEXKIT_EXPORTER`,
  `ANNEXKIT_DISABLED`, `ANNEXKIT_DEPLOYMENT`).
- Privacy-by-default: input/output payloads are SHA-256 hashed
  before any transport. Plaintext logging is intentionally not
  exposed in v0.1.

### Packaging (added during launch readiness work)

- PEP 639 license metadata: `license = "MIT"` +
  `license-files = ["LICENSE"]` (replaces deprecated SPDX
  classifier).
- Trove classifiers updated: Development Status moved to Alpha,
  Intended Audience expanded to Legal Industry + System
  Administrators.
- Verified: `uv build` produces clean `.tar.gz` + `.whl` with
  proper `License-Expression` + `License-File` in METADATA.

### Tests

- 48 unit tests covering hashing, schema, config, both decorator
  paths (sync + async, including concurrent gather), session,
  both exporters. `httpx.MockTransport` is used for hermetic
  HTTP coverage — no real network in tests.

## [0.0.1] — 2026-05-07

Placeholder package. `annexkit.track(...)` raised
`NotImplementedError` to reserve the PyPI name. Replaced same day
by 0.1.0.
