import { OG_CONTENT_TYPE, OG_SIZE, renderOg } from "../_og/template";

export const alt =
  "AnnexKit — pricing: Pro €49, Team €199, Enterprise €5K/yr self-hosted";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return renderOg({
    eyebrow: "Pricing · early access",
    title: "Three plans. Self-host is free.",
    accent: "free",
    tagline:
      "Pro €49/mo · Team €199/mo · Enterprise €5K/yr self-hosted. Open-source under AGPL-3.0 today.",
    rightStrip: "annexkit.dev/pricing",
  });
}
