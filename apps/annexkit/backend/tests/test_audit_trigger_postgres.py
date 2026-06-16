"""Postgres trigger integration test — verifies the append-only DB layer.

The append-only invariant on ``audit_logs`` has THREE defence layers
(see :mod:`app.models.audit_log` docstring). The other two layers are
tested elsewhere with SQLite in-memory:

  * Service-layer contract: ``test_audit_service_contract.py`` pins
    that ``audit_service`` exposes only ``record`` (no update/delete).
  * Module introspection: same test file also greps the
    ``audit_service.record`` source for forbidden mutation calls.

This file pins the THIRD layer — the actual Postgres trigger
``annexkit_audit_logs_immutable`` that ``BEFORE UPDATE OR DELETE``
raises an exception at the DB level. Without this test, the trigger
is verified only manually in production; a future migration that
accidentally drops it would slip through CI.

Why direct asyncpg instead of the conftest SQLAlchemy fixture: the
trigger lives at the SQL layer, so the test must hit raw SQL not the
ORM (which the service layer never uses for these tables anyway). The
test connects via the configured ``settings.database_url`` — works
against:

  * CI ``postgres`` service container (per .github/workflows/ci.yml)
  * Local ``make up`` Postgres (when developing locally)

…and SKIPS when the DATABASE_URL points at SQLite (typical for fast
unit-test loops via conftest). The skip message makes the requirement
obvious.

Run locally:

    make up                       # start the Postgres container
    make db-migrate               # apply migrations (installs trigger)
    make backend-test             # all tests including this one
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime

import asyncpg
import pytest

from app.config import settings


def _postgres_dsn_or_skip() -> str:
    """Return a psycopg-style DSN for asyncpg, or call pytest.skip()."""
    url = settings.database_url
    # SQLAlchemy URL form: postgresql+asyncpg://user:pass@host:port/db
    # asyncpg.connect wants: postgresql://user:pass@host:port/db
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql://" + url[len("postgresql+asyncpg://") :]
    if url.startswith("postgresql://"):
        return url
    pytest.skip(
        f"This test requires a real Postgres database (settings.database_url is "
        f"{url!r}, which is not Postgres). Run `make up` to start the dev "
        f"Postgres container, then re-run with `make backend-test`."
    )


async def _can_connect(dsn: str) -> bool:
    """Best-effort: skip if Postgres isn't actually reachable."""
    try:
        conn = await asyncio.wait_for(asyncpg.connect(dsn), timeout=3.0)
    except (OSError, asyncpg.PostgresError, asyncio.TimeoutError):
        return False
    await conn.close()
    return True


async def _insert_one_row(conn: asyncpg.Connection) -> int:
    """Seed one audit_logs row so we have something to attempt UPDATE/DELETE
    on. Returns the inserted id."""
    tenant_id = uuid.uuid4()
    row = await conn.fetchrow(
        """
        INSERT INTO audit_logs (tenant_id, action, created_at)
        VALUES ($1, $2, $3)
        RETURNING id
        """,
        tenant_id,
        "pg_integration_test.seed",
        datetime.now(UTC),
    )
    assert row is not None
    return int(row["id"])


@pytest.fixture
async def pg_conn() -> asyncpg.Connection:
    """Yield a raw asyncpg connection to the configured Postgres, or skip."""
    dsn = _postgres_dsn_or_skip()
    if not await _can_connect(dsn):
        pytest.skip(
            f"Postgres at {dsn!r} is not reachable. Start it with `make up` "
            f"and re-run."
        )
    conn = await asyncpg.connect(dsn)
    try:
        yield conn
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_postgres_trigger_rejects_update(pg_conn: asyncpg.Connection) -> None:
    """UPDATE on audit_logs raises the trigger exception."""
    row_id = await _insert_one_row(pg_conn)

    with pytest.raises(asyncpg.PostgresError) as exc_info:
        await pg_conn.execute(
            "UPDATE audit_logs SET action = $1 WHERE id = $2",
            "tampered",
            row_id,
        )

    msg = str(exc_info.value).lower()
    assert "append-only" in msg, (
        f"expected 'append-only' in trigger error message, got: {exc_info.value!r}"
    )


@pytest.mark.asyncio
async def test_postgres_trigger_rejects_delete(pg_conn: asyncpg.Connection) -> None:
    """DELETE on audit_logs raises the trigger exception."""
    row_id = await _insert_one_row(pg_conn)

    with pytest.raises(asyncpg.PostgresError) as exc_info:
        await pg_conn.execute(
            "DELETE FROM audit_logs WHERE id = $1",
            row_id,
        )

    msg = str(exc_info.value).lower()
    assert "append-only" in msg, (
        f"expected 'append-only' in trigger error message, got: {exc_info.value!r}"
    )


@pytest.mark.asyncio
async def test_postgres_trigger_exists_in_pg_catalog(pg_conn: asyncpg.Connection) -> None:
    """Sanity-check the trigger is installed on the right table.

    Belt-and-braces in case a future migration accidentally drops it:
    even before exercising UPDATE/DELETE, fail fast if the trigger row
    is missing from pg_trigger.
    """
    row = await pg_conn.fetchrow(
        """
        SELECT tgname, tgrelid::regclass AS table_name
        FROM pg_trigger
        WHERE tgname = 'annexkit_audit_logs_immutability'
        """
    )
    assert row is not None, (
        "Trigger 'annexkit_audit_logs_immutability' is missing from pg_trigger. "
        "The append-only DB-level guarantee is GONE. Check the latest migration "
        "didn't drop it."
    )
    assert str(row["table_name"]) == "audit_logs"
