"""Bearer-token tenant resolution dependency.

The SDK presents ``Authorization: Bearer ak_<24-char-suffix>`` on every
ingest request. This module turns that header into a :class:`Tenant`
the route handler can trust.

Lookup is **one** indexed JOIN — ``api_keys.key_hash`` is the HMAC of
the plaintext keyed with ``SECRET_KEY``, hex-encoded, with a unique
index. Constant-time hash comparison happens inside ``hmac.new`` plus
the database B-tree probe.

Side effect: a successful auth bumps ``api_keys.last_used_at`` to now.
This is best-effort: the surrounding ``get_session`` rolls back on any
raise, so 4xx route errors (422 validation, 404 not-found) revert the
``last_used_at`` write. Only 2xx requests update the timestamp.

Failed auth attempts are logged at WARN level (no plaintext, just
prefix + reason) so credential-stuffing bursts surface in production
log aggregation.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select

from app.api.deps import SessionDep
from app.models.tenant import ApiKey, Tenant
from app.services import api_key as api_key_service

logger = logging.getLogger("annexkit.auth")

_BEARER_PREFIX = "bearer "


async def get_authenticated_tenant(
    request: Request,
    session: SessionDep,
    authorization: Annotated[str | None, Header()] = None,
) -> Tenant:
    """Resolve the tenant owning the API key in ``Authorization``.

    Raises 401 on any failure (missing header, bad scheme, malformed
    key, unknown hash, revoked key, deleted tenant). The error message
    intentionally stays vague — we don't tell an attacker WHY auth
    failed.

    Failures log at WARN with the request_id + IP + reason category so
    rate limiters / SIEMs can spot credential-stuffing patterns.
    """
    request_id = getattr(request.state, "request_id", None)
    client_host = request.client.host if request.client else None

    if not authorization or not authorization.lower().startswith(_BEARER_PREFIX):
        _log_failure("missing_header", request_id, client_host)
        raise _unauthorised("Missing or malformed Authorization header")

    plaintext = authorization[len(_BEARER_PREFIX) :].strip()
    if not api_key_service.looks_like_api_key(plaintext):
        _log_failure("malformed_key", request_id, client_host)
        raise _unauthorised("Invalid API key")

    key_hash = api_key_service.hash_key(plaintext)

    # Single JOIN — one B-tree probe on ``api_keys.key_hash`` (unique
    # index), one PK lookup on ``tenants.id`` along the FK relationship.
    row = (
        await session.execute(
            select(ApiKey, Tenant)
            .join(Tenant, Tenant.id == ApiKey.tenant_id)
            .where(ApiKey.key_hash == key_hash)
            .where(ApiKey.revoked_at.is_(None))
        )
    ).first()
    if row is None:
        _log_failure("unknown_or_revoked_key", request_id, client_host)
        raise _unauthorised("Invalid API key")

    api_key_row, tenant = row

    # Best-effort touch of ``last_used_at`` — committed by the
    # surrounding ``get_session()`` dependency. 4xx route errors will
    # roll this back; only 2xx persists it.
    api_key_row.last_used_at = datetime.now(UTC)

    return tenant


def _log_failure(reason: str, request_id: str | None, client_host: str | None) -> None:
    """Log auth failure with no plaintext or hash material."""
    logger.warning(
        "auth_failed reason=%s request_id=%s client=%s",
        reason,
        request_id or "-",
        client_host or "-",
    )


def _unauthorised(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


TenantDep = Annotated[Tenant, Depends(get_authenticated_tenant)]
