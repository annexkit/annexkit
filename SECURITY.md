# Security policy

We take security seriously because AnnexKit handles the audit trail
of AI systems used in regulated EU environments. A vulnerability in
the collector — or a misconfiguration that lets one tenant's spans
leak to another — undermines the trust contract the whole product
depends on.

## Reporting a vulnerability

**Please do not open a public GitHub issue for security problems.**

Email: **security@annexkit.dev**.

Include:

  * A description of the vulnerability and its impact.
  * Steps to reproduce (URLs, commands, payloads).
  * The version / commit hash you observed it on.

Acknowledgement target: **48 hours**. Triage + initial fix plan target:
**5 business days**. We'll keep you posted while we ship.

## Scope

Anything in this repository:

  * `sdk/` — the Python SDK published as `annexkit` on PyPI.
  * `backend/` — the FastAPI collector + Annex IV API.
  * `frontend/` — the public trust-center pages.
  * `examples/` — runnable demos that exercise the above.
  * The `Dockerfile`s + `docker-compose.yml` shipping configurations.

Out of scope:

  * Vulnerabilities in upstream dependencies — please report those
    upstream first; we'll track and rebuild promptly.
  * Social-engineering / phishing attacks against project maintainers.
  * Rate limiting on the public `/api/v1/trust/*` endpoints — known
    gap, queued for v0.2; please do not stress-test it.

## Known security model

Critical invariants that should NOT regress:

  1. **`audit_logs` is append-only.** Enforced at three layers:
     no service exposes UPDATE/DELETE; the `audit_service.record`
     function is INSERT-only; a Postgres trigger raises on
     UPDATE/DELETE at the DB layer (installed by migration
     `0001_initial`).
  2. **Risk classifier is deterministic.** The rule engine
     (`backend/app/services/risk_engine.py`) never declassifies. Any
     LLM advisor (Mistral, future) can suggest categories that raise
     the tier but never lower it.
  3. **Privacy-by-default in spans.** The SDK SHA-256 hashes
     input/output before transport. Plaintext content does not leave
     the host process by default.
  4. **EU data residency.** Collector deploys to Hetzner
     (Falkenstein/Helsinki). LLM advisor calls go to Mistral La
     Plateforme (Paris). No US-hosted services for PII or telemetry.
  5. **API keys are HMAC-hashed at rest.** Plaintext is shown to the
     user once at generation; HMAC-SHA256 (keyed by `SECRET_KEY`) is
     stored. Verification is constant-time.
  6. **Trust-page redaction is whitelist-based.** Sensitive
     `provider_info` fields (contact_email, validation_methods,
     notes) MUST NOT surface on `/api/v1/trust/*`. Adding a key
     defaults to private; explicit allowlist in
     `backend/app/services/trust_service.py::_PUBLIC_PROVIDER_FIELDS`
     is required to expose it.

If a finding contradicts any of the above, treat it as
**critical**.

## Dependency security

  * Backend uses `uv` lockfile; we update + audit on every release.
  * SDK pins `httpx>=0.27` and `pydantic>=2.0` — minimum versions
    chosen to avoid known CVEs at time of writing.
  * Frontend uses `npm` lockfile; we update + audit on every release.
  * Docker base images: `python:3.13-slim-bookworm` and
    `node:22-bookworm-slim` — patched within 7 days of upstream
    advisory.

## Disclosure timeline

We will publicly disclose a fixed vulnerability **30 days** after the
fix ships, or earlier if the issue is being actively exploited. We
will credit the reporter unless asked otherwise.
