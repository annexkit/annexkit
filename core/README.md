# konformia-core — the shared compliance engine

This package is the **single source of truth** for the compliance logic that
both products consume. It exists so the classifier, artifact generator, and
audit log are written **once**, not twice.

## Who imports this

```
apps/konformia/backend  ──import──▶  konformia_core  ◀──import──  apps/annexkit/backend
```

- Both backends `import konformia_core` **in-process**. Core is a *library*,
  **not** a microservice — no FastAPI, no HTTP server lives here.
- `core` imports **nothing** from `apps/*` or `sdk/`. The dependency arrows
  only ever point *toward* core.
- The AnnexKit SDK (`sdk/`) does **not** import core either. Its span schema
  is a *deliberate copy* of `konformia_core.schemas` so the SDK and collector
  can version independently — kept honest by a contract test, not an import.

## What lives here (target state)

| Module | Responsibility | Non-negotiable |
|---|---|---|
| `classifier/` | Deterministic Annex III risk engine + `annex_iii.json` | Rules-driven; LLMs never declassify |
| `artifacts/` | Annex IV / DoC / FRIA / RMS / IFU / PMP / SCL generation + templates | + stateless & markdown modes |
| `models/` | Canonical ORM: `System`, `Classification`, `Evidence`, `AuditLog` | ORM never leaves the service layer |
| `schemas/` | Canonical Pydantic schemas | SDK span schema is a copy of these |
| `audit/` | Append-only audit service (`record` + `record_for_actor`) | No UPDATE/DELETE on `audit_logs`, ever |
| `adapters/` | `mistral_client` (EU LLM provider) | EU residency; no US fallback |
| `rules/` | Regulatory rule packs as **data** (`eu/`, `it/`) | Engine stays jurisdiction-agnostic |

## Status

**Step 1 — skeleton only.** No compliance logic has moved in yet; the
submodules are documented placeholders. The extraction happens in Steps 2–5
of [`../MIGRATION.md`](../MIGRATION.md), each as its own reviewable PR gated by
a verdict-equality regression test.
