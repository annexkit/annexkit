"use client";

/**
 * Header nav link with active-page indicator.
 *
 * Uses `usePathname()` to detect the current route and applies a
 * cobalt underline + foreground text colour when active. Behaviour:
 *
 *   - exact match  → active (e.g. /tools matches only /tools, not /tools/x)
 *   - prefix match → active when `prefix` prop is true (e.g. /tools
 *     matches /tools/annex-iv-generator too)
 *
 * Why a separate component instead of inlining in site-header:
 * site-header is a server component (server-renders the static nav
 * structure). usePathname is client-only. Extracting just the link
 * keeps the header server-rendered and only ships ~1KB of client JS
 * for the active-indicator logic.
 */

import { usePathname } from "next/navigation";
import Link from "next/link";

import { cn } from "@/lib/utils";

export function NavLink({
  href,
  label,
  prefix = false,
  className,
}: {
  href: string;
  label: string;
  /** Treat the link as active for any path starting with `href`. */
  prefix?: boolean;
  className?: string;
}) {
  const pathname = usePathname();
  const isActive = prefix
    ? pathname === href || pathname.startsWith(`${href}/`)
    : pathname === href;

  return (
    <Link
      href={href}
      aria-current={isActive ? "page" : undefined}
      className={cn(
        "relative hidden rounded-md px-3 py-2 transition-colors md:inline-flex",
        isActive
          ? "text-foreground"
          : "text-muted-foreground hover:bg-secondary hover:text-foreground",
        className,
      )}
    >
      {label}
      {isActive && (
        // 2px cobalt underline pinned to the bottom of the link box.
        // Inset 12px on each side so it spans the label, not the full
        // padding box — reads as an underline, not a bottom border.
        <span
          aria-hidden
          className="pointer-events-none absolute inset-x-3 -bottom-px h-[2px] rounded-full bg-[var(--brand-cobalt)]"
        />
      )}
    </Link>
  );
}
