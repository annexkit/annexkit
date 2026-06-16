/**
 * Single-button theme cycler. One click rotates through the three modes:
 *   system → light → dark → system.
 *
 * Icon convention
 * ---------------
 * The icon shows the CURRENT mode, not the next one. With three modes the
 * "where you're going" trick is confusing, so we follow the simpler
 * convention: Sun for light, Moon for dark, Monitor for system.
 *
 * Hydration note
 * --------------
 * On the very first client render the provider doesn't yet know which
 * theme is applied (the inline `<head>` script mutated <html>, but the
 * React tree still thinks we're rendering with the server snapshot). We'd
 * rather not show the wrong icon for one frame, so we gate on
 * `useHasMounted` and render an invisible placeholder of the same size
 * until the tree catches up.
 */

"use client";

import { useSyncExternalStore } from "react";
import { Monitor, Moon, Sun, type LucideIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTheme, type Theme } from "@/components/theme-provider";

/**
 * Returns `true` only after the client has mounted. Implemented via
 * `useSyncExternalStore` instead of `useEffect + useState` so React 19's
 * `set-state-in-effect` lint rule stays quiet.
 */
function useHasMounted(): boolean {
  return useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
}

const NEXT: Record<Theme, Theme> = {
  system: "light",
  light: "dark",
  dark: "system",
};

const ICON: Record<Theme, LucideIcon> = {
  light: Sun,
  dark: Moon,
  system: Monitor,
};

const LABEL: Record<Theme, string> = {
  light: "Light theme — click for dark",
  dark: "Dark theme — click for system",
  system: "System theme — click for light",
};

export function ThemeToggle({ className }: { className?: string }) {
  const { theme, setTheme } = useTheme();
  const mounted = useHasMounted();

  // Pre-mount placeholder: same outer shape so the surrounding layout
  // doesn't reflow when the real button swaps in.
  if (!mounted) {
    return (
      <Button
        type="button"
        variant="ghost"
        size="icon"
        aria-hidden
        tabIndex={-1}
        className={cn("opacity-0", className)}
      >
        <Sun />
      </Button>
    );
  }

  const Icon = ICON[theme];
  const label = LABEL[theme];

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      role="switch"
      // aria-checked tracks the *resolved* dark/light state — for screen
      // readers that's what matters (is the page currently dark?), not
      // whether the user picked "system" abstractly.
      aria-checked={theme === "dark"}
      aria-label={label}
      title={label}
      onClick={() => setTheme(NEXT[theme])}
      className={className}
    >
      <Icon />
    </Button>
  );
}
