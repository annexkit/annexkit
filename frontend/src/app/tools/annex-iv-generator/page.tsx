/**
 * /tools/annex-iv-generator — public free Annex IV PDF generator.
 *
 * The highest-leverage marketing surface for AnnexKit's free tools:
 * an anonymous user fills a 5-minute form, gets a real Annex IV PDF
 * classified deterministically against EU AI Act rules. The email is
 * captured to the `leads` table (B.1 design decision: required).
 *
 * Server component: fetches the rules tree (8 Annex III + 8 prohibited
 * + 4 transparency) from the backend at request time, with a 24h
 * revalidate (the rules don't change between deploys). Hands the tree
 * to <GeneratorForm /> which is the interactive client component.
 *
 * Backend pairing:
 *   GET  /api/v1/tools/rules.json
 *   POST /api/v1/tools/annex-iv-generator
 *
 * Rate limit: 10/hour/IP enforced server-side. The UI does no
 * client-side rate-limit signal; users see HTTP 429 + a friendly
 * error message if they hit it.
 */

import type { Metadata } from "next";

import { BackendUnavailable } from "@/components/BackendUnavailable";
import { Disclaimer } from "@/components/Disclaimer";
import { ToolsBreadcrumb } from "@/components/tools/breadcrumb";
import { ToolsCrossLinks } from "@/components/tools/cross-links";
import { BACKEND_URL, BackendUnavailableError } from "@/lib/api";

import { GeneratorForm, type AnnexRules } from "./generator-form";

export const metadata: Metadata = {
  title: "Free Annex IV Generator",
  description:
    "Generate an EU AI Act Annex IV technical documentation PDF in 5 minutes. " +
    "Deterministic rule-based classification. No account required. " +
    "AnnexKit is not a law firm.",
  alternates: { canonical: "/tools/annex-iv-generator" },
};

// Force dynamic — the backend fetch happens at request time. Without
// this, `docker compose build frontend` would statically prerender
// BackendUnavailable (the build container can't reach the backend on
// the docker network) and cache it. Trade-off: ~10ms backend hit per
// request, vs broken page until next rebuild. Worth it.
export const dynamic = "force-dynamic";

async function fetchRules(): Promise<AnnexRules | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/tools/rules.json`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new BackendUnavailableError(`Rules fetch failed: HTTP ${res.status}`);
    }
    return (await res.json()) as AnnexRules;
  } catch (err) {
    if (err instanceof BackendUnavailableError) throw err;
    throw new BackendUnavailableError("Network failure reaching the rules endpoint.");
  }
}

export default async function AnnexIVGeneratorPage() {
  let rules: AnnexRules | null;
  try {
    rules = await fetchRules();
  } catch {
    return <BackendUnavailable pageLabel="The Annex IV generator" />;
  }
  if (rules === null) {
    return <BackendUnavailable pageLabel="The Annex IV generator" />;
  }

  return (
    <main className="mx-auto w-full max-w-4xl px-6 py-12">
      <ToolsBreadcrumb
        items={[
          { label: "Tools", href: "/tools" },
          { label: "Annex IV generator" },
        ]}
      />
      <header className="mt-6 mb-10 space-y-4">
        <span className="eyebrow">Free tool</span>
        <h1 className="text-4xl font-bold tracking-tight text-foreground">
          Annex IV Generator
        </h1>
        <p className="text-lg text-muted-foreground">
          Generate an EU AI Act Annex IV technical-documentation PDF in 5 minutes.
          Classifies your system deterministically against Annex III, Article 5,
          and Article 50 rules. <strong>No account required.</strong>
        </p>
        <p className="text-sm text-muted-foreground">
          Your email is captured so we can follow up — the PDF itself is generated
          in memory and not persisted on our servers.
        </p>
      </header>

      <GeneratorForm rules={rules} />

      <ToolsCrossLinks exclude="/tools/annex-iv-generator" />

      <div className="mt-12 border-t border-border pt-8">
        <Disclaimer />
      </div>
    </main>
  );
}
