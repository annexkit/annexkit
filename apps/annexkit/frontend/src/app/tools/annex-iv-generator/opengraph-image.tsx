import { OG_CONTENT_TYPE, OG_SIZE, renderOg } from "../../_og/template";

export const alt = "AnnexKit — free Annex IV PDF generator (5 minutes, no signup)";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return renderOg({
    eyebrow: "Annex IV PDF generator · free",
    title: "Generate an Annex IV PDF in 5 minutes.",
    accent: "5 minutes",
    tagline:
      "Fill the form, get a real EU AI Act Annex IV PDF. Deterministic classifier. No account required.",
    rightStrip: "annexkit.dev/tools/annex-iv-generator",
  });
}
