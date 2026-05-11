/**
 * iOS / macOS home-screen icon — 180×180 PNG generated at request time.
 *
 * Apple devices add a rounded mask + drop shadow + glossy highlight on
 * top of whatever you ship, so we render a flat square and let Safari
 * apply its house style. More padding than the favicon so the monogram
 * still reads after Apple's mask carves the corners.
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
          background: "#0a0d14",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
        }}
      >
        {/* 'a' — large, dominant */}
        <div
          style={{
            position: "absolute",
            left: 28,
            top: 18,
            fontSize: 160,
            fontWeight: 900,
            color: "#ffffff",
            letterSpacing: "-0.04em",
            lineHeight: 1,
            display: "flex",
          }}
        >
          a
        </div>
        {/* 'iv' — italic serif superscript, cobalt */}
        <div
          style={{
            position: "absolute",
            right: 22,
            top: 22,
            fontSize: 56,
            fontWeight: 700,
            fontStyle: "italic",
            color: "#3d7aff",
            lineHeight: 1,
            display: "flex",
          }}
        >
          iv
        </div>
        {/* Cobalt underline */}
        <div
          style={{
            position: "absolute",
            right: 22,
            top: 82,
            width: 40,
            height: 5,
            background: "#3d7aff",
            borderRadius: 2,
          }}
        />
      </div>
    ),
    { ...size },
  );
}
