/**
 * Site-wide footer.
 *
 * Four columns on desktop (logo+copy / Product / Resources / Legal),
 * stacked vertically on mobile. The very bottom strip carries the
 * permanent disclaimer required by the project non-negotiables — that
 * line never moves and must stay bilingual EN/IT.
 *
 * Link policy
 * -----------
 * External links open in a new tab; internal links use Next's <Link>.
 * Anything that doesn't exist yet (e.g. /privacy in pre-launch builds)
 * still routes here so a 404 is the worst-case rather than a dead anchor.
 */

import Link from "next/link";

import { LogoLockup } from "@/components/logo";

interface FooterLink {
  label: string;
  href: string;
  external?: boolean;
}

interface FooterSection {
  heading: string;
  links: FooterLink[];
}

const SECTIONS: FooterSection[] = [
  {
    heading: "Product",
    links: [
      { label: "Pricing", href: "/pricing" },
      { label: "Sample trust page", href: "/trust/velmara-saas" },
      {
        label: "Quickstart",
        href: "https://github.com/annexkit/annexkit#quickstart",
        external: true,
      },
      {
        label: "GitHub",
        href: "https://github.com/annexkit/annexkit",
        external: true,
      },
      {
        label: "PyPI",
        href: "https://pypi.org/project/annexkit/",
        external: true,
      },
    ],
  },
  {
    heading: "Free tools",
    links: [
      { label: "All tools", href: "/tools" },
      { label: "Annex IV generator", href: "/tools/annex-iv-generator" },
      { label: "Article 12 schema", href: "/tools/logging-schema" },
      { label: "Live demo", href: "/demo/annex-iv" },
    ],
  },
  {
    heading: "Resources",
    links: [
      {
        label: "Documentation",
        href: "https://github.com/annexkit/annexkit#readme",
        external: true,
      },
      {
        label: "Changelog",
        href: "https://github.com/annexkit/annexkit/releases",
        external: true,
      },
      {
        label: "Architecture",
        href: "https://github.com/annexkit/annexkit/blob/main/AGENTS.md",
        external: true,
      },
      {
        label: "Reg. (EU) 2024/1689",
        href: "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
        external: true,
      },
    ],
  },
  {
    heading: "Legal",
    links: [
      { label: "Privacy", href: "/privacy" },
      { label: "Terms", href: "/terms" },
      { label: "Cookie policy", href: "/cookies" },
      { label: "Imprint", href: "/imprint" },
    ],
  },
];

export function SiteFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-24 border-t border-border/60">
      <div className="mx-auto max-w-6xl px-6 py-14">
        {/* Top — 4 columns */}
        <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-[1.4fr_1fr_1fr_1fr_1fr]">
          {/* Brand column */}
          <div className="space-y-4">
            <LogoLockup size="md" />
            <p className="max-w-xs text-sm text-muted-foreground">
              EU AI Act compliance pipeline for developers. One decorator
              on your inference call; audit-ready Annex IV docs out.
            </p>
            <p className="text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-2">
                <span
                  aria-hidden
                  className="size-1.5 rounded-full bg-[var(--brand-cobalt)]"
                />
                EU-hosted · Falkenstein / Helsinki
              </span>
            </p>
          </div>

          {SECTIONS.map((section) => (
            <FooterColumn key={section.heading} section={section} />
          ))}
        </div>

        {/* Bottom strip — permanent disclaimer + copyright */}
        <div className="mt-12 border-t border-border/40 pt-6 text-xs text-muted-foreground">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <p className="max-w-3xl leading-relaxed">
              <strong className="font-semibold text-foreground">
                AnnexKit is not a law firm / AnnexKit non è uno studio
                legale.
              </strong>{" "}
              Trust pages render technical declarations made by the named
              tenant; legal interpretation is the responsibility of the
              tenant&rsquo;s legal counsel.
            </p>
            <p className="shrink-0 sm:text-right">
              © {year} AnnexKit ·{" "}
              <a
                href="mailto:founder@annexkit.dev"
                className="hover:text-foreground"
              >
                founder@annexkit.dev
              </a>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}

function FooterColumn({ section }: { section: FooterSection }) {
  return (
    <div className="space-y-3 text-sm">
      <h3 className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
        {section.heading}
      </h3>
      <ul className="space-y-2">
        {section.links.map((link) => (
          <li key={link.href}>
            {link.external ? (
              <a
                href={link.href}
                target="_blank"
                rel="noreferrer"
                className="text-muted-foreground transition-colors hover:text-foreground"
              >
                {link.label}
              </a>
            ) : (
              <Link
                href={link.href}
                className="text-muted-foreground transition-colors hover:text-foreground"
              >
                {link.label}
              </Link>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
