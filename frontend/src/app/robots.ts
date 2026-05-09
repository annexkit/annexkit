import type { MetadataRoute } from "next";

/**
 * Search-engine policy for the trust center.
 *
 * Trust pages are public by design — that's the point of having a
 * shareable URL — but we don't actively want bots crawling them
 * because:
 *
 *   1. The pages render real-time data; a stale Google cache would
 *      mislead anyone making a procurement decision off it.
 *   2. The slug namespace is private-but-public (nothing enumerates
 *      tenants); aggressive crawling could measure the namespace.
 *
 * Solution: ``noindex`` for /trust/* (humans with a link still see
 * it; bots stay away). The landing page at / is fine to index.
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
    // Sitemap intentionally omitted — we don't enumerate tenants.
  };
}
