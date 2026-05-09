"""Shared pytest fixtures for the backend test suite.

Strategy: every test gets a brand-new in-memory SQLite database, set up
via ``Base.metadata.create_all``. Postgres-only features (the audit-log
trigger, JSONB-specific operators) are exercised by the migration in
prod; tests assert the service layer's contract instead.

Two fixtures matter:

  * :func:`db_session` — a fresh ``AsyncSession`` bound to a per-test
    in-memory DB. Yields the session for direct ORM queries in tests.
  * :func:`client` — a FastAPI ``AsyncClient`` whose ``get_session``
    dependency is overridden to return the same ``db_session``, so
    HTTP round-trips and direct ORM reads see the same transaction.

A third (:func:`authenticated_tenant`) seeds a tenant + valid API key
and returns ``(tenant, plaintext_key)`` so a test can immediately make
authed requests.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.deps import get_session
from app.database import Base
from app.main import app
from app.models.tenant import ApiKey, Tenant
from app.services import api_key as api_key_service


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Yield a fresh ``AsyncSession`` against an in-memory SQLite DB.

    Per-test isolation: each test gets its own engine + schema. No shared
    state, no cleanup required. Disposal happens after the test returns.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """FastAPI client with the DB dependency wired to ``db_session``."""

    async def _override() -> AsyncGenerator[AsyncSession]:
        # Yield the same session the test already holds — we don't open
        # a second one (would deadlock on a single-connection SQLite).
        # Note: ``get_session`` normally commits; here the test session
        # is committed explicitly by the test or rolled back at teardown.
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(get_session, None)


@pytest.fixture
async def authenticated_tenant(db_session: AsyncSession) -> tuple[Tenant, str]:
    """Seed a tenant + a valid API key. Return ``(tenant, plaintext_key)``.

    We **commit** here (not just flush) so the seeded data survives any
    rollback the route under test triggers. Without this, a test that
    POSTs to a path that legitimately raises (e.g. 401) would also lose
    the seed because the override session rolls back on raise.
    """
    tenant = Tenant(name="Acme Test", slug="acme-test")
    db_session.add(tenant)
    await db_session.flush()

    generated = api_key_service.generate()
    db_session.add(
        ApiKey(
            tenant_id=tenant.id,
            name="default",
            key_prefix=generated.prefix,
            key_hash=generated.key_hash,
        )
    )
    await db_session.commit()

    return tenant, generated.plaintext
