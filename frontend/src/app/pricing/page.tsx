/**
 * Pricing page — three tiers + FAQ + final CTA.
 *
 * Stripe integration
 * ------------------
 * Each paid tier links to a Stripe Payment Link. The URLs are read from
 * env vars at build time so this file works in three modes:
 *   - Empty env  : button reads "Available soon", points to mailto founder
 *   - Live env   : button reads "Start with Pro" / "Choose Team", points
 *                  to the Stripe URL
 *   - Enterprise : always mailto founder@annexkit.dev (no checkout flow,
 *                  procurement-led)
 *
 * Env vars expected at build time:
 *   - NEXT_PUBLIC_STRIPE_PRO_LINK
 *   - NEXT_PUBLIC_STRIPE_TEAM_LINK
 *
 * Add them to `.env.local` and to the production deploy. The launch
 * runbook (`~/Desktop/annexkit-deployment-runbook.md`) has the steps.
 */

import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Check, Mail } from "lucide-react";

import { FinalCTA } from "@/components/landing/final-cta";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "Three plans. Pro €49/mo, Team €199/mo, Enterprise €5K/yr self-hosted. " +
    "Self-host is free under AGPL-3.0 today. Hosted product in early access.",
  alternates: { canonical: "/pricing" },
};

interface Tier {
  id: "pro" | "team" | "enterprise";
  name: string;
  price: string;
  cadence: string;
  tagline: string;
  features: string[];
  cta: string;
  ctaHref: string;
  highlight?: boolean;
}

const PRO_LINK = process.env.NEXT_PUBLIC_STRIPE_PRO_LINK;
const TEAM_LINK = process.env.NEXT_PUBLIC_STRIPE_TEAM_LINK;

const TIERS: Tier[] = [
  {
    id: "pro",
    name: "Pro",
    price: "€49",
    cadence: "per month",
    tagline:
      "One AI system. Solo founders, indie devs, prototype on the way to production.",
    features: [
      "100K spans / month",
      "1 declared AI system",
      "Annex IV PDF + Markdown",
      "Public trust page (your slug)",
      "Append-only audit log",
      "Email support (best-effort)",
    ],
    cta: PRO_LINK ? "Start with Pro" : "Request early access",
    ctaHref:
      PRO_LINK ??
      "mailto:founder@annexkit.dev?subject=Pro%20early%20access&body=Hi%2C%20I%27d%20like%20early%20access%20to%20the%20Pro%20tier.",
  },
  {
    id: "team",
    name: "Team",
    price: "€199",
    cadence: "per month",
    tagline:
      "Up to 5 systems. Growing engineering teams, agencies, scaleups in the EU AI Act ramp-up.",
    features: [
      "1M spans / month",
      "5 declared AI systems",
      "Bilingual EN / IT Annex IV PDFs",
      "LLM advisor (ambiguous declarations)",
      "Public + private trust pages",
      "Email support · 24h response",
      "Quarterly compliance digest",
    ],
    cta: TEAM_LINK ? "Choose Team" : "Request early access",
    ctaHref:
      TEAM_LINK ??
      "mailto:founder@annexkit.dev?subject=Team%20early%20access&body=Hi%2C%20I%27d%20like%20early%20access%20to%20the%20Team%20tier.",
    highlight: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "€5K",
    cadence: "per year — self-hosted",
    tagline:
      "Self-hosted on your infra. Banks, regulated industries, anyone needing a DPA on day one.",
    features: [
      "Unlimited spans · unlimited systems",
      "Self-host with `docker compose up`",
      "Source code (AGPL-3.0)",
      "DPA + Standard Contractual Clauses",
      "Slack channel · priority support",
      "Annual security review",
      "Optional: hosted on a dedicated EU instance",
    ],
    cta: "Talk to founder",
    ctaHref: "mailto:founder@annexkit.dev?subject=Enterprise%20tier",
  },
];

