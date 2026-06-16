"""Seed a fresh tenant + API key in the local dev database.

Run via the Makefile (recommended):

    make seed

…which execs this inside the backend container so it has the right
deps + DATABASE_URL.

The script prints the plaintext API key on success — copy it
immediately, the hash-only DB row will not let you recover it.
"""

from __future__ import annotations

import asyncio
import sys
from uuid import uuid4

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.tenant import ApiKey, Tenant
from app.services import api_key as api_key_service


async def main() -> int:
    if settings.env != "dev":
        # Hard guard: this script prints a fresh API key plaintext to
        # stdout, which is fine for local development but unacceptable
        # against staging or production databases.
        print(
            f"ERROR: seed_tenant is dev-only — refusing to run with "
            f"ENV={settings.env!r}.",
            file=sys.stderr,
        )
        print(
            "  Set ENV=dev in the environment, or use the (forthcoming) "
            "admin UI to mint tenants in non-dev environments.",
            file=sys.stderr,
        )
        return 2

    slug = f"dev-{uuid4().hex[:6]}"
    async with AsyncSessionLocal() as session:
        tenant = Tenant(name="Dev Seed", slug=slug)
        session.add(tenant)
        await session.flush()

        generated = api_key_service.generate()
        session.add(
            ApiKey(
                tenant_id=tenant.id,
                name="dev",
                key_prefix=generated.prefix,
                key_hash=generated.key_hash,
            )
        )
        await session.commit()

    print(f"tenant_id={tenant.id}")
    print(f"tenant_slug={slug}")
    print(f"api_key={generated.plaintext}")
    print()
    print("Copy api_key now — it is hashed in the DB and unrecoverable.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
