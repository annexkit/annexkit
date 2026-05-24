/**
 * Hero — top of homepage. Two-column on desktop, stacked on mobile.
 *
 * Left: eyebrow + h1 + subhead + 2 CTAs (primary + outline).
 * Right: a code snippet rendered as an editorial excerpt (filename
 *        caption, no fake browser chrome) so it reads as "code sample
 *        from the docs" rather than "screenshot of a terminal".
 *
 * Backdrop: brand-wash radial gradient over a faint surface-grid. The
 * grid is subtle on purpose (40% opacity) so it telegraphs "code/IDE"
 * without competing with the foreground copy.
 *
 * CTA hierarchy note: the primary CTA points to /pricing (intent: "see
 * the cost"), the secondary to the GitHub repo (intent: "self-host
 * route"). The FinalCTA at the bottom of the page deliberately uses a
 * *different* primary action (mailto founder) so the two bands don't
 * cannibalise — see page.tsx orchestrator for the full hierarchy.
 */

import Link from "next/link";
import { ArrowRight, Github } from "lucide-react";

import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border/60 brand-wash">
      <div className="absolute inset-0 surface-grid opacity-40" aria-hidden />
      <div className="relative mx-auto grid max-w-6xl gap-12 px-6 py-20 sm:py-28 lg:grid-cols-[1.1fr_1fr] lg:gap-16">
        {/* Copy */}
        <div className="flex flex-col justify-center space-y-7">
          <span className="eyebrow">EU AI Act compliance pipeline</span>
          <h1 className="text-balance text-5xl font-bold tracking-tight text-foreground sm:text-6xl">
            Audit-ready{" "}
            <span className="text-[var(--brand-cobalt)]">Annex IV</span>{" "}
            docs from your LLM telemetry.
          </h1>
          <p className="max-w-xl text-lg leading-relaxed text-muted-foreground">
            One decorator on your inference call. AnnexKit classifies your
            system against the Annex III risk tiers, persists an
            append-only audit log, and renders the PDF a procurement team
            or external auditor will ask for.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Button size="lg" asChild>
              <Link href="/pricing">
                Get started
                <ArrowRight />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <a
                href="https://github.com/annexkit/annexkit"
                target="_blank"
                rel="noreferrer"
              >
                <Github />
                View on GitHub
              </a>
            </Button>
          </div>
          <p className="pt-2 text-xs text-muted-foreground">
            Open-source · EU-hosted · in early access
          </p>
        </div>

        {/* Code snippet */}
        <HeroCode />
      </div>
    </section>
  );
}

/**
 * Editorial code excerpt — the smallest possible illustration of "what
 * AnnexKit actually integrates with". No fake browser chrome (traffic
 * lights) — that pattern is the default on every dev-tool landing page
 * shipped in the last three years and was flagged W5 in DESIGN_STRATEGY.
 * Instead: a quiet filename caption above and a hairline divider, so
 * the snippet reads as a doc excerpt, not a screenshot.
 */
function HeroCode() {
  return (
    <div className="surface-card relative flex flex-col overflow-hidden bg-card/80 p-0 shadow-lg backdrop-blur-sm">
      {/* Filename caption — quiet, no traffic lights */}
      <div className="flex items-center justify-between border-b border-border/60 px-5 py-2.5">
        <span className="font-mono text-xs text-muted-foreground">
          examples/loan_screener.py
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
          python
        </span>
      </div>

      {/* Code body */}
      <pre className="overflow-x-auto p-5 font-mono text-[13px] leading-relaxed">
        <code>
          <span className="text-[var(--brand-cobalt)]">from</span>{" "}
          <span className="text-foreground">annexkit</span>{" "}
          <span className="text-[var(--brand-cobalt)]">import</span>{" "}
          <span className="text-foreground">track</span>
          {"\n\n"}
          <span className="text-muted-foreground">
            @track(
            {"\n"}
            {"    "}system_id=
            <span className="text-emerald-500 dark:text-emerald-300">
              {`"loan-screener"`}
            </span>
            ,{"\n"}
            {"    "}risk_tier=
            <span className="text-emerald-500 dark:text-emerald-300">
              {`"auto"`}
            </span>
            ,{"\n"}
            {"    "}purpose=
            <span className="text-emerald-500 dark:text-emerald-300">
              {`"pre-screen credit applications"`}
            </span>
            ,{"\n"}
            )
          </span>
          {"\n"}
          <span className="text-[var(--brand-cobalt)]">def</span>{" "}
          <span className="text-foreground">screen</span>(applicant):
          {"\n"}
          {"    "}
          <span className="text-[var(--brand-cobalt)]">return</span> openai
          .chat.completions.create(
          {"\n"}
          {"        "}model=
          <span className="text-emerald-500 dark:text-emerald-300">
            {`"gpt-4o-mini"`}
          </span>
          ,{"\n"}
          {"        "}messages=[
          {"\n"}
          {"            "}
          {"{"}
          <span className="text-emerald-500 dark:text-emerald-300">
            {`"role"`}
          </span>
          :{" "}
          <span className="text-emerald-500 dark:text-emerald-300">
            {`"user"`}
          </span>
          ,{" "}
          <span className="text-emerald-500 dark:text-emerald-300">
            {`"content"`}
          </span>
          : prompt{"}"},{"\n"}
          {"        "}],
          {"\n"}
          {"    "}).choices[0].message.content
          {"\n"}
        </code>
      </pre>

      {/* Footer hint */}
      <div className="border-t border-border/60 bg-secondary/40 px-5 py-3 text-xs text-muted-foreground">
        <span className="text-[var(--brand-cobalt)]">▸</span>{" "}
        Spans ship to the collector. Annex IV PDF generates on demand.
      </div>
    </div>
  );
}
