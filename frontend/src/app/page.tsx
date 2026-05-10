/**
 * Homepage — orchestrates the seven landing sections.
 *
 * Order is deliberate. Skim-friendly: a visitor can stop after the hero
 * and still know what AnnexKit is; reach the bottom and they have all
 * three of (capability, fit, price). The architecture and feature
 * sections are the "engineer-skim" middle; comparison + pricing are
 * the "buyer-skim" middle.
 *
 * If a section starts feeling overloaded, refactor inside its own file
 * — keep this orchestrator as a one-line-per-section index.
 */

import { Architecture } from "@/components/landing/architecture";
import { Comparison } from "@/components/landing/comparison";
import { FeatureGrid } from "@/components/landing/feature-grid";
import { FinalCTA } from "@/components/landing/final-cta";
import { Hero } from "@/components/landing/hero";
import { HowItWorks } from "@/components/landing/how-it-works";
import { PricingTeaser } from "@/components/landing/pricing-teaser";
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
      <Architecture />
      <TrustPreview />
      <FeatureGrid />
      <Comparison />
      <PricingTeaser />
      <FinalCTA />
    </>
  );
}
