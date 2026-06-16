"use client";

/**
 * ⌘K hint button — sits in the header, opens the global CommandPalette
 * on click. The visible "⌘K" keycap is the discovery affordance
 * (developer-tool credibility); the search icon is the fallback for
 * users who don't know the shortcut.
 *
 * Why a synthesised KeyboardEvent (not a custom DOM event): the
 * CommandPalette listens for ⌘K/Ctrl-K on window.keydown. Going
 * through that same path guarantees identical behaviour to the
 * keyboard shortcut — including cmdk's auto-focus on the input.
 * Custom events worked but raced React strict-mode effect cleanup
 * intermittently, producing the "click opens but can't type" bug.
 */

import { useEffect, useState } from "react";
import { Search } from "lucide-react";

import { cn } from "@/lib/utils";

export function CmdKHint({ className }: { className?: string }) {
  const [isMac, setIsMac] = useState(false);

  // Cosmetic only — show "⌘K" on macOS, "Ctrl K" elsewhere. Don't read
  // navigator on the server; default to "⌘K" until hydration.
  useEffect(() => {
    setIsMac(
      typeof navigator !== "undefined" &&
        /Mac|iPhone|iPad/.test(navigator.platform),
    );
  }, []);

  function openPalette() {
    window.dispatchEvent(
      new KeyboardEvent("keydown", {
        key: "k",
        metaKey: true,
        ctrlKey: true,
        bubbles: true,
        cancelable: true,
      }),
    );
  }

  return (
    <button
      type="button"
      aria-label="Open command palette"
      onClick={openPalette}
      className={cn(
        "inline-flex items-center gap-2 rounded-md border border-border bg-background/40",
        "px-2.5 py-1.5 text-xs text-muted-foreground",
        "transition-colors hover:border-muted-foreground/30 hover:text-foreground",
        className,
      )}
    >
      <Search className="size-3.5" />
      <span className="hidden md:inline">Search…</span>
      <kbd className="hidden rounded border border-border bg-card px-1.5 py-0.5 font-medium md:inline-block">
        {isMac ? "⌘K" : "Ctrl K"}
      </kbd>
    </button>
  );
}
