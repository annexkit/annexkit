"""FastAPI application entrypoint for the AnnexKit collector.

Deliberately thin. The five jobs of this file are:
    1. Build the FastAPI app with metadata.
    2. Wire CORS + body-size + request-id middleware.
    3. Mount the top-level API router.
    4. Expose ``/health`` and ``/health/ready`` for orchestrators.
    5. Production hardening checks at startup.

Business logic lives in ``app/services/`` — never here.

Run locally:
    uvicorn app.main:app --reload
Via docker-compose:
    docker compose up backend
"""

from __future__ import annotations

import logging
import os
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import api_router
from app.config import Settings, settings
from app.database import engine

logging.basicConfig(
    level=logging.INFO if settings.env != "dev" else logging.DEBUG,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

#: Hard cap on request body size for ``POST /api/v1/spans``.
#: Even a fat span with full retrieval metadata is comfortably under
#: 100KB. Anything in the MB range is a misconfigured SDK or an attack.
MAX_REQUEST_BODY_BYTES = 1 * 1024 * 1024  # 1 MiB


def _assert_production_hardening(s: Settings) -> None:
    """Fail fast if a prod boot is running with insecure defaults."""
    if s.env != "prod":
        return

    problems: list[str] = []

    if "dev-only-insecure" in s.secret_key or len(s.secret_key) < 32:
        problems.append(
            "secret_key is the dev default or too short — set "
            "SECRET_KEY to 32+ random bytes in prod."
        )

    if not s.cors_origins or "*" in s.cors_origins:
        problems.append(
            "cors_origins must be a concrete list of HTTPS frontends in prod — no wildcards."
        )
    elif any(not o.startswith("https://") for o in s.cors_origins):
        problems.append(f"cors_origins must all use https:// in prod — got {s.cors_origins!r}.")

    if problems:
        raise RuntimeError("Production hardening checks failed:\n  - " + "\n  - ".join(problems))


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Tag every request with an ``X-Request-Id`` (incoming or generated).

    The id is stored on ``request.state.request_id`` so handlers /
    services can include it in structured logs, and echoed in the
    response so the user can quote it in a bug report.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Log unhandled exceptions server-side; return a sanitised 500.

    FastAPI's default behaviour returns a generic 500 to the client (no
    leak), but it does NOT log a stack trace anywhere — so a real
    incident is invisible until a customer reports. This middleware
    closes that gap by emitting `logger.exception` with the request_id
    and the route, then letting the exception bubble to FastAPI's
    default handler so the client still gets the canonical 500 body.

    HTTPException (4xx/5xx the route raised on purpose) is NOT caught —
    those carry their intended status and don't need an incident log.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # Intentional 4xx/5xx from the route — let FastAPI handle it
            # without logging an incident.
            raise
        except Exception:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.exception(
                "Unhandled exception in route %s %s (request_id=%s)",
                request.method,
                request.url.path,
                request_id,
            )
            # Re-raise so FastAPI's default 500 handler responds with the
            # canonical body. The client never sees the stack trace.
            raise


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose declared Content-Length exceeds the cap.

    A streaming attacker that lies in the header still has to deliver
    the bytes to overflow — uvicorn's default settings keep that
    finite. This middleware is a cheap first gate for the honest case.
    """

    def __init__(self, app: FastAPI, max_bytes: int) -> None:
        super().__init__(app)
        self._max_bytes = max_bytes

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > self._max_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request body too large"},
                    )
            except ValueError:
                # Malformed Content-Length — let the body parser handle it.
                pass
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Startup/shutdown hooks. Keep startup fast — uvicorn waits for it."""
    _assert_production_hardening(settings)
    logger.info(
        "AnnexKit API starting (env=%s, version=%s)",
        settings.env,
        settings.app_version,
    )
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "EU AI Act compliance pipeline for developers. Ingest LLM telemetry "
        "via the AnnexKit SDK, classify AI systems against AI Act risk tiers, "
        "and generate audit-ready Annex IV technical documentation."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Order matters: CORS first so preflight responses also get the
# Request-Id header; size limit before everything so bogus huge requests
# don't even reach the route resolver.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)
# Error logging sits between RequestId and BodySizeLimit so the request_id
# is already on request.state when an exception lands in the logs.
app.add_middleware(ErrorLoggingMiddleware)
app.add_middleware(BodySizeLimitMiddleware, max_bytes=MAX_REQUEST_BODY_BYTES)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness probe — cheap, no I/O."""
    return {
        "status": "ok",
        "service": "annexkit-api",
        "version": settings.app_version,
    }


@app.get("/health/ready", tags=["meta"])
async def health_ready() -> JSONResponse:
    """Readiness probe — checks DB + document storage are available.

    Distinct from ``/health``: liveness asks "is the process alive?",
    readiness asks "is the process able to serve traffic?". Failures
    return 503 so a load balancer drops the instance without restarting.
    """
    checks: dict[str, dict[str, str]] = {}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = {"status": "ok"}
    except Exception as exc:
        checks["database"] = {"status": "fail", "error": str(exc)[:200]}

    storage = Path(settings.document_storage_path)
    try:
        if storage.exists():
            if not os.access(storage, os.W_OK):
                raise PermissionError(f"{storage} is not writable")
        else:
            storage.mkdir(parents=True, exist_ok=True)
        checks["document_storage"] = {"status": "ok"}
    except Exception as exc:
        checks["document_storage"] = {
            "status": "fail",
            "error": str(exc)[:200],
        }

    overall_ok = all(c["status"] == "ok" for c in checks.values())
    payload: dict[str, object] = {
        "status": "ok" if overall_ok else "fail",
        "service": "annexkit-api",
        "version": settings.app_version,
        "checks": checks,
    }
    return JSONResponse(
        content=payload,
        status_code=200 if overall_ok else 503,
    )
