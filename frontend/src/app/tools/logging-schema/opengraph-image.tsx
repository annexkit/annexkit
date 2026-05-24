import { OG_CONTENT_TYPE, OG_SIZE, renderOg } from "../../_og/template";

export const alt =
  "AnnexKit — free JSON Schema for EU AI Act Article 12 logging events";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return renderOg({
    eyebrow: "Article 12 logging schema · free",
    title: "JSON Schema for AI Act Article 12 logging events.",
    accent: "Article 12",
    tagline:
      "Drop into your OTel collector, your CI, or your custom adapter. Every field mapped to its AI Act clause.",
    rightStrip: "annexkit.dev/tools/logging-schema",
  });
}
