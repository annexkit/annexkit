import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

interface CrossLink {
  href: string;
  label: string;
  description: string;
}

const ALL_LINKS: CrossLink[] = [
  {
    href: "/tools/annex-iv-generator",
    label: "Annex IV PDF generator",
    description:
      "Fill a 5-minute form, get a real EU AI Act Annex IV PDF. " +
      "Deterministic classifier. Email required.",
  },
  {
    href: "/demo/annex-iv",
    label: "Live Annex IV demo",
    description:
      "Three pre-built scenarios (loan / CV / customer-support). " +
      "Realistic PDFs without filling a form. No install.",
  },
  {
    href: "/tools/logging-schema",
    label: "Article 12 logging schema",
    description:
      "JSON Schema for AnnexKit spans, with each field mapped to " +
      "its AI Act Article 12 clause. Free download.",
  },
];

/**
 * "See also" footer for tool pages — links to the OTHER tools so a
 * visitor doesn't dead-end. Filter out the current page by passing its
 * href as ``exclude``.
 */
export function ToolsCrossLinks({ exclude }: { exclude: string }) {
  const others = ALL_LINKS.filter((l) => l.href !== exclude);
  return (
    <section className="mt-16 border-t border-border pt-10">
      <h2 className="mb-1 text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
        See also
      </h2>
      <p className="mb-6 text-sm text-muted-foreground">
        Other free tools — pick the one that matches what you&rsquo;re
        trying to do.
      </p>
      <ul className="surface-card divide-y divide-border overflow-hidden p-0">
        {others.map((l) => (
          <li key={l.href}>
            <Link
              href={l.href}
              className="flex items-start gap-4 px-5 py-4 transition hover:bg-secondary/40"
            >
              <ArrowUpRight className="mt-0.5 size-4 shrink-0 text-[var(--brand-cobalt)]" />
              <div className="flex flex-col gap-1">
                <span className="text-sm font-semibold tracking-tight text-foreground">
                  {l.label}
                </span>
                <span className="text-xs text-muted-foreground">
                  {l.description}
                </span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
