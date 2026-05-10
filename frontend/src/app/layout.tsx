/**
 * Root layout for the whole AnnexKit frontend.
 *
 * Every route in `src/app/**` renders inside <body> here. Anything
 * feature-specific belongs in a nested layout (e.g. `app/trust/layout.tsx`).
 *
 * What this file does:
 *   - Declares <html> / <body> with the dark-canonical class context.
 *   - Loads Geist + Geist Mono via next/font for zero CLS.
 *   - Ships an inline "no-flash" script that picks the right theme class
 *     before React hydrates, so reload doesn't flicker.
 *   - Exports the canonical site metadata (<title>, OG, Twitter, robots).
 *   - Wraps children in <ThemeProvider> so the toggle can take over
 *     post-hydration.
 *   - The Header + Footer here are temporary scaffolding; Step 3 swaps
 *     them for the proper marketing chrome with full nav, theme toggle,
 *     and "Get started" CTA.
 */

import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { ThemeProvider, THEME_STORAGE_KEY } from "@/components/theme-provider";

// Inline script that runs BEFORE React hydrates. Reads the user's saved
// choice from localStorage and applies the right class to <html> so the
// first paint already uses the right palette. Without this, a user who
// picked dark last session sees a split-second of light on every page
// load — ugly, and the bug theme libs were built to fix.
//
// Default (no stored value) is "system" — for AnnexKit's audience
// (engineers, who skew dark) that's almost always the right first
// impression. Keep this script small and dependency-free.
const THEME_NO_FLASH_SCRIPT = `
(function () {
  try {
    var stored = localStorage.getItem('${THEME_STORAGE_KEY}');
    var dark = stored === 'dark' ||
      ((stored === null || stored === 'system') &&
        window.matchMedia &&
        window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (dark) document.documentElement.classList.add('dark');
  } catch (e) {
    /* localStorage disabled — fall through to light, no harm. */
  }
})();
`;

// next/font/google self-hosts the font at build time and emits a CSS
// variable our Tailwind theme references via @theme inline.
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const SITE_ORIGIN =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://annexkit.dev";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_ORIGIN),
  title: {
    default: "AnnexKit — EU AI Act compliance pipeline for developers",
    template: "%s — AnnexKit",
  },
  description:
    "One decorator on your inference call. Audit-ready Annex IV " +
    "documentation under EU Regulation 2024/1689, generated from your " +
    "runtime telemetry. Open-source, EU-hosted, sub-€100/month.",
  applicationName: "AnnexKit",
  keywords: [
    "EU AI Act",
    "Annex IV",
    "AI compliance",
    "AI Act trust center",
    "AI governance",
    "Reg. 2024/1689",
    "LLM observability",
    "audit log",
  ],
  authors: [{ name: "AnnexKit" }],
  creator: "AnnexKit",
  publisher: "AnnexKit",
  openGraph: {
    type: "website",
    siteName: "AnnexKit",
    title: "AnnexKit — EU AI Act compliance pipeline for developers",
    description:
      "Runtime telemetry from your LLM-powered code, turned into " +
      "audit-ready Annex IV documentation. One decorator on your " +
      "inference call.",
    locale: "en_GB",
    url: SITE_ORIGIN,
  },
  twitter: {
    card: "summary_large_image",
    title: "AnnexKit — EU AI Act compliance pipeline for developers",
    description:
      "Audit-ready Annex IV docs from your LLM telemetry. Open-source, " +
      "EU-hosted, sub-€100/month.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0d14" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      // Silences React's hydration warning when the inline script above
      // mutates <html> before React hydrates — that mutation is the whole
      // point of the script, not a bug.
      suppressHydrationWarning
    >
      <head>
        {/* Must be the first thing in <head> so it runs before any paint. */}
        <script dangerouslySetInnerHTML={{ __html: THEME_NO_FLASH_SCRIPT }} />
      </head>
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <ThemeProvider>
          <SiteHeader />
          <main className="flex-1">{children}</main>
          <SiteFooter />
        </ThemeProvider>
      </body>
    </html>
  );
}
