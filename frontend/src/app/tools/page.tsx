/**
 * /tools — public free-tools hub.
 *
 * Lists the AnnexKit free tools (currently 2: Annex IV generator,
 * Article 12 logging schema; classifier flowchart + risk classifier
 * land in B.3 and B.4). Same visual contract as Konformia's
 * /strumenti — surface-card + eyebrow + breadcrumb + JSON-LD —
 * because both products are part of the same family.
 *
 * Also serves as the orphan-link guard: the tool pages live under
 * /tools/* and this hub is what links to them, so they never appear
 * as deep links from the footer without context.
 */

import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, ChevronRight, FileDown, FileText, Play } from "lucide-react";

import { Disclaimer } from "@/components/Disclaimer";
import { Button } from "@/components/ui/button";

const SITE_ORIGIN =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://annexkit.dev";
const PAGE_PATH = "/tools";
const PAGE_URL = `${SITE_ORIGIN}${PAGE_PATH}`;

export const metadata: Metadata = {
  title: "Free EU AI Act tools — Annex IV PDF, Article 12 schema, live demo",
  description:
    "Public AnnexKit tools for EU AI Act compliance: generate an Annex IV " +
    "PDF in 5 minutes, download the Article 12 JSON Schema, open a live " +
    "demo. No account required. AnnexKit is not a law firm.",
  keywords: [
    "EU AI Act tools",
    "Annex IV generator",
    "Article 12 schema",
    "AI Act free tools",
    "AI Act developer tools",
  ],
  alternates: { canonical: PAGE_PATH },
  openGraph: {
    type: "website",
    title: "Free EU AI Act tools — AnnexKit",
    description:
      "Annex IV PDF generator, Article 12 JSON Schema, live demo. " +
      "Deterministic, free, no signup.",
    url: PAGE_URL,
    siteName: "AnnexKit",
  },
};

interface Tool {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge: string;
  title: string;
  blurb: string;
  cta: string;
  external?: boolean;
}

const TOOLS: Tool[] = [
  {
    href: "/tools/annex-iv-generator",
    icon: FileDown,
    badge: "Annex IV · Article 11",
    title: "Annex IV PDF generator",
    blurb:
      "Fill a 5-minute form, get a real EU AI Act Annex IV technical-" +
      "documentation PDF. Deterministic classifier — same verdict on " +
      "every re-submit. Email required (we follow up).",
    cta: "Open the generator",
  },
  {
    href: "/demo/annex-iv",
    icon: Play,
    badge: "Live demo · 3 scenarios",
    title: "See AnnexKit produce a real Annex IV",
    blurb:
      "Three pre-built scenarios (loan-screener, CV screener, customer-" +
      "support chatbot) — each opens a fully-rendered Annex IV PDF " +
      "populated from realistic synthetic telemetry. No install, no signup.",
    cta: "View the demos",
  },
  {
    href: "/tools/logging-schema",
    icon: FileText,
    badge: "Article 12 · JSON Schema",
    title: "Article 12 logging schema",
    blurb:
      "JSON Schema for the per-event log row required by EU AI Act " +
      "Article 12. Drop into your OTel collector, your CI, or your " +
      "custom adapter. Annotated variant maps each field to its " +
      "AI Act clause.",
    cta: "Get the schema",
  },
];

const BREADCRUMB_LD = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "AnnexKit", item: SITE_ORIGIN },
    { "@type": "ListItem", position: 2, name: "Tools", item: PAGE_URL },
  ],
};

const COLLECTION_LD = {
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  name: "Free EU AI Act tools — AnnexKit",
  url: PAGE_URL,
  inLanguage: "en",
  isPartOf: { "@type": "WebSite", name: "AnnexKit", url: SITE_ORIGIN },
  hasPart: TOOLS.map((t) => ({
    "@type": "WebApplication",
    name: t.title,
    url: `${SITE_ORIGIN}${t.href}`,
  })),
};

