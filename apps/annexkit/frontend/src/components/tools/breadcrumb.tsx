import Link from "next/link";
import { ChevronRight } from "lucide-react";

/**
 * Tiny breadcrumb used on the /tools/* and /demo/* pages.
 * Mirror of Konformia's pattern — see /strumenti/page.tsx there.
 */
export function ToolsBreadcrumb({
  items,
}: {
  items: Array<{ label: string; href?: string }>;
}) {
  return (
    <nav
      aria-label="Breadcrumb"
      className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground"
    >
      <Link href="/" className="hover:text-foreground">
        AnnexKit
      </Link>
      {items.map((item, idx) => (
        <span key={`${item.label}-${idx}`} className="flex items-center gap-1.5">
          <ChevronRight className="size-3" aria-hidden />
          {item.href ? (
            <Link href={item.href} className="hover:text-foreground">
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground/80">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
