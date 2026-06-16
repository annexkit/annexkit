"""Async SQLAlchemy engine + session factory.

Why async? Because FastAPI is ASGI and we want the event loop to stay
unblocked while waiting on Postgres. If we used a sync driver, every DB call
would pin a thread.

This module exposes three things:
    - `engine`      : the process-wide async engine (one per worker process).
    - `AsyncSessionLocal` : a factory that creates short-lived sessions.
    - `get_session()`     : a FastAPI dependency that yields a session and
                            commits or rolls back automatically.

Usage in a route:
    @router.get("/")
    async def handler(session: AsyncSession = Depends(get_session)): ...
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# `echo=True` in dev prints every SQL statement. Very useful for debugging;
# very noisy in prod. Driven off the env flag in config.
engine = create_async_engine(
    settings.database_url,
    echo=(settings.env == "dev"),
    # pool_pre_ping catches stale connections after Postgres restarts.
    pool_pre_ping=True,
    future=True,
)

# `expire_on_commit=False` — after commit, instances stay usable. Without it,
# attribute access on a committed object fires a new query. Cleaner for APIs.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Declarative base all ORM models inherit from.

    Keep it here rather than scattered across models/ so that Alembic's
    autogenerate can import a single `Base.metadata` and see every table.
    """


async def get_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that yields a transactional session.

    Contract:
        - Opens a session.
        - Yields it to the route handler.
        - On successful return: commits.
        - On any exception: rolls back.
        - Always: closes the session.

    This means route handlers never need to call `session.commit()` manually;
    a successful response implies a successful commit. If you need to split
    work into multiple transactions, use `async with session.begin_nested()`.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
