# --------------------------------------------------------------------------
# AnnexKit collector — backend Dockerfile
# --------------------------------------------------------------------------
# Mirrors Konformia's Dockerfile: uv for dependency management, two-layer
# build (deps cached separately from app code), WeasyPrint native deps for
# the Annex IV PDF renderer.
#
# IMPORTANT: the build context is the repo ROOT, not this directory (see the
# `build:` block in docker-compose.yml — context: ../../). That is what lets
# the image include the shared `core/konformia_core` package. All COPY paths
# below are therefore relative to the repo root.
# --------------------------------------------------------------------------

FROM python:3.13-slim-bookworm AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libffi8 \
    libgdk-pixbuf-2.0-0 \
    libjpeg62-turbo \
    shared-mime-info \
    fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

ENV UV_INSTALL_DIR=/usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

# Dependency layer — cached until pyproject.toml/uv.lock changes.
COPY apps/annexkit/backend/pyproject.toml apps/annexkit/backend/uv.lock ./
# --frozen: install EXACTLY what's in uv.lock, never re-resolve at build time
# (reproducible builds + supply-chain safety; matches Konformia's Dockerfile).
RUN uv sync --frozen --no-dev --no-install-project

# Shared compliance engine (konformia_core) — placed beside the app so
# `import konformia_core` resolves. Its deps (pydantic/jinja2/...) are a subset
# of the backend's, so no extra install is needed. Copied before the app since
# it changes less often.
COPY core/konformia_core ./konformia_core

# Application layer — copied last so code edits don't bust the deps cache.
COPY apps/annexkit/backend/ ./

RUN uv sync --frozen --no-dev

# venv on PATH so `uvicorn` resolves; /app on PYTHONPATH so both `app` and the
# placed `konformia_core` package import cleanly.
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