export default function ToolsHubPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(BREADCRUMB_LD) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(COLLECTION_LD) }}
      />

      <Hero />
      <ToolsGrid />
      <FinalCta />
    </>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border/70">
      <div className="absolute inset-0 brand-wash" aria-hidden />
      <div className="relative mx-auto max-w-5xl px-6 py-16 md:px-10 md:py-24">
        <Breadcrumb items={[{ label: "Tools" }]} />
        <span className="eyebrow mt-6 inline-block">Free tools</span>
        <h1
          className="mt-4 text-4xl font-semibold leading-[1.05] tracking-tight md:text-5xl"
          style={{ letterSpacing: "-0.03em" }}
        >
          EU AI Act tools,{" "}
          <span className="text-[var(--brand-cobalt)]">
            no account required.
          </span>
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground">
          Deterministic rule engine, real Annex IV PDFs, downloadable JSON
          Schema. The same machinery the AnnexKit SDK uses — exposed publicly
          so you can try it before opening an account.
        </p>
      </div>
    </section>
  );
}

function ToolsGrid() {
  return (
    <section className="px-6 py-16 md:px-10 md:py-20">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 flex flex-col gap-3 md:max-w-2xl">
          <span className="eyebrow">The tools</span>
          <h2
            className="text-3xl font-semibold tracking-tight md:text-4xl"
            style={{ letterSpacing: "-0.025em" }}
          >
            Pick what you need today.
          </h2>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {TOOLS.map((t) => {
            const Icon = t.icon;
            return (
              <Link
                key={t.href}
                href={t.href}
                className="surface-card surface-hoverable group flex flex-col gap-3 p-6 transition"
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="inline-flex size-10 items-center justify-center rounded-lg bg-[var(--brand-cobalt)]/10 text-[var(--brand-cobalt)]">
                    <Icon className="size-5" />
                  </span>
                  <span className="rounded-full bg-secondary px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                    {t.badge}
                  </span>
                </div>
                <h3 className="text-lg font-semibold tracking-tight text-foreground">
                  {t.title}
                </h3>
                <p className="flex-1 text-sm leading-relaxed text-muted-foreground">
                  {t.blurb}
                </p>
                <div className="mt-2 flex items-center gap-1.5 text-xs font-medium text-foreground/80 transition group-hover:text-foreground">
                  {t.cta}
                  <ArrowRight className="size-3.5" />
                </div>
              </Link>
            );
          })}
        </div>

        <div className="mt-10 text-sm text-muted-foreground">
          More tools land in v0.2 — risk-classifier wizard, drag-and-drop
          flowchart, embeddable trust badge. Subscribe at{" "}
          <a
            href="mailto:founder@annexkit.dev"
            className="text-[var(--brand-cobalt)] underline-offset-4 hover:underline"
          >
            founder@annexkit.dev
          </a>{" "}
          to be notified.
        </div>
      </div>
    </section>
  );
}

function FinalCta() {
  return (
    <section className="px-6 py-16 md:px-10 md:py-20">
      <div className="mx-auto max-w-6xl">
        <div className="surface-card brand-wash relative overflow-hidden p-10 md:p-14">
          <div className="grid gap-10 md:grid-cols-[1.2fr_0.8fr] md:items-center">
            <div className="flex flex-col gap-5">
              <span className="eyebrow">From one PDF to a pipeline</span>
              <h2
                className="text-3xl font-semibold tracking-tight md:text-4xl"
                style={{ letterSpacing: "-0.025em" }}
              >
                Tried a tool? Wire AnnexKit into your codebase.
              </h2>
              <p className="leading-relaxed text-muted-foreground">
                The tools above use the same deterministic rule engine and
                the same renderer the SDK pipeline runs against your real
                spans. One <code className="inline-code">@track</code>{" "}
                decorator + ~10 minutes and your own Annex IV looks like the
                demo — with your actual numbers.
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <Button asChild size="lg">
                <a
                  href="https://github.com/annexkit/annexkit#quickstart"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  pip install annexkit
                  <ArrowRight className="ml-1.5 size-4" />
                </a>
              </Button>
              <Button asChild size="lg" variant="outline">
                <Link href="/pricing">See pricing</Link>
              </Button>
            </div>
          </div>
        </div>

        <div className="mt-12">
          <Disclaimer />
        </div>
      </div>
    </section>
  );
}

function Breadcrumb({
  items,
}: {
  items: Array<{ label: string; href?: string }>;
}) {
  return (
    <nav
      aria-label="Breadcrumb"
      className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground"
    >
      <Link href="/" className="hover:text-foreground">
        AnnexKit
      </Link>
      {items.map((item, idx) => (
        <span key={`${item.label}-${idx}`} className="flex items-center gap-1.5">
          <ChevronRight className="size-3" aria-hidden />
          {item.href ? (
            <Link href={item.href} className="hover:text-foreground">
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground/80">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
