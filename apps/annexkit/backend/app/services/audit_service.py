"""Audit service — the only way to write to ``audit_logs``.

Keep this tiny. One function: :func:`record`. No read methods, no
update methods, certainly no delete methods. If you feel tempted to
add one, stop and re-read ``app/models/audit_log.py``.

Design notes:
    * Reuses the caller's ``AsyncSession`` so audit writes participate in
      the same transaction as the triggering domain change. If the
      domain INSERT rolls back, the audit row rolls back too — no
      "phantom audit rows".
    * The Postgres trigger installed by the initial migration
      (``annexkit_audit_logs_immutable``) makes UPDATE/DELETE impossible
      at the DB level, so even raw psql can't violate append-only.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def record(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    action: str,
    user_id: uuid.UUID | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """Insert one audit event. Contract: this function only INSERTs.

    Returns the persisted row so callers can include the id in a
    response if they ever need to. Commit is handled by the surrounding
    ``get_session()`` dependency.
    """
    entry = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
    )
    session.add(entry)
    # Flush (not commit) so ``entry.id`` is populated if the caller needs it.
    await session.flush()
    return entry
