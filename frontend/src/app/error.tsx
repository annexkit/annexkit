"use client";

import { useEffect } from "react";

/**
 * Global error boundary for any route below the root layout.
 *
 * Triggered when a server component throws during rendering — most
 * commonly when the backend collector is unreachable (the SSR fetch
 * inside ``trustApi.*`` raises).
 *
 * Without this file the user sees the bare Next.js 500 page; with it
 * we get a branded, on-disclaimer message that tells them what's going
 * on and offers a retry. The error.tsx file itself MUST be a client
 * component (Next.js 16 requirement).
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Send to console for now; in production this is where you'd ping
    // your error tracker (Sentry/PostHog/etc.). Logged with the digest
    // so support can correlate with server-side stack traces.
    console.error("AnnexKit trust page error:", error);
  }, [error]);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-neutral-900">
        Trust page temporarily unavailable
      </h1>
      <p className="text-neutral-700">
        We couldn&rsquo;t load this page right now. The most likely cause
        is that the AnnexKit collector backend is restarting or
        unreachable.
      </p>
      <p className="text-neutral-700">
        If you&rsquo;re running AnnexKit locally, check that{" "}
        <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">
          docker compose ps
        </code>{" "}
        shows the <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">backend</code>{" "}
        service as <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">running</code>{" "}
        and that <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">curl http://localhost:8033/health</code>{" "}
        returns <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">{"{\"status\":\"ok\"}"}</code>.
      </p>
      <div className="flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={reset}
          className="rounded bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700"
        >
          Try again
        </button>
        <a
          href="/"
          className="text-sm text-blue-700 underline hover:text-blue-900"
        >
          Back to home
        </a>
        {error.digest && (
          <code className="rounded bg-neutral-100 px-2 py-1 text-xs text-neutral-600">
            ref: {error.digest}
          </code>
        )}
      </div>
    </div>
  );
}
