/**
 * OpenGraph + Twitter card image — 1200×630 generated at request time.
 *
 * Renders when AnnexKit URLs are pasted into Slack / X / LinkedIn /
 * iMessage / Notion etc. The whole point: a first-time visitor who only
 * sees this preview should walk away with three things — name, what we
 * do, and the brand cobalt as the visual hook.
 *
 * Layout follows the "Linear / Stripe / Vercel" social card convention:
 *   - Dark canvas with a subtle radial cobalt wash
 *   - Brand monogram top-left, eyebrow above the title
 *   - Big tagline in the centre-left, supporting line below
 *   - URL strip bottom-left as a "credibility footprint"
 *
 * Constraints to remember (next/og is satori under the hood):
 *   - Inline styles only, no Tailwind
 *   - Limited CSS subset — flex works, grid does not
 *   - All custom fonts must be loaded via fetch + arrayBuffer; we stick
 *     to satori's default "Geist-ish" sans so we don't pay the network
 *     round-trip on every preview render
 */

import { ImageResponse } from "next/og";

// Twitter and OpenGraph use the same dimensions for "summary_large_image".
export const alt =
  "AnnexKit — EU AI Act compliance pipeline for developers";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#0a0d14",
          backgroundImage: [
            "radial-gradient(circle at 100% 0%, rgba(61,122,255,0.30) 0%, transparent 55%)",
            "radial-gradient(circle at 0% 100%, rgba(61,122,255,0.18) 0%, transparent 55%)",
          ].join(", "),
          padding: "72px 80px",
          fontFamily: "sans-serif",
          color: "#f5f7fb",
        }}
      >
        {/* Top — brand mark + wordmark */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          <svg width="64" height="64" viewBox="0 0 64 64">
            <g fill="#ffffff">
              <path d="M 24 14 L 6 52 H 14 L 30 18 Z" />
              <path d="M 40 14 L 58 52 H 50 L 34 18 Z" />
              <path d="M 24 14 L 40 14 L 38 22 L 26 22 Z" />
              <rect x="18" y="34" width="28" height="5" rx="1" />
            </g>
            <circle cx="55" cy="48" r="6" fill="#3d7aff" />
          </svg>
          <span
            style={{
              fontSize: 32,
              fontWeight: 600,
              letterSpacing: "-0.025em",
              display: "flex",
            }}
          >
            <span style={{ color: "#3d7aff" }}>a</span>
            <span>nnexkit</span>
          </span>
        </div>

        {/* Middle — eyebrow + title + tagline */}
        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          <span
            style={{
              fontSize: 18,
              fontWeight: 600,
              letterSpacing: "0.18em",
              textTransform: "uppercase",
              color: "rgba(245,247,251,0.65)",
            }}
          >
            EU AI Act compliance pipeline
          </span>
          <div
            style={{
              fontSize: 70,
              fontWeight: 700,
              letterSpacing: "-0.03em",
              lineHeight: 1.05,
              maxWidth: 980,
              display: "flex",
              flexWrap: "wrap",
            }}
          >
            <span>Audit-ready&nbsp;</span>
            <span style={{ color: "#3d7aff" }}>Annex IV&nbsp;</span>
            <span>docs from your LLM telemetry.</span>
          </div>
          <p
            style={{
              fontSize: 26,
              fontWeight: 400,
              color: "rgba(245,247,251,0.70)",
              maxWidth: 880,
              lineHeight: 1.4,
              margin: 0,
            }}
          >
            One decorator on your inference call. Open-source, EU-hosted,
            in early access.
          </p>
        </div>

        {/* Bottom — credibility strip */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: 18,
            color: "rgba(245,247,251,0.55)",
          }}
        >
          <span style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: 9999,
                background: "#3d7aff",
              }}
            />
            <span>annexkit.dev</span>
          </span>
          <span style={{ display: "flex", gap: 24 }}>
            <span>Reg. (EU) 2024/1689</span>
            <span>·</span>
            <span>EU-hosted</span>
            <span>·</span>
            <span>Open-core</span>
          </span>
        </div>
      </div>
    ),
    { ...size },
  );
}
