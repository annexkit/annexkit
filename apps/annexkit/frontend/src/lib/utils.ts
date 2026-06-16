import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind class names with conflict resolution.
 *
 * `clsx` joins truthy values; `tailwind-merge` then collapses conflicting
 * Tailwind utilities (e.g. `px-2 px-4` → `px-4`) so authors can layer
 * variants without worrying about ordering.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
