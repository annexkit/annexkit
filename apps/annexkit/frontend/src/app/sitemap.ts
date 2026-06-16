import type { MetadataRoute } from "next";

/**
 * Sitemap for search engines.
 *
 * Only public marketing + legal pages are listed. Trust pages
 * (`/trust/[slug]`) are deliberately excluded because:
 *
 *   1. The slug namespace is private-but-public — enumerating tenants
 *      via the sitemap would defeat the point of an opt-in trust
 *      surface.
 *   2. The pages render real-time data; a Google cache is misleading.
 *
 * `robots.ts` keeps `/trust/*` `disallow`-ed in parallel so the two
 * agree.
 *
 * `priority` is advisory; Google has said for years it ignores the
 * field, but other crawlers still read it. Homepage = 1.0, pricing =
 * 0.9, legal = 0.5.
 */

const SITE_ORIGIN =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://annexkit.dev";

interface Entry {
  path: string;
  changeFreq: MetadataRoute.Sitemap[number]["changeFrequency"];
  priority: number;
}

const ENTRIES: Entry[] = [
  { path: "/", changeFreq: "weekly", priority: 1.0 },
  { path: "/pricing", changeFreq: "monthly", priority: 0.9 },

  // Free tools — top organic-search target. The hub gets a high priority;
  // the two children sit below it (still in the sitemap so they can be
  // crawled directly, not just via the hub).
  { path: "/tools", changeFreq: "monthly", priority: 0.8 },
  { path: "/tools/annex-iv-generator", changeFreq: "monthly", priority: 0.7 },
  { path: "/tools/logging-schema", changeFreq: "monthly", priority: 0.7 },

  // Demo — entry point for skeptical buyers who want to see an artefact
  // before reading copy. Crawled at the same cadence as pricing.
  { path: "/demo/annex-iv", changeFreq: "monthly", priority: 0.7 },

  { path: "/privacy", changeFreq: "yearly", priority: 0.4 },
  { path: "/terms", changeFreq: "yearly", priority: 0.4 },
  { path: "/cookies", changeFreq: "yearly", priority: 0.3 },
  { path: "/imprint", changeFreq: "yearly", priority: 0.3 },
];

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  return ENTRIES.map((entry) => ({
    url: `${SITE_ORIGIN}${entry.path}`,
    lastModified: now,
    changeFrequency: entry.changeFreq,
    priority: entry.priority,
  }));
}