const FAQS: { q: string; a: string | React.ReactNode }[] = [
  {
    q: "Which AI Act articles does AnnexKit actually cover?",
    a: (
      <>
        Article 11 (technical documentation), Article 12 (logging),
        Article 13 (transparency to deployers), Article 50
        (chatbot-style disclosure obligations), Article 72 (post-market
        monitoring), and the full Annex III + Annex IV mappings. Articles
        9 (risk management) and 14 (human oversight) are partially covered
        — they require organisational evidence the SDK can&rsquo;t infer
        from spans, and we surface them as gap-analysis rows in the
        generated PDF.
      </>
    ),
  },
  {
    q: "Can I self-host?",
    a: (
      <>
        Yes — the collector and trust frontend ship under AGPL-3.0. A
        complete production <code className="inline-code">
          docker-compose.prod.yml
        </code>{" "}
        is in the repo; you bring Postgres 16 + a domain + 5 minutes,
        you get the same product that runs on annexkit.dev.
      </>
    ),
  },
  {
    q: "Where is the data stored? Do you see my prompts in plaintext?",
    a: (
      <>
        The collector runs on Hetzner Falkenstein (Germany). LLM advisor
        calls go through Mistral La Plateforme in Paris. By default the
        SDK SHA-256 hashes prompts and outputs before they leave your
        host — so we never see plaintext unless you opt in. Plaintext
        retention lands in v0.2 with encryption-at-rest on the collector
        and is gated behind a per-tenant flag.
      </>
    ),
  },
  {
    q: "Can I cancel anytime?",
    a: (
      <>
        Yes. Pro and Team are month-to-month — cancel from the customer
        dashboard, the next month doesn&rsquo;t bill. Generated Annex IV
        PDFs and the audit-log export are yours to keep regardless of
        subscription state. Enterprise is a yearly term billed
        in advance; refund pro-rata if you cancel mid-year.
      </>
    ),
  },
  {
    q: "Free trial? Free tier?",
    a: (
      <>
        Self-host is the de-facto free tier — clone the repo, run{" "}
        <code className="inline-code">docker compose up</code>, you have
        the full product. The hosted tiers don&rsquo;t have a time-bound
        free trial, but the first month is refundable on request, no
        questions asked.
      </>
    ),
  },
  {
    q: "DPA, Standard Contractual Clauses, procurement docs?",
    a: (
      <>
        Enterprise tier includes a DPA + SCC pack ready for your CISO to
        review. Pro and Team tiers can request the DPA at signup; we send
        a per-tenant signed copy within 24h. We&rsquo;re an Italian
        company, registered in the EU, no third-country transfers for
        hosted customer data.
      </>
    ),
  },
];

/**
 * Plain-text mirror of FAQS for the Schema.org FAQPage block — Google's
 * rich-result format requires `acceptedAnswer.text` as a string.
 *
 * Kept as a parallel constant rather than a derived projection because
 * extracting plaintext from React children at render time is fragile
 * (would need react-dom/server, which adds bundle weight). When you
 * edit FAQS above, mirror the change here in the same commit.
 */
const FAQ_LDJSON: { q: string; a: string }[] = [
  {
    q: "Which AI Act articles does AnnexKit actually cover?",
    a:
      "Article 11 (technical documentation), Article 12 (logging), Article 13 " +
      "(transparency to deployers), Article 50 (chatbot-style disclosure " +
      "obligations), Article 72 (post-market monitoring), and the full Annex " +
      "III + Annex IV mappings. Articles 9 (risk management) and 14 (human " +
      "oversight) are partially covered — they require organisational evidence " +
      "the SDK can't infer from spans.",
  },
  {
    q: "Can I self-host?",
    a:
      "Yes — the collector and trust frontend ship under AGPL-3.0. A complete " +
      "production docker-compose.prod.yml is in the repo; you bring Postgres " +
      "16 + a domain, you get the same product that runs on annexkit.dev.",
  },
  {
    q: "Where is the data stored? Do you see my prompts in plaintext?",
    a:
      "The collector runs on Hetzner Falkenstein (Germany). LLM advisor calls " +
      "go through Mistral La Plateforme in Paris. By default the SDK SHA-256 " +
      "hashes prompts and outputs before they leave your host — we never see " +
      "plaintext unless you opt in.",
  },
  {
    q: "Can I cancel anytime?",
    a:
      "Yes. Pro and Team are month-to-month — cancel from the customer " +
      "dashboard, the next month doesn't bill. Generated Annex IV PDFs and " +
      "the audit-log export are yours to keep regardless of subscription " +
      "state. Enterprise is a yearly term billed in advance; refund pro-rata " +
      "if you cancel mid-year.",
  },
  {
    q: "Free trial? Free tier?",
    a:
      "Self-host is the de-facto free tier — clone the repo, run docker " +
      "compose up, you have the full product. The hosted tiers don't have a " +
      "time-bound free trial, but the first month is refundable on request.",
  },
  {
    q: "DPA, Standard Contractual Clauses, procurement docs?",
    a:
      "Enterprise tier includes a DPA + SCC pack ready for your CISO to " +
      "review. Pro and Team tiers can request the DPA at signup; we send a " +
      "per-tenant signed copy within 24h. We're an Italian company, " +
      "registered in the EU, no third-country transfers for hosted customer " +
      "data.",
  },
];

const FAQ_STRUCTURED_DATA = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: FAQ_LDJSON.map((item) => ({
    "@type": "Question",
    name: item.q,
    acceptedAnswer: {
      "@type": "Answer",
      text: item.a,
    },
  })),
};

export default function PricingPage() {
  return (
    <>
      {/* Schema.org FAQPage — gives the /pricing FAQ a chance at Google
          rich-result snippets. The plain-text mirror lives in FAQ_LDJSON
          above. */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(FAQ_STRUCTURED_DATA),
        }}
      />
      <PricingHero />
      <TierGrid />
      <FAQ />
      <FinalCTA />
    </>
  );
}

/* ----------------------------------------------------------------------- */
/* Sections                                                                 */
/* ----------------------------------------------------------------------- */

