/**
 * Top-of-page navigation bar shared by every public route.
 *
 * Sticky, blurred, lives above the brand-wash hero so the hero gradient
 * peeks through. Three responsive states:
 *   - >= md   : full nav (Pricing, Docs, GitHub) + theme toggle + "Get started"
 *   - sm only : nav links collapse, GitHub becomes an icon, "Get started"
 *               stays primary
 *   - mobile  : just logo + GitHub icon + theme toggle (the CTA moves to the
 *               page hero so we don't fight for vertical space in the bar)
 *
 * No mobile drawer yet — the public surface is shallow enough that a
 * vertical menu is overkill. Add one if/when /docs grows to >5 links.
 */

import Link from "next/link";
import { ArrowRight, Github } from "lucide-react";

import { LogoLockup } from "@/components/logo";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";

const NAV_LINKS = [
  { href: "/pricing", label: "Pricing" },
  {
    href: "https://github.com/annexkit/annexkit#readme",
    label: "Docs",
    external: true,
  },
] as const;

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-border/60 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <Link
          href="/"
          aria-label="AnnexKit — home"
          className="rounded-md outline-none focus-visible:ring-2 focus-visible:ring-ring/60"
        >
          <LogoLockup size="md" />
        </Link>

        <nav
          aria-label="Primary"
          className="flex items-center gap-1 text-sm"
        >
          {NAV_LINKS.map((link) =>
            "external" in link ? (
              <a
                key={link.href}
                href={link.href}
                target="_blank"
                rel="noreferrer"
                className="hidden rounded-md px-3 py-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground md:inline-flex"
              >
                {link.label}
              </a>
            ) : (
              <Link
                key={link.href}
                href={link.href}
                className="hidden rounded-md px-3 py-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground md:inline-flex"
              >
                {link.label}
              </Link>
            ),
          )}

          {/* GitHub: text on >=md, icon-only on smaller screens. */}
          <a
            href="https://github.com/annexkit/annexkit"
            target="_blank"
            rel="noreferrer"
            aria-label="AnnexKit on GitHub"
            className="inline-flex items-center gap-2 rounded-md px-3 py-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
          >
            <Github className="size-4" />
            <span className="hidden md:inline">GitHub</span>
          </a>

          <ThemeToggle className="ml-1" />

          <Button size="sm" asChild className="ml-2 hidden sm:inline-flex">
            <Link href="/pricing">
              Get started
              <ArrowRight />
            </Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}
