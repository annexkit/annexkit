# --------------------------------------------------------------------------
# AnnexKit collector — backend Dockerfile
# --------------------------------------------------------------------------
# Mirrors Konformia's Dockerfile: uv for dependency management, two-layer
# build (deps cached separately from app code), WeasyPrint native deps for
# the Annex IV PDF renderer.
# --------------------------------------------------------------------------

FROM python:3.14-slim-bookworm AS base

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
COPY pyproject.toml ./
# uv.lock will land after `uv lock` is first run; both are copied if present.
COPY uv.lock* ./

RUN uv sync --no-dev --no-install-project

# Application layer — copied last so code edits don't bust deps cache.
COPY . .

RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
