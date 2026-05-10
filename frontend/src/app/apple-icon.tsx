/**
 * iOS / macOS home-screen icon — 180×180 PNG generated at request time.
 *
 * Apple devices add a rounded mask + drop shadow + glossy highlight on
 * top of whatever you ship, so we render a flat square and let Safari
 * apply its house style. Slightly more padding than the favicon so the
 * monogram still reads after Apple's mask carves the corners.
 */

import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
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
        }}
      >
        <svg width="120" height="120" viewBox="0 0 64 64">
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
