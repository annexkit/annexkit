/**
 * AnnexKit logo — three variants in one file so we can A/B them without
 * juggling files.
 *
 * Brand insight: "AnnexKit" → a *kit* for delivering *Annex IV* technical
 * documentation. The monogram leans into that with two letterforms:
 *
 *   - lowercase 'a' (the initial of AnnexKit, matches the cobalt-tinted
 *     leading 'a' in the wordmark — same letter, same colour cue)
 *   - small italic serif 'iv' superscript in cobalt, with a cobalt
 *     underline — reads as a citation/footnote reference to the literal
 *     output of the product: Annex IV technical documentation
 *
 * A regulator or compliance officer who has read the AI Act sees the
 * "iv" and knows what AnnexKit is in 0.3 seconds. A developer reads it
 * as a clean lowercase wordmark.
 *
 *   - <LogoMark>     : icon-only (16-200 px). Favicons, sidebar collapsed,
 *                      app-icon contexts.
 *   - <LogoWordmark> : "annexkit" with the leading 'a' in cobalt. Use
 *                      when the icon would be redundant (footer copy).
 *   - <LogoLockup>   : mark + wordmark side-by-side. Default for headers.
 *
 * The mark itself ships in three variants selectable via a `variant` prop:
 *   - "monogram" — lowercase 'a' + iv superscript with cobalt underline.
 *                  Recommended, default.
 *   - "bracket"  — same letterform inside `[ ]` brackets; signals
 *                  "code container / kit".
 *   - "seal"     — same letterform inside a rounded-square frame;
 *                  signals "audit-grade stamp".
 *
 * Colour: the 'a' uses `currentColor` so it inherits the surrounding
 * text colour (light/dark theme flips for free). The cobalt accent
 * (the 'iv', its underline, the seal accent) is hard-coded to the
 * brand token so it stays legible against any background.
 *
 * Typography note: the 'a' uses the Geist Sans family that the site
 * already loads for body text (CSS variable `--font-geist-sans`); the
 * 'iv' uses a system serif (Georgia / 'New York' / 'Iowan Old Style')
 * so the contrast between sans + italic-serif is preserved everywhere.
 * Fallback chains keep the mark legible if a font is missing.
 */

import * as React from "react";

import { cn } from "@/lib/utils";

export type LogoStyle = "monogram" | "bracket" | "seal";

interface LogoProps extends React.SVGProps<SVGSVGElement> {
  /** Pixel size for both width + height. Default 28. */
  size?: number;
  /** Which mark variant to render. */
  variant?: LogoStyle;
  /** Optional aria label override. */
  title?: string;
}

// CSS chains shared by every variant — keep them in one place so the
// mark looks identical across MonogramMark / BracketMark / SealMark.
const SANS_STACK =
  "var(--font-geist-sans), -apple-system, BlinkMacSystemFont, 'Geist', " +
  "Inter, system-ui, 'Segoe UI', Roboto, sans-serif";
// EB Garamond Bold Italic — loaded as a webfont in app/layout.tsx and
// exposed via --font-brand-serif. System serifs are the fallback so the
// mark stays legible if the webfont is still loading.
const SERIF_STACK =
  "var(--font-brand-serif), 'EB Garamond', 'New York', Georgia, " +
  "'Iowan Old Style', 'Cambria', 'Times New Roman', serif";

// ---------------------------------------------------------------------------
// Mark — icon-only
// ---------------------------------------------------------------------------
export function LogoMark({
  size = 28,
  variant = "monogram",
  title = "AnnexKit",
  className,
  ...props
}: LogoProps) {
  if (variant === "bracket")
    return <BracketMark size={size} title={title} className={className} {...props} />;
  if (variant === "seal")
    return <SealMark size={size} title={title} className={className} {...props} />;
  return <MonogramMark size={size} title={title} className={className} {...props} />;
}

/* The lowercase 'a' + 'iv' superscript + cobalt underline.
 * Extracted so all three variants render the same core letterform. */
