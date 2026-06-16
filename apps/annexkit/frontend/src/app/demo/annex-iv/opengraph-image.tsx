import { OG_CONTENT_TYPE, OG_SIZE, renderOg } from "../../_og/template";

export const alt =
  "AnnexKit — live Annex IV demo, three real PDFs in three clicks";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return renderOg({
    eyebrow: "Live demo · 3 scenarios",
    title: "See AnnexKit produce a real Annex IV.",
    accent: "real Annex IV",
    tagline:
      "Loan screener · CV screener · customer-support chatbot. No install. No signup. Three clicks.",
    rightStrip: "annexkit.dev/demo/annex-iv",
  });
}
