"""Shared ORM building blocks.

Re-usable column types and mixins go here so every table doesn't re-declare
its own `id` / `created_at` boilerplate.

Keep this file small — if something is only used by two models, inline it
in one and let the other copy. Premature abstraction is worse than
duplication.

Dialect-agnostic note: we use `sqlalchemy.Uuid` (2.0+) so the models work
on both Postgres (native `uuid`) and SQLite (`CHAR(32)`) — the latter is
what unit tests hit. Production JSON columns get the Postgres-specific
`JSONB` variant via `.with_variant()` in the models themselves.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

# Reusable type alias. Uuid(as_uuid=True) means Python `uuid.UUID` objects
# in Python, native UUID in Postgres, CHAR(32) in SQLite.
UUIDpk = Uuid(as_uuid=True)


def uuid_pk() -> Mapped[uuid.UUID]:
    """Standard UUIDv4 primary key.

    We rely on a Python-side default rather than a server-side one. Reason:
    `gen_random_uuid()` is Postgres-only. SQLAlchemy 2.0's `Uuid` type
    renders correctly on every dialect when the value is generated Python-side.
    In prod the CPU cost is negligible (UUID4 is a one-liner) and we never
    insert from raw SQL except in migrations.
    """
    return mapped_column(
        UUIDpk,
        primary_key=True,
        default=uuid.uuid4,
    )


def created_at_column() -> Mapped[datetime]:
    """`created_at TIMESTAMPTZ DEFAULT now()`.

    `TIMESTAMPTZ` everywhere — never naive timestamps. Postgres stores UTC
    and converts on output; naive datetimes bite you the day you deploy
    to a different timezone.
    """
    return mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


def updated_at_column() -> Mapped[datetime]:
    """`updated_at TIMESTAMPTZ`.

    Updated via `onupdate=` so SQLAlchemy refreshes the value on every
    UPDATE statement, transparently. Both server and Python sides are
    wired so the in-memory attribute stays populated after a flush —
    without the Python callable, async routes that mutate+return an ORM
    row hit "MissingGreenlet" when Pydantic lazy-loads the expired
    attribute.
    """
    now = lambda: datetime.now(UTC)  # noqa: E731
    return mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        onupdate=now,
        default=now,
        nullable=False,
    )
