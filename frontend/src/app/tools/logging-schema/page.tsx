/**
 * /tools/logging-schema — JSON Schema for EU AI Act Article 12 logging.
 *
 * Server-component page. Fetches the annotated schema from the
 * backend so the field-level Article 12 mapping is always in sync
 * with the actual IngestSpan Pydantic class. Static client component
 * (`SchemaTool`) handles the download buttons + tabbed examples.
 *
 * Backend pairing:
 *   GET /api/v1/tools/article-12-schema/v1.json
 *   GET /api/v1/tools/article-12-schema-annotated/v1.json
 *
 * No rate limit (read-only static-ish JSON; Cloudflare caches the
 * URL — pulling 1KB once per CI run is fine).
 */

import type { Metadata } from "next";
import Link from "next/link";

import { BackendUnavailable } from "@/components/BackendUnavailable";
import { Disclaimer } from "@/components/Disclaimer";
import { ToolsBreadcrumb } from "@/components/tools/breadcrumb";
import { ToolsCrossLinks } from "@/components/tools/cross-links";
import { PageTOC } from "@/components/tools/page-toc";
import { BACKEND_URL, BackendUnavailableError } from "@/lib/api";

import { SchemaTool, type AnnotatedSchema } from "./schema-tool";

const TOC_SECTIONS = [
  { id: "downloads", label: "Downloads" },
  { id: "use-the-schema", label: "Use the schema" },
  { id: "field-reference", label: "Field reference" },
  { id: "versioned-urls", label: "Why versioned URLs?" },
] as const;

export const metadata: Metadata = {
  title: "Article 12 Logging Schema",
  description:
    "Free JSON Schema for EU AI Act Article 12 logging events. " +
    "Drop into your OTel collector, your CI tests, or your custom adapter. " +
    "Every field mapped to the AI Act clause it satisfies.",
  alternates: { canonical: "/tools/logging-schema" },
};

// Force dynamic — same reason as /tools/annex-iv-generator: the build
// container can't reach the backend, so a static prerender would cache
// BackendUnavailable. See that file for the full note.
export const dynamic = "force-dynamic";

async function fetchAnnotatedSchema(): Promise<AnnotatedSchema | null> {
  try {
    const res = await fetch(
      `${BACKEND_URL}/api/v1/tools/article-12-schema-annotated/v1.json`,
      { cache: "no-store" },
    );
    if (!res.ok) {
      throw new BackendUnavailableError(`Schema fetch failed: HTTP ${res.status}`);
    }
    return (await res.json()) as AnnotatedSchema;
  } catch (err) {
    if (err instanceof BackendUnavailableError) throw err;
    throw new BackendUnavailableError("Network failure reaching the schema endpoint.");
  }
}

export default async function LoggingSchemaPage() {
  let schema: AnnotatedSchema | null;
  try {
    schema = await fetchAnnotatedSchema();
  } catch {
    return <BackendUnavailable pageLabel="The Article 12 schema" />;
  }
  if (!schema) {
    return <BackendUnavailable pageLabel="The Article 12 schema" />;
  }

  return (
    <main className="mx-auto w-full max-w-6xl px-6 py-12">
      <ToolsBreadcrumb
        items={[
          { label: "Tools", href: "/tools" },
          { label: "Article 12 schema" },
        ]}
      />
      <header className="mt-6 mb-10 space-y-4">
        <span className="eyebrow">Free tool</span>
        <h1 className="text-4xl font-bold tracking-tight text-foreground">
          Article 12 Logging Schema
        </h1>
        <p className="text-lg text-muted-foreground">
          JSON Schema for the per-event log row required by{" "}
          <strong>EU AI Act Article 12</strong>. Same shape the AnnexKit SDK
          POSTs to the collector. Drop it into your OTel pipeline, your CI,
          or your custom adapter to validate spans before they ship.
        </p>
        <p className="text-sm text-muted-foreground">
          Every field is mapped to the AI Act clause it satisfies — see the
          field reference below. No account required. Versioned URL
          (`/v1.json`) so a future shape change ships separately.
        </p>
      </header>

      {/* Two-column layout at lg+ — left = content, right = sticky TOC.
          Below lg the TOC is hidden and content takes full width. */}
      <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_220px] lg:gap-12">
        <article className="min-w-0">
          <section id="downloads" className="scroll-mt-24">
            <SchemaTool schema={schema} />
          </section>

          <section id="field-reference" className="mt-16 scroll-mt-24 space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Field reference</h2>
        <p className="text-sm text-muted-foreground">
          What every field is for, in compliance terms. Generated from the
          live schema — always in sync with the deployed{" "}
          <code className="inline-code">IngestSpan</code> Pydantic class.
        </p>
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted/40">
              <tr>
                <th className="px-4 py-2 text-left font-medium">Field</th>
                <th className="px-4 py-2 text-left font-medium">AI Act clause</th>
                <th className="px-4 py-2 text-left font-medium">Purpose</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(schema.properties).map(([name, prop]) => (
                <tr key={name} className="border-t border-border">
                  <td className="px-4 py-2 align-top">
                    <code className="inline-code">{name}</code>
                  </td>
                  <td className="px-4 py-2 align-top text-muted-foreground">
                    {prop["x-aiact-clause"] ?? "—"}
                  </td>
                  <td className="px-4 py-2 align-top text-muted-foreground">
                    {prop["x-purpose"] ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

          <section
            id="versioned-urls"
            className="mt-12 scroll-mt-24 space-y-4 text-sm text-muted-foreground"
          >
            <h2 className="text-2xl font-semibold text-foreground">
              Why versioned URLs?
            </h2>
        <p>
          The schema URL ends in <code className="inline-code">/v1.json</code>{" "}
          so consumers can pin against a stable shape. When a future SDK
          release reorders or renames a field, a fresh{" "}
          <code className="inline-code">/v2.json</code> ships and{" "}
          <code className="inline-code">/v1.json</code> keeps serving the
          old shape — your OTel collector or CI validator doesn&rsquo;t
          break on upgrade day.
        </p>
        <p>
          The current shape comes from the AnnexKit SDK{" "}
          <Link
            href="/docs/sdk-quickstart"
            className="text-[var(--brand-cobalt)] underline-offset-4 hover:underline"
          >
            wire format
          </Link>{" "}
          and is documented inside the schema itself (every field has{" "}
          <code className="inline-code">description</code>,{" "}
              <code className="inline-code">x-aiact-clause</code>, and{" "}
              <code className="inline-code">x-purpose</code>).
            </p>
          </section>
        </article>

        <PageTOC sections={[...TOC_SECTIONS]} />
      </div>

      <ToolsCrossLinks exclude="/tools/logging-schema" />

      <div className="mt-12 border-t border-border pt-8">
        <Disclaimer />
      </div>
    </main>
  );
}
