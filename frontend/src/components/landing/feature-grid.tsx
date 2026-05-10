/**
 * Feature grid — six cards covering the architectural choices that
 * matter to engineers and procurement teams. Each card is one
 * sentence + a one-line "why this is non-negotiable" pull-quote, so
 * skimmers grok the value without reading the body.
 *
 * Six is deliberate: a 3×2 grid reads at a glance, and the six picks
 * cover the three audiences a buyer will represent (engineering,
 * compliance, procurement) without sprawl.
 */

import {
  FileLock2,
  Gauge,
  Lock,
  Package,
  Server,
  Sparkles,
  type LucideIcon,
} from "lucide-react";

interface Feature {
  icon: LucideIcon;
  title: string;
  body: string;
  pull: string;
}

const FEATURES: Feature[] = [
  {
    icon: Gauge,
    title: "Deterministic risk classifier",
    body:
      "Annex III mapping is rules-driven. LLM advisors can suggest categories on ambiguous inputs, but they can never lower a tier the rules raised.",
    pull: "rules-driven · never declassifies",
  },
  {
    icon: FileLock2,
    title: "Append-only audit log",
    body:
      "A Postgres trigger raises on UPDATE or DELETE. There is no service-layer mutation API. The only way out of the log is a new row.",
    pull: "Postgres-enforced",
  },
  {
    icon: Lock,
    title: "Privacy by default",
    body:
      "Inputs and outputs are SHA-256 hashed before leaving your host. Plaintext is opt-in, lands at v0.2 with encryption-at-rest on the collector.",
    pull: "SHA-256 at the source",
  },
  {
    icon: Server,
    title: "EU-hosted",
    body:
      "Hetzner Falkenstein for the collector, Mistral La Plateforme (Paris) for any LLM advisor calls. No US-only services touch PII or telemetry.",
    pull: "Falkenstein · Helsinki · Paris",
  },
  {
    icon: Package,
    title: "Open-core",
    body:
      "SDK is MIT, collector and trust frontend are AGPL-3.0. Same arrangement Sentry, PostHog, and MinIO use. Self-host or hosted, your call.",
    pull: "MIT SDK · AGPL backend",
  },
  {
    icon: Sparkles,
    title: "Bilingual EN / IT PDF",
    body:
      "Annex IV documents render in both English and Italian, with risk-tier badges that match the trust page exactly. Audit-grade in either language.",
    pull: "regulator-grade out of the box",
  },
];

export function FeatureGrid() {
  return (
    <section className="border-b border-border/60 bg-secondary/30">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="max-w-2xl space-y-3">
          <span className="eyebrow">Built like infrastructure</span>
          <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Six choices an auditor will check first.
          </h2>
          <p className="text-muted-foreground">
            None of these are toggles in a settings page. They&rsquo;re
            decisions baked into the data model, the licence, and the
            hosting region.
          </p>
        </div>

        <ul className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <FeatureCard key={f.title} {...f} />
          ))}
        </ul>
      </div>
    </section>
  );
}

function FeatureCard({ icon: Icon, title, body, pull }: Feature) {
  return (
    <li className="surface-card surface-hoverable flex flex-col gap-3 p-5">
      <span className="inline-flex size-9 items-center justify-center rounded-md bg-[var(--brand-cobalt)]/10 text-[var(--brand-cobalt)]">
        <Icon className="size-4" />
      </span>
      <h3 className="text-base font-semibold tracking-tight text-foreground">
        {title}
      </h3>
      <p className="text-sm leading-relaxed text-muted-foreground">
        {body}
      </p>
      <span className="mt-auto pt-2 font-mono text-[11px] uppercase tracking-[0.14em] text-[var(--brand-cobalt)]">
        ▸ {pull}
      </span>
    </li>
  );
}
