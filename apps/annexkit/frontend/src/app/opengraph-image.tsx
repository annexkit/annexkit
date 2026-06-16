/**
 * Root `/` OpenGraph + Twitter card.
 *
 * Renders when annexkit.dev (the homepage) is shared on Slack / X /
 * LinkedIn / iMessage / Notion etc. Uses the shared `_og/template`
 * helper so every AnnexKit URL — root, /tools/*, /demo/*, /pricing —
 * reads as part of the same product.
 */

import { OG_CONTENT_TYPE, OG_SIZE, renderOg } from "./_og/template";

export const alt =
  "AnnexKit — EU AI Act compliance pipeline for developers";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return renderOg({
    eyebrow: "EU AI Act compliance pipeline",
    title: "Audit-ready Annex IV docs from your LLM telemetry.",
    accent: "Annex IV",
    tagline:
      "One decorator on your inference call. Open-source, EU-hosted, in early access.",
  });
}