function CoreLetterform({
  scale = 1,
  offsetX = 0,
  offsetY = 0,
}: {
  scale?: number;
  offsetX?: number;
  offsetY?: number;
}) {
  return (
    <g transform={`translate(${offsetX} ${offsetY}) scale(${scale})`}>
      {/* 'a' — bold sans lowercase, current text colour */}
      <text
        x={14}
        y={54}
        style={{
          fontFamily: SANS_STACK,
          fontWeight: 900,
          fontSize: 52,
          letterSpacing: "-0.025em",
        }}
        fill="currentColor"
      >
        a
      </text>
      {/* 'iv' — italic serif, cobalt, superscript position */}
      <text
        x={46}
        y={28}
        style={{
          fontFamily: SERIF_STACK,
          fontStyle: "italic",
          fontWeight: 700,
          fontSize: 20,
        }}
        fill="var(--brand-accent)"
      >
        iv
      </text>
      {/* Cobalt underline beneath the 'iv' — the citation-mark cue.
          Sits 2px under the iv baseline so it reads as a footnote ref. */}
      <rect x={46} y={30} width={14} height={2} rx={1} fill="var(--brand-accent)" />
    </g>
  );
}

// ---------------------------------------------------------------------------
// Variant A: lowercase 'a' + iv with cobalt underline (recommended, default)
// ---------------------------------------------------------------------------
function MonogramMark({
  size = 28,
  title,
  className,
  ...props
}: LogoProps) {
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role="img"
      aria-label={title}
      className={cn("text-foreground", className)}
      {...props}
    >
      <title>{title}</title>
      <CoreLetterform />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Variant B: bracket-framed letterform — "code container / kit"
// ---------------------------------------------------------------------------
function BracketMark({
  size = 28,
  title,
  className,
  ...props
}: LogoProps) {
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role="img"
      aria-label={title}
      className={cn("text-foreground", className)}
      {...props}
    >
      <title>{title}</title>
      {/* Left bracket */}
      <path
        d="M 14 10 H 6 V 54 H 14"
        fill="none"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Right bracket */}
      <path
        d="M 50 10 H 58 V 54 H 50"
        fill="none"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Letterform compressed slightly to fit inside the brackets */}
      <CoreLetterform scale={0.78} offsetX={8} offsetY={6} />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Variant C: rounded-square seal — "audit-grade stamp"
// ---------------------------------------------------------------------------
function SealMark({
  size = 28,
  title,
  className,
  ...props
}: LogoProps) {
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role="img"
      aria-label={title}
      className={cn("text-foreground", className)}
      {...props}
    >
      <title>{title}</title>
      {/* Rounded-square frame */}
      <rect
        x="4"
        y="4"
        width="56"
        height="56"
        rx="12"
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
      />
      {/* Letterform sized to fit inside the seal with a bit of breathing room */}
      <CoreLetterform scale={0.82} offsetX={6} offsetY={4} />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Wordmark — text-only "annexkit" with the leading "a" subtly tinted in
// the cobalt accent so the lowercase 'a' echoes the one in the
// monogram. Lowercase reads as "developer tool" (cf. vercel, linear,
// stripe wordmarks).
// ---------------------------------------------------------------------------
interface WordmarkProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  /** When true, the leading "a" is rendered in the foreground tone instead
   *  of the cobalt accent. Use for tight contrast contexts (e.g. inside a
   *  coloured badge) where the cobalt would clash. */
  monoTone?: boolean;
}

export function LogoWordmark({
  size = "md",
  className,
  monoTone = false,
}: WordmarkProps) {
  const cls = {
    sm: "text-base",
    md: "text-lg",
    lg: "text-2xl",
  }[size];
  return (
    <span
      className={cn(
        "inline-flex items-baseline font-semibold tracking-tight",
        cls,
        className,
      )}
      style={{ letterSpacing: "-0.028em" }}
    >
      <span
        aria-hidden
        className={monoTone ? "" : "text-[var(--brand-accent)]"}
      >
        a
      </span>
      <span>nnexkit</span>
    </span>
  );
}

// ---------------------------------------------------------------------------
// Lockup — mark + wordmark side-by-side. Default for headers.
// ---------------------------------------------------------------------------
interface LockupProps {
  variant?: LogoStyle;
  size?: "sm" | "md" | "lg";
  className?: string;
  /** When true, hide the wordmark (icon-only mode). */
  iconOnly?: boolean;
  /** Pass through to LogoWordmark — see there. */
  monoTone?: boolean;
}

export function LogoLockup({
  variant = "monogram",
  size = "md",
  className,
  iconOnly = false,
  monoTone = false,
}: LockupProps) {
  const markPx = { sm: 22, md: 28, lg: 36 }[size];

  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <LogoMark variant={variant} size={markPx} />
      {!iconOnly && <LogoWordmark size={size} monoTone={monoTone} />}
    </span>
  );
}
