import Link from "next/link";

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="space-y-4">
        <h1 className="text-4xl font-bold tracking-tight text-neutral-900">
          AnnexKit trust center
        </h1>
        <p className="text-lg text-neutral-700">
          Public, slug-addressable pages for tenants that declare their AI
          systems via the AnnexKit pipeline. Each tenant chooses what to
          publish; sensitive provider details never leave the gated Annex
          IV PDF.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-neutral-900">
          What lives here
        </h2>
        <ul className="list-inside list-disc space-y-1 text-neutral-700">
          <li>
            <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">
              /trust/&lt;slug&gt;
            </code>{" "}
            — overview of one tenant: name, count of declared AI systems,
            risk-tier breakdown.
          </li>
          <li>
            <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">
              /trust/&lt;slug&gt;/systems/&lt;system_id&gt;
            </code>{" "}
            — detail of a single AI system: declared purpose, Annex III
            categories, Article 50 transparency triggers, classifier
            reasoning, public provider info.
          </li>
        </ul>
      </section>

      <section className="rounded border border-neutral-200 bg-white p-6">
        <h2 className="mb-3 text-xl font-semibold text-neutral-900">
          Try a demo trust page
        </h2>
        <p className="mb-4 text-neutral-700">
          Run <code className="rounded bg-neutral-100 px-1 py-0.5 text-sm">make demo-seed</code>{" "}
          from the project root to seed a tenant + run the loan-screener
          chatbot, then visit:
        </p>
        <p className="text-sm">
          <Link
            href="/trust/dev-replace-with-your-slug"
            className="font-medium text-blue-700 underline"
          >
            /trust/dev-replace-with-your-slug
          </Link>{" "}
          (replace with the slug printed by{" "}
          <code className="rounded bg-neutral-100 px-1 py-0.5 text-xs">
            make seed
          </code>
          ).
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-neutral-900">
          Open-source and EU-hosted
        </h2>
        <p className="text-neutral-700">
          The collector backend is{" "}
          <a
            href="https://github.com/annexkit/annexkit/blob/main/backend/LICENSE"
            className="text-blue-700 underline"
          >
            AGPL-3.0
          </a>
          ; the developer SDK is{" "}
          <a
            href="https://github.com/annexkit/annexkit/blob/main/sdk/LICENSE"
            className="text-blue-700 underline"
          >
            MIT
          </a>
          . Hosting is in Falkenstein/Helsinki, LLM advisor calls go
          through Mistral La Plateforme (Paris). No US-only services for
          PII or telemetry payloads.
        </p>
      </section>
    </div>
  );
}
