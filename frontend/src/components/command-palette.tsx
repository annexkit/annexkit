"use client";

/**
 * Cmd-K / Ctrl-K global command palette.
 *
 * Linear / Raycast / Vercel pattern. The single most "premium dev-tool"
 * interaction a marketing site can ship — visitors who hit ⌘K
 * immediately register the product as serious infrastructure.
 *
 * Mount-point: <Layout> root (see app/layout.tsx). Listens for the
 * shortcut globally; opens a centred dialog overlay with fuzzy search
 * across navigation, free-tool actions, external links, and theme.
 *
 * Architecture:
 *   - cmdk for the command primitive (search + keyboard nav + list)
 *   - One file, ~280 LOC. No sub-components — the commands list is
 *     the only thing that changes; everything else is wrapping.
 *   - Static commands array — search performance scales with O(n)
 *     across ~20 items, no virtualisation needed.
 *
 * Trust slug for "Sample trust page" → /trust/velmara-saas (the demo
 * tenant seeded by scripts/seed_demo.py). If you rename the slug
 * there, change DEMO_TRUST_SLUG below.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import {
  ArrowRight,
  ArrowUpRight,
  Beaker,
  FileDown,
  FileText,
  Github,
  Home as HomeIcon,
  LifeBuoy,
  Moon,
  Package,
  Play,
  Search,
  Sun,
} from "lucide-react";

import { useTheme } from "@/components/theme-provider";
import { cn } from "@/lib/utils";

const DEMO_TRUST_SLUG = "velmara-saas";

type CommandShape = {
  id: string;
  label: string;
  keywords?: string[];
  icon: React.ComponentType<{ className?: string }>;
  /** Either an internal route or an external URL. */
  href?: string;
  /** Optional in-app action (theme toggle etc.). */
  action?: () => void;
  /** True when href starts with http(s) — render external icon. */
  external?: boolean;
  /** Display group heading. */
  group: "Navigation" | "Free tools" | "Trust" | "External" | "Settings";
};

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  // cmdk auto-focuses Command.Input only on first mount. When the
  // palette is opened from a mouse click (not a keyboard shortcut),
  // focus stays on the clicked button until we explicitly move it.
  // The ref + useEffect below forces focus to the input every time
  // the palette opens, regardless of trigger source.
  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (!open) return;
    // Two rAFs — first lets cmdk mount the input, second lets the
    // dialog become focusable. One rAF alone is flaky on some
    // browsers (Safari fires the click handler before paint).
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    });
  }, [open]);
  const { theme, setTheme } = useTheme();

  // Global keyboard listener — ⌘K on macOS, Ctrl+K elsewhere.
  // Also closes on Escape (cmdk handles that internally, no extra
  // listener needed).
  useEffect(() => {
    function onKeydown(e: KeyboardEvent) {
      const isCmdK =
        (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k";
      if (!isCmdK) return;
      e.preventDefault();
      setOpen((v) => !v);
    }
    window.addEventListener("keydown", onKeydown);
    return () => window.removeEventListener("keydown", onKeydown);
  }, []);

  // Disable page scroll while the palette is open. Tiny detail, but
  // every premium product gets this right.
  useEffect(() => {
    if (!open) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previous;
    };
  }, [open]);

  const close = useCallback(() => setOpen(false), []);

  const commands: CommandShape[] = [
    // Navigation ---------------------------------------------------------
    {
      id: "nav-home",
      label: "Home",
      keywords: ["product", "overview", "landing"],
      icon: HomeIcon,
      href: "/",
      group: "Navigation",
    },
    {
      id: "nav-tools",
      label: "Tools — hub",
      keywords: ["free", "utilities"],
      icon: Beaker,
      href: "/tools",
      group: "Navigation",
    },
    {
      id: "nav-pricing",
      label: "Pricing",
      keywords: ["plans", "tiers", "cost", "money"],
      icon: Package,
      href: "/pricing",
      group: "Navigation",
    },
    {
      id: "nav-docs",
      label: "Documentation (GitHub README)",
      keywords: ["docs", "guide", "resources", "quickstart"],
      icon: LifeBuoy,
      href: "https://github.com/annexkit/annexkit#readme",
      external: true,
      group: "Navigation",
    },

    // Free tools — direct ------------------------------------------------
    {
      id: "tool-annex-iv",
      label: "Generate an Annex IV PDF",
      keywords: ["annex 4", "pdf", "generator", "form", "documentation"],
      icon: FileDown,
      href: "/tools/annex-iv-generator",
      group: "Free tools",
    },
    {
      id: "tool-schema",
      label: "Download Article 12 JSON Schema",
      keywords: ["article 12", "logging", "json schema", "otel", "validator"],
      icon: FileText,
      href: "/tools/logging-schema",
      group: "Free tools",
    },
    {
      id: "tool-demo",
      label: "Open the live Annex IV demo",
      keywords: ["demo", "preview", "examples", "scenarios"],
      icon: Play,
      href: "/demo/annex-iv",
      group: "Free tools",
    },

    // Trust pages --------------------------------------------------------
    {
      id: "trust-sample",
      label: "Sample trust page",
      keywords: ["trust", "public", "demo tenant"],
      icon: Beaker,
      href: `/trust/${DEMO_TRUST_SLUG}`,
      group: "Trust",
    },

    // External -----------------------------------------------------------
    {
      id: "ext-github",
      label: "GitHub repository",
      keywords: ["source", "code", "open source"],
      icon: Github,
      href: "https://github.com/annexkit/annexkit",
      external: true,
      group: "External",
    },
    {
      id: "ext-pypi",
      label: "PyPI package",
      keywords: ["pip install annexkit", "python", "sdk"],
      icon: Package,
      href: "https://pypi.org/project/annexkit/",
      external: true,
      group: "External",
    },
    {
      id: "ext-eurlex",
      label: "EU AI Act — Reg. (EU) 2024/1689",
      keywords: ["regulation", "law", "official text", "eur-lex"],
      icon: ArrowUpRight,
      href: "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
      external: true,
      group: "External",
    },

    // Settings -----------------------------------------------------------
    {
      id: "settings-theme",
      label: theme === "dark" ? "Switch to light theme" : "Switch to dark theme",
      keywords: ["dark mode", "light mode", "theme", "appearance"],
      icon: theme === "dark" ? Sun : Moon,
      action: () => setTheme(theme === "dark" ? "light" : "dark"),
      group: "Settings",
    },
  ];

  function runCommand(c: CommandShape) {
    close();
    if (c.action) {
      // Microtask so the dialog closes visually before the action runs.
      queueMicrotask(c.action);
      return;
    }
    if (!c.href) return;
    if (c.external) {
      window.open(c.href, "_blank", "noopener,noreferrer");
      return;
    }
    router.push(c.href);
  }

  // Group commands for the visible list.
  const groups = groupBy(commands, (c) => c.group);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-background/70 px-4 pt-[14vh] backdrop-blur-sm"
      onClick={(e) => {
        // Backdrop click closes; cmdk dialog inside stops propagation.
        if (e.target === e.currentTarget) close();
      }}
      role="presentation"
    >
      <Command
        label="Command palette"
        loop
        className={cn(
          "w-full max-w-xl overflow-hidden rounded-xl border border-border bg-card shadow-2xl",
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 border-b border-border px-4">
          <Search className="size-4 text-muted-foreground" />
          <Command.Input
            ref={inputRef}
            placeholder="Search tools, pages, settings…"
            className="h-12 w-full bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
          <kbd className="hidden rounded border border-border bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground sm:inline-flex">
            esc
          </kbd>
        </div>

        <Command.List className="max-h-[420px] overflow-y-auto p-2">
          <Command.Empty className="px-4 py-6 text-center text-sm text-muted-foreground">
            No matching commands.
          </Command.Empty>

          {Object.entries(groups).map(([group, items]) => (
            <Command.Group
              key={group}
              heading={group}
              className="text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-2"
            >
              {items.map((c) => {
                const Icon = c.icon;
                return (
                  <Command.Item
                    key={c.id}
                    value={`${c.label} ${(c.keywords ?? []).join(" ")}`}
                    onSelect={() => runCommand(c)}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm text-foreground transition-colors",
                      "data-[selected=true]:bg-secondary",
                      "data-[selected=true]:text-foreground",
                      "cursor-pointer",
                    )}
                  >
                    <Icon className="size-4 shrink-0 text-muted-foreground group-data-[selected=true]:text-foreground" />
                    <span className="flex-1 truncate">{c.label}</span>
                    {c.external ? (
                      <ArrowUpRight className="size-3.5 text-muted-foreground" />
                    ) : (
                      <ArrowRight className="size-3.5 text-muted-foreground opacity-0 transition-opacity data-[selected=true]:opacity-100" />
                    )}
                  </Command.Item>
                );
              })}
            </Command.Group>
          ))}
        </Command.List>

        <div className="flex items-center justify-between border-t border-border bg-muted/40 px-4 py-2 text-[11px] text-muted-foreground">
          <span className="flex items-center gap-2">
            <kbd className="rounded border border-border bg-card px-1.5 py-0.5 font-medium">
              ↑↓
            </kbd>
            navigate
            <kbd className="ml-2 rounded border border-border bg-card px-1.5 py-0.5 font-medium">
              ↵
            </kbd>
            select
          </span>
          <span>AnnexKit · ⌘K</span>
        </div>
      </Command>
    </div>
  );
}

function groupBy<T, K extends string>(
  arr: T[],
  keyFn: (x: T) => K,
): Record<K, T[]> {
  const out: Partial<Record<K, T[]>> = {};
  for (const item of arr) {
    const k = keyFn(item);
    (out[k] ??= []).push(item);
  }
  return out as Record<K, T[]>;
}
