import type { MetadataRoute } from "next";

const SITE_ORIGIN =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://annexkit.dev";

/**
 * Search-engine policy.
 *
 * Trust pages are public-by-link but `noindex`: bots stay out, humans
 * with the URL still load them. Marketing + legal pages index normally
 * and are listed in `sitemap.ts`.
 *
 * Why we don't sitemap `/trust/*`:
 *
 *   1. The pages render real-time data; a stale Google cache would
 *      mislead anyone making a procurement decision off it.
 *   2. Listing tenants in a sitemap would defeat the privacy-by-default
 *      intent of the slug namespace.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/trust/"],
      },
    ],
    sitemap: `${SITE_ORIGIN}/sitemap.xml`,
    host: SITE_ORIGIN,
  };
}
