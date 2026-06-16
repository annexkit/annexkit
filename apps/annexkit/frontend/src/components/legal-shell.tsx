/**
 * Shared frame for the four legal pages (Privacy, Terms, Cookies,
 * Imprint).
 *
 * Why a custom shell instead of just letting Tailwind's `prose` style
 * the markup
 *   - We don't ship `@tailwindcss/typography`, and adding it for four
 *     pages is overkill.
 *   - The brand wants a slightly tighter, more "engineering doc" feel
 *     than `prose` ships by default — closer to Stripe's legal pages
 *     than to Medium's.
 *
 * The TOC sticks to the right on desktop because legal pages are scannable
 * documents — readers usually want to jump to a specific clause, not read
 * cover-to-cover.
 */

"use client";

import { useMemo } from "react";

interface SectionDef {
  /** Slug used as the heading `id` and the TOC anchor. */
  id: string;
  /** Human-readable title shown in the TOC and as the H2. */
  title: string;
}

interface LegalShellProps {
  /** Page title (rendered in the H1). */
  title: string;
  /** "Last updated" date — ISO string preferred. */
  updated: string;
  /** Plain-English summary of what this document is. Shown above the TOC. */
  summary?: React.ReactNode;
  /** Sections in document order. */
  sections: SectionDef[];
  /** When true, renders a prominent "pre-launch placeholder" banner above
   * the summary so visitors don't take the bracketed values literally. */
  preLaunch?: boolean;
  children: React.ReactNode;
}

export function LegalShell({
  title,
  updated,
  summary,
  sections,
  preLaunch = false,
  children,
}: LegalShellProps) {
  const formattedDate = useMemo(
    () =>
      new Date(updated).toLocaleDateString("en-GB", {
        year: "numeric",
        month: "long",
        day: "numeric",
      }),
    [updated],
  );

  return (
    <div className="mx-auto max-w-6xl px-6 py-14">
      <header className="space-y-3">
        <span className="eyebrow">Legal</span>
        <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          {title}
        </h1>
        <p className="text-sm text-muted-foreground">
          Last updated{" "}
          <time dateTime={updated} className="font-medium">
            {formattedDate}
          </time>
        </p>
      </header>

      <div className="mt-12 grid gap-12 lg:grid-cols-[1fr_220px]">
        <article className="legal-prose space-y-10">
          {preLaunch && <PreLaunchNotice />}
          {summary && (
            <section className="surface-card border-l-2 border-l-[var(--brand-accent)] p-5 text-sm leading-relaxed text-muted-foreground">
              {summary}
            </section>
          )}
          {children}
        </article>

        <aside className="lg:sticky lg:top-20 lg:h-fit">
          <h2 className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            On this page
          </h2>
          <ul className="mt-3 space-y-2 border-l border-border/60 pl-3 text-sm">
            {sections.map((s) => (
              <li key={s.id}>
                <a
                  href={`#${s.id}`}
                  className="block text-muted-foreground transition-colors hover:text-foreground"
                >
                  {s.title}
                </a>
              </li>
            ))}
          </ul>
        </aside>
      </div>
    </div>
  );
}

/**
 * Pre-launch banner — shown on legal pages until the company is
 * formally registered. Communicates honestly that the document is
 * scaffolding rather than letting visitors squint at literal
 * "[LEGAL NAME]" / "[VAT]" placeholders inline.
 *
 * Once the VAT registration lands, set preLaunch={false} on each
 * legal page and grep for "[" in src/app/{privacy,terms,imprint}/
 * to find the values to replace.
 */
function PreLaunchNotice() {
  return (
    <aside
      role="note"
      className="rounded-lg border border-amber-300/50 bg-amber-50/60 p-5 text-sm leading-relaxed text-amber-950 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-100"
    >
      <p>
        <strong className="font-semibold">
          Pre-launch placeholder.
        </strong>{" "}
        AnnexKit is in early access ahead of formal company registration.
        Bracketed values like <code className="font-mono text-xs">[LEGAL NAME]</code>{" "}
        or <code className="font-mono text-xs">[VAT]</code> are stand-ins
        — they&rsquo;ll be replaced with the registered details before
        we accept paying customers. The structure of this document
        reflects our intended policy and is binding on the founder
        operating the early-access programme today, but does not yet
        bind a registered legal entity.
      </p>
      <p className="mt-2">
        Questions in the meantime →{" "}
        <a
          href="mailto:founder@annexkit.dev"
          className="font-medium underline underline-offset-4"
        >
          founder@annexkit.dev
        </a>
        .
      </p>
    </aside>
  );
}

/* Inline prose styling — scoped to the shell only. Keeps headings tight,
   paragraphs comfortable, and code legible without pulling in the full
   Tailwind Typography plugin for four pages. */
export function LegalProseStyles() {
  return (
    <style>{`
      .legal-prose h2 {
        font-size: 1.5rem;
        font-weight: 600;
        letter-spacing: -0.018em;
        color: var(--foreground);
        margin-top: 2.5rem;
        margin-bottom: 0.75rem;
        padding-top: 0.5rem;
        scroll-margin-top: 5rem;
      }
      .legal-prose h2:first-child { margin-top: 0; }
      .legal-prose h3 {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--foreground);
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
      }
      .legal-prose p {
        color: var(--muted-foreground);
        line-height: 1.7;
        margin-bottom: 1rem;
      }
      .legal-prose ul, .legal-prose ol {
        color: var(--muted-foreground);
        line-height: 1.7;
        margin-bottom: 1rem;
        padding-left: 1.25rem;
      }
      .legal-prose li { margin-bottom: 0.4rem; }
      .legal-prose ul li { list-style: disc; }
      .legal-prose ol li { list-style: decimal; }
      .legal-prose a {
        color: var(--brand-accent);
        text-underline-offset: 4px;
      }
      .legal-prose a:hover { text-decoration: underline; }
      .legal-prose strong {
        color: var(--foreground);
        font-weight: 600;
      }
      .legal-prose code {
        font-family: var(--font-mono);
        font-size: 0.875em;
        padding: 0.1rem 0.35rem;
        border-radius: 4px;
        background: var(--secondary);
        color: var(--foreground);
      }
    `}</style>
  );
}
