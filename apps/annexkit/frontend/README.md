# annexkit-frontend

Next.js 16 trust-center frontend. Renders the public surfaces backed by
`/api/v1/trust/*` on the AnnexKit collector.

Routes:

| Path | What it shows |
|---|---|
| `/` | Project landing — links to GitHub, demo trust page placeholder. |
| `/trust/[slug]` | One tenant: name, system count, tier breakdown, list of declared AI systems with risk badges. |
| `/trust/[slug]/systems/[systemId]` | One AI system: declared purpose, classifier reasoning (bilingual EN/IT), redacted provider info, lifecycle dates. |

## Stack

- **Next.js 16** (App Router, Turbopack default, React 19)
- **TypeScript** strict
- **Tailwind 4** (`@import "tailwindcss"`, no `tailwind.config.ts`
  needed — theme via `@theme` in CSS)

No client-side state, no shadcn/ui yet — every page is a server
component that fetches from the backend on each request. Add a
client island when interactivity actually needs one.

## Environment

| Var | Default | Purpose |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8033` | Where the Next.js process resolves the collector. In Docker compose this is `http://backend:8000`. |

## Development

From this directory:

```bash
npm install
BACKEND_URL=http://localhost:8033 npm run dev
# Then open http://localhost:3000
```

The collector must be running (`make up` from the project root).

To inspect a real trust page after running the demo:

```bash
make demo-seed       # in another terminal — prints the seeded slug
# Open http://localhost:3000/trust/<that-slug>
```

## Production

The Dockerfile produces a standalone Next.js 16 bundle. Compose mounts
this on `:3001` (host) → `:3000` (container) — see
[`../docker-compose.yml`](../docker-compose.yml).

## License

AGPL-3.0-only — same as the backend (see
[`../backend/LICENSE`](../backend/LICENSE)).
