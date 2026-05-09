# =========================================================================
# AnnexKit dev Makefile
# -------------------------------------------------------------------------
# One command per common chore. Run `make help` for the full list.
# Production deploy targets land in Day 7+ once we cut a release.
# =========================================================================

.PHONY: help dev up down logs ps restart \
        backend-shell backend-logs backend-test \
        db-shell db-migrate db-revision db-reset \
        sdk-test sdk-build sdk-publish-test \
        frontend-dev frontend-build frontend-logs \
        health seed smoke demo demo-seed \
        fmt lint clean

.DEFAULT_GOAL := help

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*##"; printf "\nAnnexKit dev commands:\n"} \
	/^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# --- Docker Compose ------------------------------------------------------

dev: up ## Alias for `up`

up: ## Start the dev stack (db + collector backend) with live reload
	docker compose up --build

down: ## Stop containers (keeps the DB volume)
	docker compose down

logs: ## Tail logs from every compose service
	docker compose logs -f

ps: ## List compose services and their status
	docker compose ps

restart: ## Restart the backend without touching the DB
	docker compose restart backend

# --- Backend -------------------------------------------------------------

backend-shell: ## Drop into a bash shell inside the backend container
	docker compose exec backend bash

backend-logs: ## Tail only the backend logs
	docker compose logs -f backend

backend-test: ## Run pytest inside the backend container
	docker compose exec backend uv run pytest -v

# --- Database ------------------------------------------------------------

db-shell: ## Open a psql prompt against the dev database
	docker compose exec db psql -U annexkit -d annexkit

db-migrate: ## Apply all pending Alembic migrations
	docker compose exec backend uv run alembic upgrade head

db-revision: ## Create a new migration: make db-revision m="add spans table"
	@test -n "$(m)" || (echo 'Usage: make db-revision m="message"' && exit 1)
	docker compose exec backend uv run alembic revision --autogenerate -m "$(m)"

db-reset: ## DANGER: wipe DB volume and re-migrate from scratch
	docker compose down -v
	docker compose up -d db
	sleep 3
	$(MAKE) db-migrate

# --- Smoke tests + dev convenience ---------------------------------------

health: ## curl /health on the running backend
	@curl -sS http://localhost:8033/health | python3 -m json.tool

seed: ## Create a test tenant + API key (prints the plaintext key — copy it!)
	@docker compose cp scripts/seed_tenant.py backend:/tmp/seed_tenant.py >/dev/null
	@docker compose exec -T backend uv run python /tmp/seed_tenant.py

smoke: ## Health check + ping + a sample 401 (no key) + a sample 401 (bad key)
	@echo "=== /health ==="; curl -sS http://localhost:8033/health | python3 -m json.tool
	@echo "=== /api/v1/ping ==="; curl -sS http://localhost:8033/api/v1/ping | python3 -m json.tool
	@echo "=== /api/v1/spans without auth (expect 401) ==="; curl -sS -o /dev/null -w "HTTP %{http_code}\n" -X POST http://localhost:8033/api/v1/spans -H 'Content-Type: application/json' -d '{}'

# --- End-to-end demo ----------------------------------------------------

demo: ## Run examples/chatbot-openai end-to-end (collector must be up + ANNEXKIT_API_KEY exported)
	cd examples/chatbot-openai && uv sync --quiet && uv run python chatbot.py

demo-seed: ## One-shot: seed a fresh tenant + run the demo with that key
	@docker compose cp scripts/seed_tenant.py backend:/tmp/seed_tenant.py >/dev/null
	@KEY=$$(docker compose exec -T backend uv run python /tmp/seed_tenant.py 2>/dev/null | grep '^api_key=' | cut -d= -f2); \
	if [ -z "$$KEY" ]; then echo "ERROR: seed failed - is the stack up? Run 'make up' first."; exit 1; fi; \
	echo "Seeded api_key: $$KEY"; \
	cd examples/chatbot-openai && uv sync --quiet && ANNEXKIT_API_KEY=$$KEY uv run python chatbot.py

walkthrough: ## Run the 3-persona test walkthrough end-to-end (seeds tenant + generates 8 output files)
	@docker compose cp scripts/seed_tenant.py backend:/tmp/seed_tenant.py >/dev/null
	@KEY=$$(docker compose exec -T backend uv run python /tmp/seed_tenant.py 2>/dev/null | grep '^api_key=' | cut -d= -f2); \
	if [ -z "$$KEY" ]; then echo "ERROR: seed failed - is the stack up? Run 'make up' first."; exit 1; fi; \
	echo "Seeded api_key: $$KEY"; \
	cd examples/test-walkthrough && uv sync --quiet && ANNEXKIT_API_KEY=$$KEY uv run python walkthrough.py

# --- Frontend (trust center) --------------------------------------------

frontend-dev: ## Run the Next.js dev server on host port 3000 (collector must be up)
	cd frontend && npm install && BACKEND_URL=http://localhost:8033 npm run dev

frontend-build: ## Production build of the Next.js app
	cd frontend && npm install && npm run build

frontend-logs: ## Tail the frontend container logs (when running via compose)
	docker compose logs -f frontend

# --- SDK -----------------------------------------------------------------

sdk-test: ## Run the SDK test suite (host-side, not in Docker)
	cd sdk && uv run pytest -v

sdk-build: ## Build the SDK distribution into sdk/dist/
	cd sdk && uv build

sdk-publish-test: ## Publish to TestPyPI (use for pre-release dry runs)
	cd sdk && uv publish --publish-url https://test.pypi.org/legacy/

sdk-example-basic: ## Run the sync chatbot SDK example (spans on stderr)
	cd sdk && uv run python examples/basic_chatbot.py

sdk-example-async: ## Run the async handler SDK example
	cd sdk && uv run python examples/async_handler.py

sdk-example-session: ## Run the context-manager SDK example
	cd sdk && uv run python examples/with_session.py

# --- Quality -------------------------------------------------------------

fmt: ## Format both backend and SDK with ruff
	cd backend && uv run ruff format .
	cd sdk && uv run ruff format .

lint: ## Lint both backend and SDK with ruff
	cd backend && uv run ruff check .
	cd sdk && uv run ruff check .

clean: ## Remove caches and build artefacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf sdk/dist sdk/build sdk/*.egg-info
