# annexkit-backend

The collector + Annex IV API for [AnnexKit](../README.md).

This package is **not** published to PyPI — it ships only as a Docker
image. The matching dev-facing SDK is in [`../sdk`](../sdk).

## Run locally

From the repo root:

```bash
cp .env.example .env
make up                  # docker compose up --build
curl http://localhost:8033/health
```

See [`../README.md`](../README.md) for the full project overview and
[`../docs/ANNEXKIT_PLAN.md`](../docs/ANNEXKIT_PLAN.md) for the strategic
plan + 12-month roadmap.

## Project layout

```
backend/
├── app/
│   ├── api/         FastAPI route modules (thin controllers)
│   ├── data/        Static datasets (annex_iii.json — regulatory ruleset, do not edit casually)
│   ├── models/      SQLAlchemy ORM (audit_log is APPEND-ONLY)
│   ├── services/    Business logic (risk_engine, annex, mistral_client, ...)
│   ├── schemas/     Pydantic request/response shapes
│   ├── templates/   Jinja templates for Annex IV PDF rendering
│   ├── config.py    pydantic-settings — env-driven configuration
│   ├── database.py  Async SQLAlchemy engine + session factory
│   └── main.py      FastAPI entrypoint, CORS, /health, lifespan
├── alembic/         Async migration environment
├── tests/           pytest suite — `make backend-test`
├── pyproject.toml   uv-managed deps, ruff + pytest config
└── Dockerfile       Multi-stage build, WeasyPrint native deps
```

## Dependencies of note

- **fastapi** + **uvicorn[standard]** — async web stack.
- **sqlalchemy[asyncio]** + **asyncpg** — async DB layer.
- **pgvector** — reserved for prompt-template semantic matching (M5+).
- **alembic** — schema migrations, async-aware via `alembic/env.py`.
- **mistralai** — EU-hosted LLM advisor for ambiguous risk classifications.
- **weasyprint** — Annex IV PDF renderer (HTML → PDF).
- **jinja2** — Annex IV / DoC / FRIA templates.

## Disclaimer

AnnexKit is not a law firm. The Annex IV documents and risk
classifications it produces are technical evidence; interpretation is
the responsibility of your legal team or external counsel.
