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
        fmt lint clean \
        prod-check prod-deploy prod-deploy-backend prod-deploy-frontend \
        prod-ps prod-logs prod-logs-backend prod-logs-frontend prod-logs-db \
        prod-migrate prod-db-shell prod-db-backup \
        prod-restart prod-restart-backend prod-restart-frontend \
        prod-shell prod-status prod-env-edit

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

# =========================================================================
# Production deploy — Hetzner VPS (co-hosted with Konformia)
# -------------------------------------------------------------------------
# AnnexKit shares a VPS with Konformia. The Konformia stack runs Caddy +
# Cloudflare ACME; AnnexKit joins the `konformia_default` Docker network
# so Caddy can reverse-proxy `annexkit.dev` to `annexkit-backend:8000`
# and `annexkit-frontend:3000`. Full architecture in
# ~/Desktop/AnnexKit-internal-docs/annexkit-deployment-runbook.md.
#
# Deploy is git-pull-based: a `prod-deploy` SSHes to the VPS, runs
# `git pull` against the AnnexKit repo on the server, then
# `docker compose up -d --build`. Simpler than Konformia's rsync flow
# because the AnnexKit repo is already cloned at $(VPS_PROJECT_PATH).
#
# Set VPS_HOST once. Options:
#   1. Per-command:   make prod-ps VPS_HOST=konformia-prod-01
#   2. Shell export:  export VPS_HOST=konformia-prod-01
#                     (add to ~/.zshrc to persist)
#   3. Local file:    create `.envrc` next to this Makefile with:
#                       export VPS_HOST=konformia-prod-01
#                     (gitignored — never committed)
#
# CADDY: managed in the Konformia repo. To touch the Caddyfile or
# restart Caddy, work from /Users/mykael/PycharmProjects/Konformia.
# This Makefile intentionally has NO `prod-restart-caddy` target.
# =========================================================================

VPS_USER ?= root
VPS_HOST ?=
VPS_PROJECT_PATH ?= /home/annexkit/annexkit
COMPOSE_PROD := docker compose -f docker-compose.yml -f docker-compose.prod.yml
SSH := ssh $(VPS_USER)@$(VPS_HOST)

# Computed at make-invocation time. Format: <semver>+<git-sha-short>-<utc-stamp>.
# Examples: 0.1.0+a1b2c3d-20260523T1630, 0.1.0+a1b2c3d-dirty-... if the working
# tree has uncommitted changes. Override at the CLI with:
#     make prod-deploy APP_VERSION=0.2.0-rc1
APP_VERSION ?= 0.1.0+$(shell git rev-parse --short HEAD 2>/dev/null || echo nogit)-$(shell date -u +%Y%m%dT%H%M)$(shell git diff --quiet 2>/dev/null || echo -dirty)

prod-check: ## Verify VPS_HOST is set before running prod commands
	@if [ -z "$(VPS_HOST)" ]; then \
		echo "ERROR: VPS_HOST is not set."; \
		echo "Set it once with:  export VPS_HOST=konformia-prod-01"; \
		echo "Or pass per-call:  make prod-ps VPS_HOST=konformia-prod-01"; \
		exit 1; \
	fi
	@echo "-> VPS: $(VPS_USER)@$(VPS_HOST)"

# --- Deploy --------------------------------------------------------------

prod-deploy: prod-check ## Full deploy: git pull + rebuild + migrate (~2 min)
	@echo "-> Version: $(APP_VERSION)"
	@echo "-> git pull on $(VPS_HOST)..."
	$(SSH) 'cd $(VPS_PROJECT_PATH) && git pull --ff-only'
	@echo "-> Building & restarting containers..."
	$(SSH) 'cd $(VPS_PROJECT_PATH) && APP_VERSION=$(APP_VERSION) $(COMPOSE_PROD) up -d --build'
	@echo "-> Applying DB migrations..."
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) exec -T backend uv run alembic upgrade head'
	@echo "Deploy complete (version=$(APP_VERSION)). Verify with: make prod-status"

