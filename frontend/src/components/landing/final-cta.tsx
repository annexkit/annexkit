/**
 * Final CTA — last band before the footer. Brand-wash background ties
 * back to the hero so the page bookends visually.
 *
 * CTA hierarchy (Quick Win #3 from DESIGN_STRATEGY):
 *   - Hero primary       → /pricing       ("see the cost")
 *   - Hero secondary     → GitHub repo    ("self-host route")
 *   - FinalCTA primary   → mailto founder ("talk to a human")  ← this file
 *   - FinalCTA secondary → GitHub repo    ("still on the fence")
 *
 * The previous version used "Get started → /pricing" here too, which
 * meant the page had the same primary CTA at top and bottom — visually
 * the visitor reads "the team only knows one ask". Escalating to a
 * personal-email CTA at the bottom matches early-access reality: hosted
 * onboarding is done by the founder over email today, not self-serve
 * Stripe (which lands Q3 with billing infrastructure).
 */

import Link from "next/link";
import { Github, Mail } from "lucide-react";

import { Button } from "@/components/ui/button";

const FOUNDER_EMAIL = "founder@annexkit.dev";
const MAILTO =
  `mailto:${FOUNDER_EMAIL}` +
  "?subject=AnnexKit%20%E2%80%94%20talk%20to%20the%20founder" +
  "&body=Hi%2C%20I%27d%20like%20to%20talk%20about%20using%20AnnexKit%20for%3A%0A%0A" +
  "%E2%80%A2%20Company%2Fproduct%3A%20%0A" +
  "%E2%80%A2%20AI%20systems%20you%27re%20declaring%3A%20%0A" +
  "%E2%80%A2%20Self-host%20or%20hosted%3F%20%0A%0AThanks.";

export function FinalCTA() {
  return (
    <section className="relative overflow-hidden brand-wash">
      <div className="absolute inset-0 surface-grid opacity-30" aria-hidden />
      <div className="relative mx-auto flex max-w-4xl flex-col items-center gap-6 px-6 py-24 text-center">
        <span className="eyebrow">Talk to the founder</span>
        <h2 className="max-w-3xl text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Your next AI Act audit shouldn&rsquo;t cost an engineering
          quarter.
        </h2>
        <p className="max-w-2xl text-lg text-muted-foreground">
          Hosted customers are onboarded directly by the founder &mdash;
          usually within 24h. If self-host is the right answer for you,
          the SDK + collector are on GitHub under MIT / AGPL-3.0. Either
          way, the conversation starts with an email.
        </p>
        <div className="flex flex-wrap justify-center gap-3 pt-3">
          <Button size="lg" asChild>
            <a href={MAILTO}>
              <Mail />
              Email {FOUNDER_EMAIL}
            </a>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <a
              href="https://github.com/annexkit/annexkit"
              target="_blank"
              rel="noreferrer"
            >
              <Github />
              Read the SDK
            </a>
          </Button>
        </div>
        <p className="pt-2 text-xs text-muted-foreground">
          Prefer to skim the cost first?{" "}
          <Link
            href="/pricing"
            className="text-[var(--brand-cobalt)] underline-offset-4 hover:underline"
          >
            See pricing
          </Link>{" "}
          &middot; €49/mo &rarr; €5K/yr self-hosted.
        </p>
      </div>
    </section>
  );
}