function PricingHero() {
  return (
    <section className="relative overflow-hidden border-b border-border/60 brand-wash">
      <div className="absolute inset-0 surface-grid opacity-30" aria-hidden />
      <div className="relative mx-auto max-w-4xl space-y-5 px-6 py-20 text-center sm:py-24">
        <span className="eyebrow">Pricing</span>
        <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Three plans. Same{" "}
          <span className="text-[var(--brand-cobalt)]">audit-grade</span>{" "}
          pipeline.
        </h1>
        <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
          Self-host is free under AGPL-3.0. The hosted product is in{" "}
          <strong className="font-semibold text-foreground">
            early access
          </strong>{" "}
          — €49/month onwards, onboarded directly by the founder.
        </p>
      </div>
    </section>
  );
}

function TierGrid() {
  return (
    <section className="border-b border-border/60">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="grid gap-5 lg:grid-cols-3">
          {TIERS.map((tier) => (
            <TierCard key={tier.id} tier={tier} />
          ))}
        </div>
        <p className="mt-10 text-center text-sm text-muted-foreground">
          All prices in EUR. VAT billed where applicable. Need NET-30
          invoicing or annual billing? Drop us a line.
        </p>

        {/* Self-host callout — the "fourth tier" that exists today */}
        <div className="surface-card mx-auto mt-10 max-w-3xl border-l-2 border-l-[var(--brand-cobalt)] p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between sm:gap-6">
            <div className="space-y-1">
              <h3 className="text-base font-semibold tracking-tight text-foreground">
                Self-host is free, today.
              </h3>
              <p className="text-sm text-muted-foreground">
                Backend (AGPL-3.0) and SDK (MIT) are on GitHub. Bring
                Postgres + a domain, you get the same product. Hosted
                tiers above are for teams who want us to run it.
              </p>
            </div>
            <a
              href="https://github.com/annexkit/annexkit#quickstart"
              target="_blank"
              rel="noreferrer"
              className="shrink-0 self-start rounded-md border border-border bg-background px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
            >
              Read the quickstart →
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

function TierCard({ tier }: { tier: Tier }) {
  const isMailto = tier.ctaHref.startsWith("mailto:");
  return (
    <article
      id={tier.id}
      className={cn(
        "surface-card flex scroll-mt-20 flex-col gap-5 p-6",
        tier.highlight &&
          "ring-2 ring-[var(--brand-cobalt)] ring-offset-2 ring-offset-background",
      )}
    >
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold tracking-tight text-foreground">
          {tier.name}
        </h2>
        {tier.highlight && (
          <span className="rounded-full bg-[var(--brand-cobalt)]/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--brand-cobalt)]">
            Most picked
          </span>
        )}
      </div>

      <div>
        <div className="display-num text-5xl font-bold text-foreground">
          {tier.price}
        </div>
        <div className="text-xs text-muted-foreground">{tier.cadence}</div>
      </div>

      <p className="text-sm text-muted-foreground">{tier.tagline}</p>

      <ul className="flex flex-col gap-2.5 text-sm">
        {tier.features.map((feature) => (
          <li key={feature} className="flex items-start gap-2">
            <Check className="mt-0.5 size-4 shrink-0 text-[var(--brand-cobalt)]" />
            <span className="text-foreground/90">{feature}</span>
          </li>
        ))}
      </ul>

      <Button
        className="mt-auto"
        size="lg"
        variant={tier.highlight ? "default" : "outline"}
        asChild
      >
        <a
          href={tier.ctaHref}
          target={isMailto ? undefined : "_blank"}
          rel={isMailto ? undefined : "noreferrer"}
        >
          {isMailto ? <Mail /> : null}
          {tier.cta}
          {!isMailto && <ArrowRight />}
        </a>
      </Button>
    </article>
  );
}

function FAQ() {
  return (
    <section className="border-b border-border/60 bg-secondary/30">
      <div className="mx-auto max-w-3xl px-6 py-20">
        <div className="mb-10 space-y-3 text-center">
          <span className="eyebrow">Questions, answered</span>
          <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground">
            What people ask before signing up.
          </h2>
        </div>

        <ul className="space-y-3">
          {FAQS.map((item) => (
            <li
              key={item.q}
              className="surface-card group overflow-hidden p-0"
            >
              <details className="group">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-5 text-left text-base font-medium text-foreground transition-colors hover:bg-secondary/40">
                  <span>{item.q}</span>
                  <span
                    aria-hidden
                    className="font-mono text-lg text-muted-foreground transition-transform group-open:rotate-45"
                  >
                    +
                  </span>
                </summary>
                <div className="border-t border-border/60 p-5 text-sm leading-relaxed text-muted-foreground">
                  {item.a}
                </div>
              </details>
            </li>
          ))}
        </ul>

        <p className="mt-10 text-center text-sm text-muted-foreground">
          Still got questions?{" "}
          <Link
            href="mailto:founder@annexkit.dev"
            className="text-[var(--brand-cobalt)] underline-offset-4 hover:underline"
          >
            founder@annexkit.dev
          </Link>{" "}
          — replied to within a working day.
        </p>
      </div>
    </section>
  );
}
