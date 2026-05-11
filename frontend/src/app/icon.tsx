/**
 * Browser favicon — generated at request time so the brand monogram
 * stays in sync with the rest of the design system. Next.js renders
 * the JSX through @vercel/og (satori + resvg) into a PNG that
 * browsers happily tab-icon and bookmark.
 *
 * Sized at 32×32: the canonical favicon. Browsers downscale to 16×16
 * for the address bar; the geometry stays simple enough to survive
 * that downscale — at the smallest size you'll mainly read the white
 * 'a' on a dark square, with the cobalt 'iv' superscript just enough
 * to register as a brand cue.
 */

import { ImageResponse } from "next/og";

export const size = { width: 32, height: 32 };
export const contentType = "image/png";

export default function Icon() {
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
        {/* Lowercase 'a' — the dominant glyph. Sized so it nearly fills
            the height; satori uses its built-in geometric sans, which
            produces a clean single-storey 'a'. */}
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
        {/* Cobalt 'iv' superscript — italic, top-right corner. At 32px
            this becomes very small but still readable as a cobalt
            accent shape; on retina it resolves to the iv letterforms. */}
        <div
          style={{
            position: "absolute",
            right: 3,
            top: 2,
            fontSize: 11,
            fontWeight: 700,
            fontStyle: "italic",
            color: "#3d7aff",
            lineHeight: 1,
            display: "flex",
          }}
        >
          iv
        </div>
        {/* Cobalt underline below the 'iv' — the citation cue. */}
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
    { ...size },
  );
}
