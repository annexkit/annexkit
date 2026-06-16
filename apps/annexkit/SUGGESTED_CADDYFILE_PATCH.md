# Suggested Caddyfile patch — expose `/health` for the AnnexKit block

> This file is a **suggestion**, not an applied change. The Caddyfile
> lives in the Konformia repo (`/home/konformia/Konformia/Caddyfile`
> on the VPS, `/Users/mykael/PycharmProjects/Konformia/Caddyfile`
> locally). Apply only if you want `/health` to be a public probe.

## Current behaviour

The annexkit block in Konformia's Caddyfile routes only
`/api/*`, `/docs`, `/openapi.json` to the backend; everything else
goes to the Next.js frontend. So:

| URL | Currently | Why |
|---|---|---|
| `https://annexkit.dev/api/v1/ping` | 200 (backend) | matches `@api` |
| `https://annexkit.dev/api/v1/spans` | 200/401 (backend) | matches `@api` |
| `https://annexkit.dev/health` | 404 (frontend has no `/health` route) | falls through to frontend handler |
| `https://annexkit.dev/openapi.json` | 200 (backend) | matches `@api` |
| `https://annexkit.dev/` | 200 (frontend trust home) | falls through to frontend handler |

The runbook §1.1 listed `https://annexkit.dev/health` as "live", but
the Caddy config never matched it. The runbook is now updated to
reflect this (intentional design: keep the liveness probe internal).

## Three options

### Option A — keep `/health` private (current, **recommended**)

Don't change anything. Use `make prod-status` from the AnnexKit repo,
which combines:
- Public canary: `GET https://annexkit.dev/api/v1/ping` (proves Cloudflare → Caddy → backend works)
- Internal probe: `ssh root@konformia-prod-01 docker exec annexkit-backend curl http://localhost:8000/health` (proves the readiness JSON is healthy)

This is the right default for a small product: exposing a generic
`/health` JSON to the world gives attackers a probe surface for
fingerprinting + version disclosure (we leak `app_version` in the
body).

### Option B — expose `/health` as a public liveness probe

If you want `/health` reachable from external uptime monitors
(UptimeRobot, BetterStack, Pingdom):

```diff
 annexkit.dev, www.annexkit.dev {
-    @api path /api/* /docs /openapi.json
+    @api path /api/* /docs /openapi.json /health
     handle @api {
         reverse_proxy annexkit-backend:8000
     }
     handle {
         reverse_proxy annexkit-frontend:3000
     }
     encode gzip zstd
 }
```

Then `https://annexkit.dev/health` returns the JSON liveness body.
Worth doing in M2 when you wire UptimeRobot (runbook §6 TODO).

### Option C — expose a narrow `/healthz` that drops the version

If you don't want to leak `app_version` but want external monitoring,
add a new endpoint server-side that returns just `{"status":"ok"}`
without version, then route it:

```diff
 annexkit.dev, www.annexkit.dev {
-    @api path /api/* /docs /openapi.json
+    @api path /api/* /docs /openapi.json /healthz
     ...
 }
```

Server-side (in `backend/app/main.py`):
```python
@app.get("/healthz", tags=["meta"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
```

This is what Kubernetes etc. expect (`/healthz` is the canonical
liveness path; `/health` is more of a Spring/FastAPI convention).

## Recommendation

- **Now**: keep Option A (don't touch the Caddyfile). Use
  `make prod-status`.
- **When you wire UptimeRobot in M2**: switch to Option C
  (`/healthz`, no version leak). Take ~20 minutes total: add the
  endpoint + Caddyfile patch + UptimeRobot config.
- **Skip Option B** unless you have a specific reason — leaking
  `app_version` publicly is a small recon win for attackers.

## How to apply Option C if you go for it

1. In `/Users/mykael/PycharmProjects/AnnexKit/backend/app/main.py`,
   add the `/healthz` route shown above.
2. Bump `app_version` if relevant.
3. SSH to the VPS, edit `/home/konformia/Konformia/Caddyfile`, add
   `/healthz` to the `@api` matcher in the `annexkit.dev` block.
4. From the Konformia repo: `make prod-restart-caddy` (or
   `docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile`).
5. From the AnnexKit repo: `make prod-deploy-backend` to ship the
   new endpoint.
6. Verify: `curl https://annexkit.dev/healthz` → `{"status":"ok"}`.
7. Update [AUDIT.md](AUDIT.md) F4 row if relevant.
