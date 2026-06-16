import type { NextConfig } from "next";

/**
 * Next.js 16 — Turbopack is the default bundler; no `experimental.turbo`
 * flag needed. The `middleware` lifecycle was renamed to `proxy` in v16
 * (we don't use it yet but it's worth knowing if you add one).
 *
 * Rewrites — same-origin /api/* → backend:
 *   In prod, Caddy already routes /api/* to the backend container,
 *   so the rewrite never fires (the request never reaches Next.js).
 *   In compose dev (frontend :3001, backend :8033) and host dev
 *   (frontend :3000, backend :8033), Next.js proxies /api/* to the
 *   BACKEND_URL env var. Browser sees same-origin → no CORS dance,
 *   no NEXT_PUBLIC_* baked at build time, no env shenanigans.
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Standalone output keeps the Docker image lean — only what next start
  // needs goes into the runtime container.
  output: "standalone",
  // No img domains needed yet; trust pages render no remote images.
  images: { remotePatterns: [] },
  // NOTE on /api/* routing:
  //   We deliberately do NOT use a `rewrites()` here — Next.js
  //   standalone bakes rewrite destinations at build time, so the
  //   BACKEND_URL env var at container runtime is ignored. Instead,
  //   src/app/api/[...path]/route.ts proxies /api/* to BACKEND_URL
  //   at request time. Works identically in compose dev (BACKEND_URL=
  //   http://backend:8000), host dev (http://localhost:8033), and
  //   prod (where Caddy fronts /api/* and the proxy is never hit).
};

export default nextConfig;
