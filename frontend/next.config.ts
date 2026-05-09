import type { NextConfig } from "next";

/**
 * Next.js 16 — Turbopack is now the default bundler; no `experimental.turbo`
 * flag needed. The `middleware` lifecycle was renamed to `proxy` in v16
 * (we don't use it yet but it's worth knowing if you add one).
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Standalone output keeps the Docker image lean — only what next start
  // needs goes into the runtime container.
  output: "standalone",
  // No img domains needed yet; trust pages render no remote images.
  images: { remotePatterns: [] },
};

export default nextConfig;
