/**
 * /brand/avatar — 1024×1024 PNG of the AnnexKit monogram, brand-correct.
 *
 * Generated at request time via satori (the same engine that backs
 * icon.tsx, apple-icon.tsx, and the per-route OG images). Single
 * source of truth for the brand mark.
 *
 * Why a dedicated endpoint instead of just exporting a static PNG:
 *   - The colour palette is in CSS tokens, but rasterised images can't
 *     read CSS. Centralising in one route file means a future brand
 *     refresh updates this file alongside icon.tsx (next to it in the
 *     diff) rather than asking someone to remember to re-export a PNG.
 *   - GitHub / Twitter / Slack / Discord all want a square PNG. 1024
 *     downscales cleanly to every common preset (256, 460, 512).
 *   - Cloudflare caches the PNG response, so the per-request render is
 *     a one-time cost.
 *
 * Composition note: layout is tuned for circular crop (GitHub, Slack,
 * Discord all mask to a circle). The monogram sits inside a roughly
 * 800-diameter inscribed circle with comfortable margin so the 'a' and
 * 'iv' both survive the mask intact.
 */

import { readFile } from "node:fs/promises";

import { ImageResponse } from "next/og";

export const runtime = "nodejs";

const SIZE = 1024;

export async function GET() {
  const [interBold, ebGaramondItalic] = await Promise.all([
    readFile(new URL("../../_fonts/Inter-Bold.ttf", import.meta.url)),
    readFile(new URL("../../_fonts/EBGaramond-BoldItalic.ttf", import.meta.url)),
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
        {/* 'a' — large dominant glyph, Inter Bold. Positioned slightly
            left of centre so the 'iv' superscript can sit close on the
            right without the whole composition drifting toward the
            crop edge. */}
        <div
          style={{
            position: "absolute",
            left: 200,
            top: 180,
            fontFamily: "Inter",
            fontSize: 720,
            fontWeight: 700,
            color: "#ffffff",
            letterSpacing: "-0.04em",
            lineHeight: 1,
            display: "flex",
          }}
        >
          a
        </div>
        {/* 'iv' — italic serif via EB Garamond. Superscript-ish position,
            visually anchored to the top-right shoulder of the 'a'. */}
        <div
          style={{
            position: "absolute",
            right: 180,
            top: 170,
            fontFamily: "EB Garamond",
            fontStyle: "italic",
            fontSize: 280,
            fontWeight: 700,
            color: "#3fbf86",
            lineHeight: 1,
            display: "flex",
          }}
        >
          iv
        </div>
        {/* Sage underline — the visual signature that ties the wordmark
            to the website palette. Sits below the 'iv', not the 'a'. */}
        <div
          style={{
            position: "absolute",
            right: 180,
            top: 470,
            width: 220,
            height: 24,
            background: "#3fbf86",
            borderRadius: 4,
          }}
        />
      </div>
    ),
    {
      width: SIZE,
      height: SIZE,
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
      headers: {
        // Long cache — brand asset rarely changes. Cloudflare will
        // honour this; a brand refresh requires a deploy anyway, which
        // changes the build id and bypasses cached responses naturally.
        "Cache-Control": "public, max-age=31536000, immutable",
      },
    },
  );
}
