/**
 * AnnexKit logo — three variants in one file so we can A/B them without
 * juggling files.
 *
 * Brand insight: "AnnexKit" → a *kit* for delivering *Annex IV* technical
 * documentation. The mark leans into the developer-tool half of the
 * positioning — a bold "A" letterform, with a small cobalt dot anchored
 * at the right diagonal. The dot reads as a "live signal" (telemetry,
 * AI, span emission) and ties the entire app to the cobalt accent. The
 * wordmark is lowercase to read as "developer tool" rather than
 * "consultancy SaaS".
 *
 *   - <LogoMark>      : icon-only (16-200 px). Use for favicons, sidebar
 *                       collapsed states, app-icon contexts.
 *   - <LogoWordmark>  : "annexkit" with subtle cobalt-tinted "a". Use
 *                       when the icon would be redundant (footer copy).
 *   - <LogoLockup>    : mark + wordmark side-by-side. Default for headers
 *                       and any place we want full brand presence.
 *
 * The mark itself ships in 3 variants selectable via a `variant` prop:
 *   - "monogram" — bold A + cobalt span dot (recommended, default).
 *   - "bracket"  — bracket-framed A; signals "code / kit container".
 *   - "seal"     — rounded-square sigillo with A inside; signals "audit-grade".
 *
 * Colour: the A strokes use `currentColor` so the mark inherits the
 * surrounding text colour (light/dark theme flips for free). The cobalt
 * accent is hard-coded to the brand token so it stays legible against
 * any background.
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

// ---------------------------------------------------------------------------
// Variant A: bold A monogram + cobalt span dot (recommended, default)
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
      {/* Bold "A" letterform — geometric, sans-serif. Built as 3 filled
          shapes so it stays crisp at favicon sizes (no anti-aliased
          curves that smear at 16px). Coordinates picked on a 64-grid. */}
      <g fill="currentColor">
        {/* Left diagonal stroke */}
        <path d="M 24 14 L 6 52 H 14 L 30 18 Z" />
        {/* Right diagonal stroke */}
        <path d="M 40 14 L 58 52 H 50 L 34 18 Z" />
        {/* Bridge (apex / top) — joins the two diagonals into a closed A */}
        <path d="M 24 14 L 40 14 L 38 22 L 26 22 Z" />
        {/* Crossbar — slightly above mid-height for a designed feel */}
        <rect x="18" y="34" width="28" height="5" rx="1" />
      </g>
      {/* Cobalt span dot — anchored bottom-right of the bounding box.
          Reads as "live telemetry / AI signal", ties the mark to the
          brand accent. Always cobalt regardless of theme. */}
      <circle cx="55" cy="48" r="5" fill="var(--brand-cobalt)" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Variant B: bracket-framed A — "code container / kit"
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
        d="M 18 10 H 8 V 54 H 18"
        fill="none"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Right bracket */}
      <path
        d="M 46 10 H 56 V 54 H 46"
        fill="none"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* A inside the brackets — slightly compressed so it fits */}
      <g fill="currentColor">
        <path d="M 28 18 L 20 48 H 26 L 27.5 42 H 36.5 L 38 48 H 44 L 36 18 Z M 29 36 L 35 36 L 32 24 Z" />
      </g>
      {/* Cobalt crossbar accent */}
      <rect x="28" y="34" width="8" height="3" rx="0.5" fill="var(--brand-cobalt)" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Variant C: rounded-square seal with A inside — "audit-grade stamp"
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
      {/* A inside */}
      <g fill="currentColor">
        <path d="M 32 16 L 18 48 H 24 L 26 42 H 38 L 40 48 H 46 L 32 16 Z M 28 36 L 36 36 L 32 24 Z" />
      </g>
      {/* Cobalt dot — bottom-right corner of the A, like a verification stamp */}
      <circle cx="44" cy="46" r="3" fill="var(--brand-cobalt)" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Wordmark — text-only "annexkit" with the leading "a" subtly tinted in
// the cobalt accent so the dual identity (annex + kit) stays visible
// even without the icon. Lowercase reads as "developer tool" (cf. vercel,
// linear, stripe wordmarks).
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
        className={monoTone ? "" : "text-[var(--brand-cobalt)]"}
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
