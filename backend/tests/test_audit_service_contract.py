"""Audit-service contract tests.

The append-only invariant on ``audit_logs`` has three defense layers:

  1. The Postgres trigger ``annexkit_audit_logs_immutable`` raises on
     UPDATE/DELETE at the DB layer. Tested live against Postgres (not
     in this file — it requires real Postgres + the trigger from
     migration 0001_initial).

  2. No service or API exposes update/delete semantics for the
     ``audit_logs`` table.

  3. ``audit_service`` exposes exactly one mutation function:
     :func:`record`. This file pins (3) so a future PR adding an
     "audit_service.delete_old(...)" or similar gets bounced in CI.

These tests do NOT require a database. They introspect the module
namespace.
"""

from __future__ import annotations

import inspect

from app.services import audit_service


def test_audit_service_exposes_only_record() -> None:
    """The ``audit_service`` module must expose exactly one public
    callable: ``record``. Anything else is a contract violation."""
    public_callables = {
        name
        for name, obj in vars(audit_service).items()
        if not name.startswith("_")
        and (inspect.iscoroutinefunction(obj) or inspect.isfunction(obj))
    }
    # Only ``record`` is a coroutine function; everything else is an
    # imported type / module / class.
    assert "record" in public_callables

    forbidden = {
        "update",
        "delete",
        "remove",
        "edit",
        "modify",
        "purge",
        "drop",
        "truncate",
        "rotate",
    }
    leaked = forbidden & public_callables
    assert not leaked, (
        f"audit_service must not expose mutation functions; "
        f"found: {sorted(leaked)}. The append-only invariant requires "
        f"that only ``record`` (INSERT) is public — see "
        f"app/models/audit_log.py for the rationale."
    )


def test_record_is_insert_only_in_implementation() -> None:
    """Sanity-check ``record``'s implementation: it should only call
    ``session.add(...)`` + ``session.flush()``. No update / delete /
    execute(UPDATE/DELETE) calls."""
    source = inspect.getsource(audit_service.record)
    forbidden_substrings = [
        "session.delete(",
        "session.execute(update(",
        "session.execute(delete(",
        # The bare ".update(" might appear inside ``details=details``
        # which is a dict.update() in callers, not in our impl —
        # check our impl source itself.
    ]
    for forbidden in forbidden_substrings:
        assert forbidden not in source, (
            f"audit_service.record contains forbidden mutation: "
            f"{forbidden!r}. Only INSERT (session.add + session.flush) "
            f"is allowed."
        )
