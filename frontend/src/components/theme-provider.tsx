/**
 * Client-side theme provider. Three user-facing modes: "light", "dark",
 * and "system" — where "system" follows the OS `prefers-color-scheme`.
 *
 * Default on first visit
 * ----------------------
 * "system". AnnexKit's marketing surface is designed dark-first (it's a
 * developer tool, not a B2B SaaS marketing site), so following the OS
 * preference produces the right first impression for the typical visitor
 * (engineers run their machines dark) without forcing it on the minority
 * who keep light.
 *
 * How the look actually changes
 * -----------------------------
 * `globals.css` ships two full palettes: `:root` (light) and `.dark`.
 * Switching themes means toggling the `dark` class on `<html>` — this
 * file owns that responsibility.
 *
 * Resolved vs. preference
 * -----------------------
 *   - `theme`         — what the user picked: "light" | "dark" | "system"
 *   - `resolvedTheme` — what's actually applied: "light" | "dark"
 * For "system", `resolvedTheme` tracks `prefers-color-scheme` live (we
 * subscribe to the media query so flipping OS appearance reflects
 * immediately, no reload needed).
 *
 * Why no dependency
 * -----------------
 * `next-themes` would do the same plus a few edge cases. React 19 +
 * `useSyncExternalStore` + localStorage covers everything we need with
 * fewer moving parts.
 *
 * Hydration safety
 * ----------------
 * The root layout ships a tiny inline `<script>` that reads localStorage
 * and applies the right class to `<html>` BEFORE React hydrates — so no
 * flash of wrong theme on reload. This provider subscribes to the same
 * store via `useSyncExternalStore` so server and first client render
 * agree.
 */

"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useSyncExternalStore,
  type ReactNode,
} from "react";

export type Theme = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

// Exported so the inline no-flash script in `layout.tsx` can reference
// the same storage key. Rename here → rename there, or the two stop
// agreeing and the flash returns.
export const THEME_STORAGE_KEY = "annexkit-theme";

interface ThemeContextValue {
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  setTheme: (next: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

// ---------------------------------------------------------------------------
// external store — localStorage  (null = user hasn't chosen → default system)
// ---------------------------------------------------------------------------

function readStoredTheme(): Theme | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(THEME_STORAGE_KEY);
  return raw === "light" || raw === "dark" || raw === "system" ? raw : null;
}

function subscribeStorage(onChange: () => void): () => void {
  if (typeof window === "undefined") return () => {};
  window.addEventListener("storage", onChange);
  return () => window.removeEventListener("storage", onChange);
}

// ---------------------------------------------------------------------------
// external store — `prefers-color-scheme` media query
// ---------------------------------------------------------------------------

function readSystemPrefersDark(): boolean {
  if (typeof window === "undefined" || !window.matchMedia) return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function subscribePrefers(onChange: () => void): () => void {
  if (typeof window === "undefined" || !window.matchMedia) return () => {};
  const mql = window.matchMedia("(prefers-color-scheme: dark)");
  mql.addEventListener("change", onChange);
  return () => mql.removeEventListener("change", onChange);
}

// ---------------------------------------------------------------------------
// provider
// ---------------------------------------------------------------------------

export function ThemeProvider({ children }: { children: ReactNode }) {
  const stored = useSyncExternalStore(
    subscribeStorage,
    readStoredTheme,
    () => null,
  );
  const systemPrefersDark = useSyncExternalStore(
    subscribePrefers,
    readSystemPrefersDark,
    // Server snapshot: bias to dark since AnnexKit is dark-canonical.
    // Worst case if the OS is actually light: one frame of dark before
    // the inline no-flash script flips to light. Acceptable.
    () => true,
  );

  // Explicit choice wins; otherwise default to "system".
  const theme: Theme = stored ?? "system";
  const resolvedTheme: ResolvedTheme =
    theme === "system" ? (systemPrefersDark ? "dark" : "light") : theme;

  // Keep <html class> in sync with the resolved theme. One-way sync from
  // React to the DOM — no setState in here.
  useEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.classList.toggle("dark", resolvedTheme === "dark");
  }, [resolvedTheme]);

  const setTheme = useCallback((next: Theme) => {
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch {
      // Private-mode Safari / disabled storage / quota full. Non-fatal:
      // the synthetic event below still flips this session.
    }
    // `localStorage.setItem` does NOT fire a `storage` event in the
    // same tab (cross-tab only). Dispatch a synthetic one so our own
    // `useSyncExternalStore` subscribers re-read the value.
    window.dispatchEvent(
      new StorageEvent("storage", {
        key: THEME_STORAGE_KEY,
        newValue: next,
        storageArea: window.localStorage,
      }),
    );
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

/** Hook for the toggle and anyone else that needs to know / change theme. */
export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used inside <ThemeProvider>");
  }
  return ctx;
}
