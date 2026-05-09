import type { Metadata } from "next";
import "./globals.css";

const PUBLIC_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://annexkit.dev";

export const metadata: Metadata = {
  metadataBase: new URL(PUBLIC_URL),
  title: {
    default: "AnnexKit — EU AI Act compliance pipeline",
    template: "%s — AnnexKit",
  },
  description:
    "EU AI Act compliance pipeline for developers. Public trust pages " +
    "for tenants who declare their AI systems via AnnexKit.",
  applicationName: "AnnexKit",
  keywords: [
    "EU AI Act",
    "Annex IV",
    "AI compliance",
    "AI Act trust center",
    "AI governance",
    "Reg. 2024/1689",
  ],
  authors: [{ name: "AnnexKit" }],
  openGraph: {
    type: "website",
    siteName: "AnnexKit",
    title: "AnnexKit — EU AI Act compliance pipeline",
    description:
      "Public trust pages for AI systems declared under the EU AI Act, " +
      "backed by deterministic risk classification and append-only audit logs.",
    locale: "en_GB",
  },
  twitter: {
    card: "summary",
    title: "AnnexKit — EU AI Act compliance pipeline",
    description:
      "Public trust pages for AI systems declared under the EU AI Act.",
  },
  robots: {
    // Per /robots.txt rules: index landing, leave /trust/* to humans
    // with the link.
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-neutral-200 bg-white">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
            <a
              href="/"
              className="text-lg font-semibold tracking-tight text-neutral-900"
            >
              AnnexKit
            </a>
            <nav className="text-sm text-neutral-500">
              <a
                className="hover:text-neutral-900"
                href="https://github.com/annexkit/annexkit"
              >
                GitHub
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
        <footer className="mx-auto max-w-5xl px-6 py-10 text-xs text-neutral-500">
          <p>
            AnnexKit is not a law firm / AnnexKit non è uno studio legale.
            Trust pages render technical declarations made by the named
            tenant; legal interpretation is the responsibility of the
            tenant&rsquo;s legal counsel.
          </p>
        </footer>
      </body>
    </html>
  );
}
