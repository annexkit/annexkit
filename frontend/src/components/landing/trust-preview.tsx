/**
 * Trust-page preview — pairs an explainer with a faithful mini-render
 * of the live demo trust page at /trust/velmara-saas.
 *
 * The preview is a real Link clickable through to the demo, NOT a
 * decorative SVG. So a visitor who scrolls past skims a small but
 * accurate replica of what their customers will see; clicking the
 * card lands them on the actual page.
 *
 * The data shown is hard-coded to match the seed_demo.py output
 * (3 systems: customer-support-bot LIMITED + cv-screener HIGH +
 * loan-prescreen HIGH). If seed_demo.py changes, update this file
 * to keep the preview honest.
 */

import Link from "next/link";
import { ArrowRight, ChevronRight, ExternalLink } from "lucide-react";

import { RiskBadge } from "@/components/RiskBadge";
import { Button } from "@/components/ui/button";
import type { RiskTier } from "@/lib/api";

interface PreviewSystem {
  id: string;
  tier: RiskTier;
}

const PREVIEW_SYSTEMS: PreviewSystem[] = [
  { id: "customer-support-bot", tier: "limited" },
  { id: "cv-screener", tier: "high" },
  { id: "loan-prescreen", tier: "high" },
];

const DEMO_SLUG = "velmara-saas";

export function TrustPreview() {
  return (
    <section className="border-b border-border/60 bg-secondary/30">
      <div className="mx-auto grid max-w-6xl gap-12 px-6 py-20 lg:grid-cols-[1fr_1.1fr] lg:gap-16">
        {/* Copy */}
        <div className="flex flex-col justify-center space-y-5">
          <span className="eyebrow">See it live</span>
          <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            What your customers see when you share your trust page.
          </h2>
          <p className="text-muted-foreground">
            Every tenant gets a slug-addressable page at{" "}
            <code className="inline-code">
              annexkit.dev/trust/&lt;slug&gt;
            </code>
            . Sensitive provider details stay in the gated Annex IV PDF;
            the public page renders only what you opt to publish.
          </p>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span
                aria-hidden
                className="mt-2 size-1.5 shrink-0 rounded-full bg-[var(--brand-cobalt)]"
              />
              Risk-tier breakdown per declared system
            </li>
            <li className="flex items-start gap-2">
              <span
                aria-hidden
                className="mt-2 size-1.5 shrink-0 rounded-full bg-[var(--brand-cobalt)]"
              />
              Annex III categories + Article 50 triggers, in plain text
            </li>
            <li className="flex items-start gap-2">
              <span
                aria-hidden
                className="mt-2 size-1.5 shrink-0 rounded-full bg-[var(--brand-cobalt)]"
              />
              Whitelist-redacted provider info (no contact emails leak)
            </li>
          </ul>
          <div className="flex flex-wrap gap-3 pt-2">
            <Button asChild>
              <Link href={`/trust/${DEMO_SLUG}`}>
                View live example
                <ArrowRight />
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/trust/${DEMO_SLUG}/systems/cv-screener`}>
                See a HIGH-risk detail
                <ExternalLink />
              </Link>
            </Button>
          </div>
        </div>

        {/* Faithful mini-replica of the trust page, clickable */}
        <Link
          href={`/trust/${DEMO_SLUG}`}
          aria-label="Open the example trust page"
          className="surface-card surface-hoverable group flex flex-col overflow-hidden p-0"
        >
          {/* Window chrome — same pattern as the hero terminal */}
          <div className="flex items-center justify-between border-b border-border/60 bg-background/40 px-4 py-2.5">
            <div className="flex gap-1.5">
              <span className="size-2.5 rounded-full bg-muted-foreground/30" />
              <span className="size-2.5 rounded-full bg-muted-foreground/30" />
              <span className="size-2.5 rounded-full bg-muted-foreground/30" />
            </div>
            <span className="font-mono text-xs text-muted-foreground">
              annexkit.dev/trust/{DEMO_SLUG}
            </span>
            <span className="w-12" />
          </div>

          {/* Page body */}
          <div className="space-y-5 p-6">
            <div>
              <span className="eyebrow">AnnexKit trust page</span>
              <h3 className="mt-2 text-xl font-bold tracking-tight text-foreground">
                Velmara SaaS S.r.l. (demo)
              </h3>
            </div>

            {/* Stats strip */}
            <div className="rounded-lg border border-border/60 bg-background/60 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                    Total declared
                  </div>
                  <div className="display-num text-2xl font-bold text-foreground">
                    3
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="flex items-center gap-1.5">
                    <RiskBadge tier="limited" size="sm" />
                    <span className="text-xs font-semibold text-foreground">
                      ×1
                    </span>
                  </span>
                  <span className="flex items-center gap-1.5">
                    <RiskBadge tier="high" size="sm" />
                    <span className="text-xs font-semibold text-foreground">
                      ×2
                    </span>
                  </span>
                </div>
              </div>
            </div>

            {/* System list */}
            <ul className="space-y-2">
              {PREVIEW_SYSTEMS.map((sys) => (
                <li
                  key={sys.id}
                  className="flex items-center justify-between rounded-md border border-border/60 bg-background/60 px-3 py-2.5"
                >
                  <span className="font-mono text-xs text-foreground">
                    {sys.id}
                  </span>
                  <RiskBadge tier={sys.tier} size="sm" />
                </li>
              ))}
            </ul>

            {/* Click affordance */}
            <div className="flex items-center gap-1 pt-1 text-xs font-medium text-[var(--brand-cobalt)]">
              Open the live page
              <ChevronRight className="size-3 transition-transform group-hover:translate-x-0.5" />
            </div>
          </div>
        </Link>
      </div>
    </section>
  );
}
