/**
 * Pricing teaser — three cards on the homepage that link to the full
 * /pricing page. Cards mirror the structure on /pricing so the visual
 * grammar carries between the two surfaces.
 *
 * The middle tier (Team) is highlighted as "most picked" because that's
 * the one we want most prospects to land on; this nudge is a standard
 * SaaS pricing-page pattern (Stripe, Linear, Vercel all do it).
 */

import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Tier {
  id: string;
  name: string;
  price: string;
  cadence: string;
  tagline: string;
  features: string[];
  cta: string;
  highlight?: boolean;
}

const TIERS: Tier[] = [
  {
    id: "pro",
    name: "Pro",
    price: "€49",
    cadence: "per month",
    tagline: "One AI system. Solo founders, indie devs, prototypes.",
    features: [
      "100K spans / month",
      "1 declared AI system",
      "Annex IV PDF + Markdown",
      "Public trust page",
    ],
    cta: "Start with Pro",
  },
  {
    id: "team",
    name: "Team",
    price: "€199",
    cadence: "per month",
    tagline: "Up to 5 systems. Growing engineering teams.",
    features: [
      "1M spans / month",
      "5 declared AI systems",
      "Bilingual EN / IT PDFs",
      "LLM advisor on ambiguous declarations",
      "Email support",
    ],
    cta: "Choose Team",
    highlight: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "€5K",
    cadence: "per year (self-host)",
    tagline: "Self-hosted on your infra, regulated industries.",
    features: [
      "Unlimited spans + systems",
      "Self-host with `docker compose`",
      "DPA + SCC templates",
      "Priority + Slack support",
      "Annual security review",
    ],
    cta: "Talk to founder",
  },
];

export function PricingTeaser() {
  return (
    <section className="border-b border-border/60 bg-secondary/30">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div className="max-w-2xl space-y-3">
            <span className="eyebrow">Pricing</span>
            <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
              Three plans. Same pipeline.
            </h2>
            <p className="text-muted-foreground">
              No enterprise gate to cross to get the hosted product. The
              self-host build is the same code that runs annexkit.dev.
            </p>
          </div>
          <Link
            href="/pricing"
            className="hidden items-center gap-1 text-sm font-medium text-[var(--brand-cobalt)] sm:inline-flex"
          >
            See full pricing comparison <ArrowRight className="size-4" />
          </Link>
        </div>

        <div className="mt-12 grid gap-5 lg:grid-cols-3">
          {TIERS.map((tier) => (
            <TierCard key={tier.id} tier={tier} />
          ))}
        </div>
      </div>
    </section>
  );
}

function TierCard({ tier }: { tier: Tier }) {
  return (
    <article
      className={cn(
        "surface-card flex flex-col gap-5 p-6",
        tier.highlight &&
          "ring-2 ring-[var(--brand-cobalt)] ring-offset-2 ring-offset-secondary",
      )}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold tracking-tight text-foreground">
          {tier.name}
        </h3>
        {tier.highlight && (
          <span className="rounded-full bg-[var(--brand-cobalt)]/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--brand-cobalt)]">
            Most picked
          </span>
        )}
      </div>

      <div>
        <div className="display-num text-4xl font-bold text-foreground">
          {tier.price}
        </div>
        <div className="text-xs text-muted-foreground">{tier.cadence}</div>
      </div>

      <p className="text-sm text-muted-foreground">{tier.tagline}</p>

      <ul className="flex flex-col gap-2 text-sm">
        {tier.features.map((feature) => (
          <li key={feature} className="flex items-start gap-2">
            <Check className="mt-0.5 size-4 shrink-0 text-[var(--brand-cobalt)]" />
            <span className="text-foreground/90">{feature}</span>
          </li>
        ))}
      </ul>

      <Button
        className="mt-auto"
        variant={tier.highlight ? "default" : "outline"}
        asChild
      >
        <Link href={`/pricing#${tier.id}`}>{tier.cta}</Link>
      </Button>
    </article>
  );
}
