"""konformia_core — the single shared compliance engine.

Source of truth for the deterministic EU AI Act risk classifier, the artifact
generator (Annex IV, DoC, FRIA, ...), the append-only audit log, and the
canonical data model. Both surfaces — the AnnexKit collector
(``apps/annexkit``) and the Konformia SaaS (``apps/konformia``) — import from
here.

Invariants (enforced by review + tests, see ../MIGRATION.md):
  * ``konformia_core`` imports nothing from ``apps/*`` or ``sdk/``.
  * The AnnexKit SDK (``sdk/``) never imports ``konformia_core`` — its span
    schema is a deliberate copy, kept in sync by a contract test.
  * ``core`` is an in-process library, never a network service.

NOTE: this is a Step-1 skeleton. Compliance logic has NOT moved in yet — that
is Steps 2+ of the migration. The submodules are intentionally empty
placeholders that mark where each piece lands.
"""

from __future__ import annotations

__version__ = "0.0.1"
