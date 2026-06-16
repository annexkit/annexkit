"use client";

import { useEffect } from "react";
import { ArrowLeft, RotateCw } from "lucide-react";

import { Button } from "@/components/ui/button";

/**
 * Global error boundary for any route below the root layout.
 *
 * Triggered when a server component throws during rendering — most
 * commonly when the backend collector is unreachable (the SSR fetch
 * inside `trustApi.*` raises).
 *
 * Without this file the user sees Next.js's default 500; with it they
 * get a branded message + retry. `error.tsx` MUST be a client component
 * (Next.js 16 requirement).
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
    console.error("AnnexKit error:", error);
  }, [error]);

  return (
    <div className="mx-auto max-w-3xl px-6 py-20">
      <div className="space-y-6">
        <span className="eyebrow">Something broke</span>
        <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground">
          Trust page temporarily unavailable
        </h1>
        <p className="text-muted-foreground">
          We couldn&rsquo;t load this page right now. The most likely
          cause is that the AnnexKit collector backend is restarting or
          unreachable.
        </p>
        <p className="text-sm text-muted-foreground">
          If you&rsquo;re running AnnexKit locally, check that{" "}
          <code className="inline-code">docker compose ps</code> shows
          the <code className="inline-code">backend</code> service as{" "}
          <code className="inline-code">running</code> and that{" "}
          <code className="inline-code">
            curl http://localhost:8033/health
          </code>{" "}
          returns{" "}
          <code className="inline-code">{"{\"status\":\"ok\"}"}</code>.
        </p>
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <Button onClick={reset}>
            <RotateCw />
            Try again
          </Button>
          <Button variant="outline" asChild>
            <a href="/">
              <ArrowLeft />
              Back to home
            </a>
          </Button>
          {error.digest && (
            <code className="inline-code">ref: {error.digest}</code>
          )}
        </div>
      </div>
    </div>
  );
}
