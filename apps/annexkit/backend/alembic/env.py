"""Alembic migration environment — async-aware.

Two things make this file non-standard:

1. It drives an **async** SQLAlchemy engine (asyncpg). Alembic's own
   `run_migrations_online` is synchronous, so we run it inside
   `connection.run_sync(...)` — Alembic stays happy, asyncpg stays async.

2. The DB URL comes from `app.config.settings`, not from alembic.ini. One
   source of truth: whatever the app uses, migrations use.

Run locally (from /app inside the backend container):
    alembic upgrade head         # apply all pending migrations
    alembic revision --autogenerate -m "add users"  # new migration
"""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Make `app` importable when this file runs from /app/alembic (docker) or
# from backend/ (host). Adds the parent of alembic/ to sys.path.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import app.models  # noqa: F401,E402  -- side-effect import so every model is registered
from app.config import settings  # noqa: E402  (sys.path adjusted just above)
from app.database import Base  # noqa: E402

# Alembic Config object, providing access to values within the .ini file.
config = context.config

# Inject the real DB URL so autogenerate can connect.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configure logging from alembic.ini if it was given one.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# `target_metadata` is what autogenerate diffs the live schema against.
# Every model module must have been imported by now so all tables are here.
target_metadata = Base.metadata


# -------------------------------------------------------------------------
# Offline mode — emits SQL to stdout without touching a DB.
# Rarely used; handy for generating .sql files for DBAs to review.
# -------------------------------------------------------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # detect column type changes, not just name changes
    )
    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------------------------------
# Online mode — opens an async engine, wraps the sync Alembic migration
# runner inside `connection.run_sync(...)`.
# -------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        # Alembic will render a `server_default` diff unless we tell it to.
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        future=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


# Entrypoint.
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
