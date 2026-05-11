/**
 * Browser favicon — generated at request time so the brand monogram
 * stays in sync with the rest of the design system. Next.js renders
 * the JSX through @vercel/og (satori + resvg) into a PNG that
 * browsers tab-icon and bookmark.
 *
 * Sized at 32×32: the canonical favicon. Browsers downscale to 16×16
 * for the address bar.
 *
 * Two fonts are passed to satori:
 *   - Inter Bold (700, normal)         : the 'a' glyph
 *   - EB Garamond Bold Italic (700)    : the 'iv' superscript only
 * Both bundled as TTF in app/_fonts/. Without an explicit sans font,
 * satori falls back to its single registered font for EVERYTHING — so
 * before this two-font setup, the 'a' was inheriting EB Garamond too.
 */

import { readFile } from "node:fs/promises";

import { ImageResponse } from "next/og";

export const size = { width: 32, height: 32 };
export const contentType = "image/png";

export default async function Icon() {
  // readFile (not fetch) — Turbopack doesn't yet implement
  // fetch(new URL(..., import.meta.url)) for local files at build time.
  const [interBold, ebGaramondItalic] = await Promise.all([
    readFile(new URL("./_fonts/Inter-Bold.ttf", import.meta.url)),
    readFile(new URL("./_fonts/EBGaramond-BoldItalic.ttf", import.meta.url)),
  ]);

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          background: "#0a0d14",
          borderRadius: 6,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
        }}
      >
        {/* Lowercase 'a' — dominant glyph, Inter Bold */}
        <div
          style={{
            position: "absolute",
            left: 5,
            top: 0,
            fontFamily: "Inter",
            fontSize: 30,
            fontWeight: 700,
            color: "#ffffff",
            letterSpacing: "-0.03em",
            lineHeight: 1,
            display: "flex",
          }}
        >
          a
        </div>
        {/* 'iv' — italic serif via the loaded EB Garamond font */}
        <div
          style={{
            position: "absolute",
            right: 3,
            top: 2,
            fontFamily: "EB Garamond",
            fontStyle: "italic",
            fontSize: 11,
            fontWeight: 700,
            color: "#3d7aff",
            lineHeight: 1,
            display: "flex",
          }}
        >
          iv
        </div>
        {/* Cobalt underline below 'iv' — the citation cue */}
        <div
          style={{
            position: "absolute",
            right: 3,
            top: 14,
            width: 9,
            height: 1.5,
            background: "#3d7aff",
            borderRadius: 1,
          }}
        />
      </div>
    ),
    {
      ...size,
      fonts: [
        {
          name: "Inter",
          data: interBold,
          weight: 700,
          style: "normal",
        },
        {
          name: "EB Garamond",
          data: ebGaramondItalic,
          weight: 700,
          style: "italic",
        },
      ],
    },
  );
}
