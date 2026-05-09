/**
 * Friendly component shown when the collector backend is unreachable
 * (network failure, 5xx, malformed JSON).
 *
 * Used by page handlers that catch ``BackendUnavailableError`` from
 * ``lib/api.ts``. Avoids leaking the internal ``BACKEND_URL`` to the
 * end user; gives them an actionable next step instead.
 */
export function BackendUnavailable() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-neutral-900">
        Trust page temporarily unavailable
      </h1>
      <p className="text-neutral-700">
        We couldn&rsquo;t reach the AnnexKit collector right now. The
        page itself is fine; the data service it depends on is
        restarting or unreachable. Please refresh in a minute or two.
      </p>
      <p className="text-neutral-700">
        If you&rsquo;re running AnnexKit locally, check that{" "}
        <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">
          docker compose ps
        </code>{" "}
        shows the <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">backend</code>{" "}
        service as <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">running</code>{" "}
        and that{" "}
        <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">
          curl http://localhost:8033/health
        </code>{" "}
        returns{" "}
        <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">
          {"{\"status\":\"ok\"}"}
        </code>
        .
      </p>
      <p>
        <a href="/" className="text-blue-700 underline hover:text-blue-900">
          ← Back to home
        </a>
      </p>
    </div>
  );
}
