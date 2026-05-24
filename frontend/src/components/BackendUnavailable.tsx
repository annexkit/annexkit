/**
 * Friendly component shown when the collector backend is unreachable
 * (network failure, 5xx, malformed JSON).
 *
 * Used by page handlers that catch `BackendUnavailableError` from
 * `lib/api.ts`. Avoids leaking the internal `BACKEND_URL` to the end
 * user; gives them an actionable next step instead.
 *
 * Pass `pageLabel` so the heading matches the page the user is on
 * ("Annex IV generator", "Article 12 schema", "Trust page", …).
 * Defaults to a generic "This page" so omitting it still reads OK.
 */
export function BackendUnavailable({
  pageLabel = "This page",
}: {
  pageLabel?: string;
}) {
  return (
    <div className="mx-auto w-full max-w-2xl space-y-6 px-6 py-16">
      <h1 className="text-3xl font-bold tracking-tight text-foreground">
        {pageLabel} is temporarily unavailable
      </h1>
      <p className="text-muted-foreground">
        We couldn&rsquo;t reach the AnnexKit collector right now. The
        page itself is fine; the data service it depends on is restarting
        or unreachable. Please refresh in a minute or two.
      </p>
      <p className="text-muted-foreground">
        If you&rsquo;re running AnnexKit locally, check that{" "}
        <code className="inline-code">docker compose ps</code> shows the{" "}
        <code className="inline-code">backend</code> service as{" "}
        <code className="inline-code">running</code> and that{" "}
        <code className="inline-code">curl http://localhost:8033/health</code>{" "}
        returns <code className="inline-code">{"{\"status\":\"ok\"}"}</code>.
      </p>
      <p>
        <a
          href="/"
          className="inline-flex items-center gap-1 text-[var(--brand-cobalt)] underline-offset-4 hover:underline"
        >
          ← Back to home
        </a>
      </p>
    </div>
  );
}
