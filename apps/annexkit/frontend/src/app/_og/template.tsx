/**
 * Shared OpenGraph image template.
 *
 * Per-route `opengraph-image.tsx` files import `renderOg(...)` and pass
 * the eyebrow / title / tagline that's specific to that route. The
 * card itself — fonts, monogram, palette, bottom strip — stays
 * identical so every shared link reads as part of the same product.
 *
 * Why a shared module instead of duplicating the file:
 *   - Single source of truth for the monogram + palette
 *   - One commit changes the look across every shared URL
 *   - Per-route file becomes a 12-line config object (see uses)
 *
 * Satori (the next/og engine) constraints:
 *   - Inline styles only, no Tailwind
 *   - Limited CSS subset (flex works, grid doesn't, no animations)
 *   - Custom fonts loaded via the `fonts:` option as ArrayBuffer
 *   - Use readFile() not fetch(new URL()) — Turbopack hasn't shipped
 *     the local-file fetch yet (Next.js 16)
 */

import type { ReactElement } from "react";
import { readFile } from "node:fs/promises";

import { ImageResponse } from "next/og";

// Turbopack needs each `new URL(..., import.meta.url)` to be a string
// LITERAL (no variables / concatenation) so it can include the file in
// the route bundle at build time. Inline the `../_fonts/Foo.ttf` path
// at every readFile call below for that reason. From this file at
// frontend/src/app/_og/, `../_fonts/` resolves to
// frontend/src/app/_fonts/ which is where the .ttf files live.

export const OG_SIZE = { width: 1200, height: 630 } as const;
export const OG_CONTENT_TYPE = "image/png";

interface OgInput {
  /** Small label above the title — e.g. "Free tool", "Live demo". */
  eyebrow: string;
  /**
   * Headline. Pass `accent` substring(s) to colour them in cobalt; the
   * function splits and renders flex-wrapped spans so satori can break
   * lines naturally.
   */
  title: string;
  /** Optional substring(s) inside `title` to highlight in cobalt. */
  accent?: string | string[];
  /** Supporting line below the title. */
  tagline: string;
  /** Right-side bottom strip — e.g. "3 pre-built scenarios". */
  rightStrip?: string;
}

/**
 * Build the ImageResponse for a route's OG card.
 *
 * Usage in a route's `opengraph-image.tsx`:
 *
 *     import { renderOg } from "@/app/_og/template";
 *     export const size = OG_SIZE;
 *     export const contentType = OG_CONTENT_TYPE;
 *     export const alt = "...";
 *     export default function Image() {
 *       return renderOg({ eyebrow: "...", title: "...", tagline: "..." });
 *     }
 */
export async function renderOg(input: OgInput): Promise<ImageResponse> {
  const [interBold, interRegular, ebGaramondItalic] = await Promise.all([
    readFile(new URL("../_fonts/Inter-Bold.ttf", import.meta.url)),
    readFile(new URL("../_fonts/Inter-Regular.ttf", import.meta.url)),
    readFile(new URL("../_fonts/EBGaramond-BoldItalic.ttf", import.meta.url)),
  ]);

  const titleNodes = renderTitleWithAccents(input.title, input.accent);
  const rightStrip = input.rightStrip ?? "Reg. (EU) 2024/1689 · EU-hosted · Open-core";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#110c05",
          backgroundImage: [
            "radial-gradient(circle at 100% 0%, rgba(61,122,255,0.30) 0%, transparent 55%)",
            "radial-gradient(circle at 0% 100%, rgba(61,122,255,0.18) 0%, transparent 55%)",
          ].join(", "),
          padding: "72px 80px",
          fontFamily: "Inter",
          color: "#f5f7fb",
        }}
      >
        {/* Top — brand mark + wordmark */}
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <Monogram />
          <span
            style={{
              fontSize: 32,
              fontWeight: 600,
              letterSpacing: "-0.025em",
              display: "flex",
            }}
          >
            <span style={{ color: "#3fbf86" }}>a</span>
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
            {input.eyebrow}
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
            {titleNodes}
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
            {input.tagline}
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
                background: "#3fbf86",
              }}
            />
            <span>annexkit.dev</span>
          </span>
          <span>{rightStrip}</span>
        </div>
      </div>
    ),
    {
      ...OG_SIZE,
      fonts: [
        { name: "Inter", data: interBold, weight: 700, style: "normal" },
        { name: "Inter", data: interRegular, weight: 400, style: "normal" },
        { name: "EB Garamond", data: ebGaramondItalic, weight: 700, style: "italic" },
      ],
    },
  );
}

function Monogram(): ReactElement {
  return (
    <div
      style={{
        position: "relative",
        width: 80,
        height: 64,
        display: "flex",
      }}
    >
      <span
        style={{
          position: "absolute",
          left: 0,
          top: -6,
          fontSize: 76,
          fontWeight: 900,
          color: "#ffffff",
          letterSpacing: "-0.04em",
          lineHeight: 1,
          display: "flex",
        }}
      >
        a
      </span>
      <span
        style={{
          position: "absolute",
          right: 0,
          top: 0,
          fontSize: 26,
          fontWeight: 700,
          fontStyle: "italic",
          fontFamily: "EB Garamond",
          color: "#3fbf86",
          lineHeight: 1,
          display: "flex",
        }}
      >
        iv
      </span>
      <div
        style={{
          position: "absolute",
          right: 0,
          top: 28,
          width: 18,
          height: 2.5,
          background: "#3fbf86",
          borderRadius: 1.5,
        }}
      />
    </div>
  );
}

/**
 * Split `title` on the accent substring(s) and wrap each accent span
 * in a cobalt-coloured node. Pure-text accents kept as plain spans so
 * satori flexWrap can break naturally.
 */
function renderTitleWithAccents(
  title: string,
  accent: string | string[] | undefined,
): ReactElement[] {
  if (!accent) {
    return [<span key="all">{title}</span>];
  }
  const accents = Array.isArray(accent) ? accent : [accent];
  // Build a regex that matches any accent (escaped) and splits.
  const escaped = accents.map((a) => a.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const re = new RegExp(`(${escaped.join("|")})`, "g");
  const parts = title.split(re);
  return parts
    .filter((p) => p !== "")
    .map((part, i) =>
      accents.includes(part) ? (
        <span key={i} style={{ color: "#3fbf86" }}>
          {part}
        </span>
      ) : (
        <span key={i}>{part}</span>
      ),
    );
}
