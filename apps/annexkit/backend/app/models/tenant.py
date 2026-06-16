"""Tenant + ApiKey ORM models.

A **tenant** is the owner of spans, AI systems, audit log entries, and
API keys. One organisation typically maps to one tenant. The schema is
intentionally minimal in v0 — billing, multi-user, SSO all land later.

An **API key** is the credential the SDK presents in
``Authorization: Bearer ak_...``. We never store the plaintext key —
only an HMAC-SHA256 hash, plus the visible ``ak_xxxxxxxx`` prefix for
identification in dashboards / logs.

Generation, hashing, and verification helpers live in
``app/services/api_key.py`` — this module is just the data layer.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import created_at_column, updated_at_column, uuid_pk


class Tenant(Base):
    """An organisation that owns API keys, spans, audit log entries."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = uuid_pk()

    # Human-friendly display name (e.g. "Velmara Bank Compliance").
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # URL slug — kebab-case, unique across the whole DB. Used to
    # construct trust-center URLs like
    # ``https://<slug>.annexkit.eu/trust``.
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()


class ApiKey(Base):
    """An HMAC-hashed credential bound to a tenant.

    The plaintext key (``ak_<24-char-suffix>``) is shown to the user
    exactly once — at generation time. Only ``key_hash`` and
    ``key_prefix`` persist. Verification is constant-time
    (``hmac.compare_digest``).
    """

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = uuid_pk()

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # User-set label so a tenant with many keys can identify them.
    # E.g. "production", "staging", "alice's laptop".
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # First ~11 chars of the plaintext key (e.g. ``ak_abc12345``).
    # Visible in dashboards. Indexed because a tenant might list keys
    # filtered by prefix.
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # HMAC-SHA256(SECRET_KEY, full_key), hex-encoded — 64 chars.
    # Unique because two collisions would mean a (vanishingly unlikely)
    # SHA-256 collision *plus* same secret. The unique index also makes
    # the auth lookup an O(1) B-tree probe.
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    # Best-effort timestamp of last successful auth. Updated in the
    # auth dependency. Nullable: a freshly generated key has no usage yet.
    last_used_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # When non-null, this key is revoked and auth must reject it.
    # We don't delete revoked keys — keeping them lets us trace
    # "which key signed which span" for forensic queries.
    revoked_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()
