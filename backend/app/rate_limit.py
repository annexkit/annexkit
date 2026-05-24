"""Process-wide rate-limit singleton.

Lives in its own module (rather than ``app/main.py``) so route modules
can import ``limiter`` without a circular dependency on ``main`` — see
``app/api/trust.py`` for the consumer.

Today: in-memory storage. Each backend process tracks limits
independently. Fine until we run >1 backend instance, at which point
switch to a Redis backend:

    Limiter(key_func=get_remote_address, storage_uri="redis://...")

The client IP comes from ``get_remote_address`` which reads
``request.client.host``. Behind Cloudflare + Caddy the real IP must
be forwarded — Cloudflare sets ``CF-Connecting-IP`` and Caddy
proxies it through; uvicorn needs ``--forwarded-allow-ips`` set to
the trust boundary for ``request.client.host`` to reflect it.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
