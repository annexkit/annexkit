"use client";

/**
 * Sticky right-rail table of contents.
 *
 * Pattern: Stripe docs / Linear changelog / Vercel docs. Sits on the
 * right at `lg+` viewports and tracks the section currently in the
 * viewport via IntersectionObserver, highlighting it in the rail.
 * Below `lg`, the rail is hidden — long-form scroll already works on
 * mobile.
 *
 * Usage:
 *
 *   <div className="lg:grid lg:grid-cols-[1fr_220px] lg:gap-12">
 *     <article>
 *       <h2 id="intro">…</h2>
 *       …
 *       <h2 id="usage">…</h2>
 *       …
 *     </article>
 *     <PageTOC sections={[
 *       { id: "intro", label: "Introduction" },
 *       { id: "usage", label: "Usage" },
 *     ]} />
 *   </div>
 *
 * The IDs must exist as `id=` attributes on real elements in the
 * article DOM — that's the contract the observer relies on. If an ID
 * is missing the row just never highlights; no console warning,
 * because hot-reload sometimes drops elements transiently and a
 * warning per render would be noise.
 */

import { useEffect, useState } from "react";
import Link from "next/link";

import { cn } from "@/lib/utils";

export interface TocSection {
  id: string;
  label: string;
}

export function PageTOC({
  sections,
  className,
}: {
  sections: TocSection[];
  className?: string;
}) {
  const [activeId, setActiveId] = useState<string | null>(
    sections[0]?.id ?? null,
  );

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (sections.length === 0) return;

    // rootMargin: shrink the viewport from the top so "active" flips
    // when a heading crosses ~25% from the top, not 0% (which feels
    // laggy — the user sees the section before the rail catches up).
    // Negative bottom margin so we ignore sections at the very bottom
    // until the user scrolls them up.
    const observer = new IntersectionObserver(
      (entries) => {
        // Take the topmost intersecting entry — multiple sections can
        // be intersecting at once during fast scroll; the one closest
        // to the top edge is what the user is "on".
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort(
            (a, b) =>
              a.boundingClientRect.top - b.boundingClientRect.top,
          );
        if (visible.length > 0) {
          setActiveId(visible[0].target.id);
        }
      },
      {
        rootMargin: "-25% 0px -60% 0px",
        threshold: 0,
      },
    );

    for (const s of sections) {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    }

    return () => observer.disconnect();
  }, [sections]);

  if (sections.length === 0) return null;

  return (
    <aside
      // Sticky sidebar. The top offset matches the sticky header
      // height (14 = 56px) plus a breath of vertical air so the rail
      // doesn't bump the nav.
      className={cn(
        "hidden lg:block",
        "sticky top-20 self-start",
        // Subtle left rule, generous padding — reads as a table of
        // contents in a printed book, not a sidebar widget.
        "border-l border-border pl-5",
        className,
      )}
      aria-label="On this page"
    >
      <p className="mb-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
        On this page
      </p>
      <ul className="space-y-1.5">
        {sections.map((s) => {
          const isActive = s.id === activeId;
          return (
            <li key={s.id}>
              <Link
                href={`#${s.id}`}
                className={cn(
                  "block rounded-sm text-xs leading-relaxed transition-colors",
                  isActive
                    ? "font-medium text-foreground"
                    : "text-muted-foreground hover:text-foreground",
                )}
                // Smooth scroll the section into view; the URL hash
                // updates so the user can copy a deep link.
                onClick={(e) => {
                  const el = document.getElementById(s.id);
                  if (el) {
                    e.preventDefault();
                    el.scrollIntoView({ behavior: "smooth", block: "start" });
                    // Push the hash so refresh / share works.
                    history.replaceState(null, "", `#${s.id}`);
                  }
                }}
              >
                {s.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