prod-deploy-backend: prod-check ## Deploy only the backend (faster — skips frontend rebuild)
	@echo "-> Version: $(APP_VERSION)"
	$(SSH) 'cd $(VPS_PROJECT_PATH) && git pull --ff-only && APP_VERSION=$(APP_VERSION) $(COMPOSE_PROD) up -d --build backend && $(COMPOSE_PROD) exec -T backend uv run alembic upgrade head'
	@echo "Backend deployed (version=$(APP_VERSION))."

prod-deploy-frontend: prod-check ## Deploy only the frontend
	$(SSH) 'cd $(VPS_PROJECT_PATH) && git pull --ff-only && $(COMPOSE_PROD) up -d --build frontend'
	@echo "Frontend deployed."

# --- Monitoring ----------------------------------------------------------

prod-ps: prod-check ## Status of all production containers
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) ps'

prod-logs: prod-check ## Tail logs from every prod service (Ctrl+C to exit)
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) logs -f --tail 50'

prod-logs-backend: prod-check ## Tail backend logs only (live, Ctrl+C to exit)
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) logs -f --tail 100 backend'

prod-logs-frontend: prod-check ## Tail frontend logs only
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) logs -f --tail 100 frontend'

prod-logs-db: prod-check ## Tail database logs only
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) logs -f --tail 100 db'

prod-status: prod-check ## Quick external health check from your laptop
	@# /health is intentionally NOT exposed via Caddy (security — internal
	@# orchestrator probe only). Public canaries are /api/v1/ping (backend)
	@# and / (frontend).
	@echo "-> API ping (backend):"
	@curl -s -o /dev/null -w "  HTTP %{http_code}  (%{time_total}s)\n" https://annexkit.dev/api/v1/ping
	@echo "-> Frontend home:"
	@curl -s -o /dev/null -w "  HTTP %{http_code}  (%{time_total}s)\n" https://annexkit.dev/
	@echo "-> Internal /health (via SSH — bypass Cloudflare/Caddy):"
	@$(SSH) 'curl -sf http://localhost:8033/health || curl -sf http://localhost:8000/health 2>/dev/null || docker exec annexkit-backend curl -sf http://localhost:8000/health' 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "  (skipped — VPS unreachable)"

# --- Database ------------------------------------------------------------

prod-migrate: prod-check ## Apply pending Alembic migrations on prod DB
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) exec -T backend uv run alembic upgrade head'

prod-db-shell: prod-check ## Open psql against the prod database (read-write — be careful)
	$(SSH) -t 'docker exec -it annexkit-db psql -U annexkit -d annexkit'

prod-db-backup: prod-check ## pg_dump prod DB to a local timestamped .sql.gz
	@mkdir -p backups
	@FILE="backups/annexkit-$$(date +%Y%m%d-%H%M%S).sql.gz"; \
	echo "-> Dumping to $$FILE..."; \
	$(SSH) 'docker exec annexkit-db pg_dump -U annexkit annexkit' | gzip > $$FILE; \
	echo "Backup saved: $$FILE ($$(du -h $$FILE | cut -f1))"

# --- Restarts ------------------------------------------------------------

prod-restart: prod-check ## Restart all prod services WITH .env reload (force-recreate, no rebuild)
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) up -d --force-recreate --no-deps backend frontend'

prod-restart-backend: prod-check ## Recreate backend container (picks up .env changes)
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) up -d --force-recreate --no-deps backend'

prod-restart-frontend: prod-check ## Recreate frontend container (picks up .env changes)
	$(SSH) 'cd $(VPS_PROJECT_PATH) && $(COMPOSE_PROD) up -d --force-recreate --no-deps frontend'

# --- Manual access -------------------------------------------------------

prod-shell: prod-check ## SSH into the VPS as the configured user (default: root)
	$(SSH)

prod-env-edit: prod-check ## Open the prod .env in nano via SSH (careful — secrets)
	$(SSH) -t 'nano $(VPS_PROJECT_PATH)/.env'
