/**
 * Browser favicon — generated at request time so the brand monogram
 * stays in sync with the rest of the design system. Next.js renders the
 * <ImageResponse> JSX through @vercel/og (satori + resvg) into a PNG that
 * browsers tab-icon and bookmark-icon happily.
 *
 * Sized at 32×32: the canonical favicon. Browsers downscale to 16×16
 * for the address bar; the geometry is kept simple enough to survive
 * that downscale without smudging.
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
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#0a0d14",
          borderRadius: 6,
          position: "relative",
        }}
      >
        {/* Bold A glyph, drawn proportional to a 32-px box so the
            shape stays readable when the browser scales to 16. */}
        <svg width="22" height="22" viewBox="0 0 64 64">
          <g fill="#ffffff">
            <path d="M 24 14 L 6 52 H 14 L 30 18 Z" />
            <path d="M 40 14 L 58 52 H 50 L 34 18 Z" />
            <path d="M 24 14 L 40 14 L 38 22 L 26 22 Z" />
            <rect x="18" y="34" width="28" height="5" rx="1" />
          </g>
          <circle cx="55" cy="48" r="6" fill="#3d7aff" />
        </svg>
      </div>
    ),
    { ...size },
  );
}
