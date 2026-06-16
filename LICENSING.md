# Licensing

This repository follows an **open-core** model: the SDK, the compliance engine,
and the runtime collector are open source; the hosted Konformia platform is
proprietary.

| Component | Path | License | Published |
|---|---|---|---|
| AnnexKit SDK | `sdk/` | MIT | ✅ public |
| Konformia Core (engine) | `core/` | AGPL-3.0-or-later¹ | ✅ public |
| AnnexKit collector (backend + frontend) | `apps/annexkit/` | AGPL-3.0-or-later | ✅ public |
| Konformia platform (SaaS) | `apps/konformia/` | Proprietary | ❌ private |

¹ Dual-licensed — see [Core and dual licensing](#core-and-dual-licensing).

## Why this split

- **SDK = MIT.** It is the developer library you `pip install annexkit`. Friction
  kills library adoption, so it carries the broadest permissive license: importing
  it into a proprietary app creates zero copyleft obligation. It depends on nothing
  else in this repo — its span schema is a deliberate copy of core's Evidence
  contract (kept in sync by a contract test, not an import) — so it is cleanly
  standalone.

- **Core + collector = AGPL-3.0.** The engine and the managed collector are the
  open-core heart. AGPL lets anyone self-host or fork, but anyone who exposes
  modifications as a network service must publish their source. Same reasoning used
  by Sentry, PostHog, MinIO, and Grafana: genuinely open, while preventing a
  competitor from running a closed SaaS fork of the engine.

- **Konformia platform = proprietary.** The hosted product — billing, multi-tenant
  orchestration, the Italian compliance UX, accumulated evidence — is the commercial
  moat and is not distributed.

## Core and dual licensing

`core/` is offered to the public under the AGPL-3.0. Konformia is the **sole
copyright holder**, and as the holder it ALSO uses `core/` under separate
commercial terms inside the proprietary platform. The AGPL binds third parties,
not the copyright holder — this is exactly what lets an AGPL engine sit beneath a
closed product owned by the same entity (the Sentry / MongoDB pattern).

`apps/konformia` imports `core` in ~12 modules; it stays proprietary **only**
because Konformia owns core's copyright. To keep this intact:

- Every external contribution to `core/`, `sdk/`, or `apps/annexkit/` is accepted
  **only under the [Contributor License Agreement](CLA.md)**. Without it, the first
  merged outside PR would break the dual-licensing right.
- The formal reservation lives in [`core/NOTICE`](core/NOTICE).

## Public mirror

The open-source subset (`core/`, `sdk/`, `apps/annexkit/`) is mirrored — one-way —
to the public AnnexKit repository via [`scripts/mirror-annexkit.sh`](scripts/mirror-annexkit.sh).
`apps/konformia/` is never included; the script aborts if it ever appears in the
staged tree.

## Commercial licensing

Need a commercial license that exempts your deployment from AGPL obligations, or a
different arrangement for `core` / the collector? Contact: **commercial@konformia.eu**
_(placeholder — replace with the real contact)._
