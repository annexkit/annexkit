import { OG_CONTENT_TYPE, OG_SIZE, renderOg } from "../_og/template";

export const alt = "AnnexKit — free EU AI Act tools, no account required";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return renderOg({
    eyebrow: "Free tools",
    title: "EU AI Act tools, no account required.",
    accent: "no account required",
    tagline:
      "Deterministic rule engine, real Annex IV PDFs, downloadable JSON Schema.",
    rightStrip: "annexkit.dev/tools",
  });
}
