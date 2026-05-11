/**
 * Browser favicon — generated at request time so the brand monogram
 * stays in sync with the rest of the design system. Next.js renders
 * the JSX through @vercel/og (satori + resvg) into a PNG that
 * browsers tab-icon and bookmark.
 *
 * Sized at 32×32: the canonical favicon. Browsers downscale to 16×16
 * for the address bar. At the smallest size you'll mainly read the
 * white 'a' on a dark square; the cobalt 'iv' superscript is just
 * enough pixels to register as a brand cue.
 *
 * Font loading
 * ------------
 * satori (the rasteriser behind next/og) doesn't honour `fontStyle:
 * italic` or `fontFamily: "<some serif>"` unless you pass the actual
 * font file via the `fonts:` option. Without that, every glyph
 * renders in its default sans, which collapses the visual contrast
 * between the bold sans 'a' and the italic serif 'iv'. We load
 * EB Garamond Bold Italic (open-source, OFL) for the 'iv' so the
 * citation cue lands the way it does on the live site.
 */

import { readFile } from "node:fs/promises";

import { ImageResponse } from "next/og";

export const size = { width: 32, height: 32 };
export const contentType = "image/png";

export default async function Icon() {
  // readFile (not fetch) — Turbopack doesn't yet implement
  // fetch(new URL(..., import.meta.url)) for local files at build time.
  const ebGaramondItalic = await readFile(
    new URL("./_fonts/EBGaramond-BoldItalic.ttf", import.meta.url),
  );

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
        {/* Lowercase 'a' — dominant glyph in satori's default sans. */}
        <div
          style={{
            position: "absolute",
            left: 5,
            top: 0,
            fontSize: 30,
            fontWeight: 900,
            color: "#ffffff",
            letterSpacing: "-0.03em",
            lineHeight: 1,
            display: "flex",
          }}
        >
          a
        </div>
        {/* 'iv' — italic serif via the loaded EB Garamond font. */}
        <div
          style={{
            position: "absolute",
            right: 3,
            top: 2,
            fontSize: 11,
            fontWeight: 700,
            fontStyle: "italic",
            fontFamily: "EB Garamond",
            color: "#3d7aff",
            lineHeight: 1,
            display: "flex",
          }}
        >
          iv
        </div>
        {/* Cobalt underline below 'iv' — the citation cue. */}
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
          name: "EB Garamond",
          data: ebGaramondItalic,
          weight: 700,
          style: "italic",
        },
      ],
    },
  );
}
