/**
 * Catch-all proxy for /api/* — forwards to BACKEND_URL at request time.
 *
 * Why this exists:
 *   In prod, Caddy fronts /api/* and routes directly to the backend
 *   container — this handler is never reached. But in compose dev
 *   (frontend :3001, backend :8033 / backend:8000) and host dev
 *   (frontend :3000, backend :8033) there's no Caddy, and the browser
 *   needs same-origin /api/* calls to reach the backend.
 *
 *   We tried `next.config.ts` `rewrites()` — Next.js standalone bakes
 *   destinations at build time, so the BACKEND_URL env var was ignored
 *   at runtime. A Route Handler runs per request, so process.env reads
 *   the live container env every time.
 *
 * Forwards: method, headers (except Host), body, query string. Strips
 * Host so the backend's Caddy / app sees its own hostname, not the
 * frontend's. Streams responses straight back including binary PDFs.
 *
 * Auth: handler is unauthenticated by design — the public /tools/*
 * pages use it for /api/v1/tools/*. Tenant endpoints (/api/v1/spans,
 * /api/v1/systems, ...) still require the Bearer token end-to-end
 * because the auth check runs on the backend.
 */

import { NextRequest } from "next/server";

const BACKEND_URL_DEFAULT = "http://localhost:8033";

function getBackend(): string {
  return process.env.BACKEND_URL ?? BACKEND_URL_DEFAULT;
}

async function proxy(req: NextRequest): Promise<Response> {
  const backend = getBackend();

  // Reconstruct the upstream URL: /api/* + the original query string.
  const url = new URL(req.url);
  const upstreamUrl = `${backend}${url.pathname}${url.search}`;

  // Strip Host (will be set by fetch from upstreamUrl). Forward
  // everything else, especially Authorization and Content-Type.
  const headers = new Headers(req.headers);
  headers.delete("host");
  headers.delete("connection");

  // Stream the body for non-GET/HEAD methods. fetch() in Node 22
  // supports ReadableStream bodies.
  const body =
    req.method === "GET" || req.method === "HEAD" ? undefined : req.body;

  let upstream: Response;
  try {
    upstream = await fetch(upstreamUrl, {
      method: req.method,
      headers,
      body,
      // Node fetch needs this when streaming bodies.
      // @ts-expect-error — duplex is a Node-only undici extension
      duplex: "half",
    });
  } catch (err) {
    return Response.json(
      {
        error: "backend_unreachable",
        detail: `Could not proxy ${req.method} ${url.pathname} to ${backend}: ${
          err instanceof Error ? err.message : String(err)
        }`,
      },
      { status: 502 },
    );
  }

  // Pass through status + headers + body (handles PDFs, JSON, text).
  const respHeaders = new Headers(upstream.headers);
  // Some hop-by-hop headers should not be forwarded.
  respHeaders.delete("transfer-encoding");
  respHeaders.delete("content-encoding");
  respHeaders.delete("connection");
  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: respHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const HEAD = proxy;
export const OPTIONS = proxy;

// Don't pre-render — every request must hit BACKEND_URL fresh.
export const dynamic = "force-dynamic";
