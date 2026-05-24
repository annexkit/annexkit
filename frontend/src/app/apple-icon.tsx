/**
 * iOS / macOS home-screen icon — 180×180 PNG generated at request time.
 *
 * Apple devices add a rounded mask + drop shadow + glossy highlight on
 * top of whatever you ship, so we render a flat square and let Safari
 * apply its house style. More padding than the favicon so the monogram
 * still reads after Apple's mask carves the corners.
 *
 * See app/icon.tsx for the two-font rationale (Inter for 'a',
 * EB Garamond Italic for 'iv').
 */

import { readFile } from "node:fs/promises";

import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default async function AppleIcon() {
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
          background: "#110c05",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
        }}
      >
        {/* 'a' — large dominant glyph, Inter Bold */}
        <div
          style={{
            position: "absolute",
            left: 28,
            top: 18,
            fontFamily: "Inter",
            fontSize: 160,
            fontWeight: 700,
            color: "#ffffff",
            letterSpacing: "-0.04em",
            lineHeight: 1,
            display: "flex",
          }}
        >
          a
        </div>
        {/* 'iv' — italic serif via EB Garamond */}
        <div
          style={{
            position: "absolute",
            right: 22,
            top: 22,
            fontFamily: "EB Garamond",
            fontStyle: "italic",
            fontSize: 56,
            fontWeight: 700,
            color: "#3fbf86",
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
            background: "#3fbf86",
            borderRadius: 2,
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
