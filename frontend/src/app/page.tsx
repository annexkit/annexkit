/**
 * Homepage — six landing sections in deliberate narrative order.
 *
 * Order is the pitch:
 *   1. Hero        — what AnnexKit does, in one breath
 *   2. Stakes      — why now (AI Act countdown, fines, articles in scope)
 *   3. HowItWorks  — three steps + the four invariants under the hood
 *   4. TrustPreview— what the buyer's customers will see
 *   5. Comparison  — where AnnexKit sits next to obs tools & gov platforms
 *   6. FinalCTA    — talk-to-founder, mailto (NOT a second "Get started")
 *
 * Removed in 2026-05-24 redesign:
 *   - Architecture (box-and-arrows diagram) → fused into HowItWorks as a
 *     compact "Under the hood" strip with the four invariants
 *   - FeatureGrid (6 cards) → the relevant facts now live in the trust
 *     preview + comparison + final-cta micro-copy
 *   - PricingTeaser → replaced by a single contextual link in FinalCTA;
 *     the dedicated /pricing page does the buying work
 *
 * CTA hierarchy (was a single "Get started" repeated, now escalates):
 *   - Hero primary       → /pricing       ("see what hosted costs")
 *   - Hero secondary     → GitHub repo    ("self-host route")
 *   - FinalCTA primary   → mailto founder ("talk to a human")
 *   - FinalCTA secondary → GitHub repo    ("still on the fence")
 *
 * If a section starts feeling overloaded, refactor inside its own file —
 * keep this orchestrator as a one-line-per-section index.
 */

import { Comparison } from "@/components/landing/comparison";
import { FinalCTA } from "@/components/landing/final-cta";
import { Hero } from "@/components/landing/hero";
import { HowItWorks } from "@/components/landing/how-it-works";
import { Stakes } from "@/components/landing/stakes";
import { TrustPreview } from "@/components/landing/trust-preview";

// Regenerate the page every hour so the AI Act countdown in <Stakes>
// scales naturally as days pass. ISR, not full dynamic SSR — the page
// stays static between regenerations, so SEO and performance keep the
// same shape they have today. The day boundary is caught within ~1h
// worst-case, which is plenty for a "84 → 83 days" UX.
export const revalidate = 3600;

export default function HomePage() {
  return (
    <>
      <Hero />
      <Stakes />
      <HowItWorks />
      <TrustPreview />
      <Comparison />
      <FinalCTA />
    </>
  );
}
