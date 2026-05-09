import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";

import { BackendUnavailable } from "@/components/BackendUnavailable";
import { Disclaimer } from "@/components/Disclaimer";
import { RiskBadge } from "@/components/RiskBadge";
import { formatDateTime } from "@/lib/format";
import {
  BackendUnavailableError,
  trustApi,
  type RiskTier,
} from "@/lib/api";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params;
  try {
    const overview = await trustApi.overview(slug);
    if (!overview) return { title: "Trust page not found" };
    const { tenant, total_systems, by_tier } = overview;
    const tierSummary = (
      ["unacceptable", "high", "limited", "minimal", "auto"] as RiskTier[]
    )
      .filter((t) => by_tier[t] > 0)
      .map((t) => `${by_tier[t]} ${t}`)
      .join(", ");
    const description = `${tenant.name} has declared ${total_systems} AI system(s) under the EU AI Act via AnnexKit${tierSummary ? ` (${tierSummary})` : ""}.`;
    return {
      title: `${tenant.name} — Trust page`,
      description,
      openGraph: {
        title: `${tenant.name} — AnnexKit trust page`,
        description,
        type: "website",
      },
      twitter: {
        card: "summary",
        title: `${tenant.name} — AnnexKit trust page`,
        description,
      },
    };
  } catch {
    return { title: "Trust page" };
  }
}

const TIER_ORDER: RiskTier[] = [
  "unacceptable",
  "high",
  "limited",
  "minimal",
  "auto",
];

export default async function TrustOverviewPage({ params }: PageProps) {
  const { slug } = await params;

  let overview, list;
  try {
    [overview, list] = await Promise.all([
      trustApi.overview(slug),
      trustApi.listSystems(slug),
    ]);
  } catch (err) {
    if (err instanceof BackendUnavailableError) {
      return <BackendUnavailable />;
    }
    throw err;
  }
  if (!overview || !list) {
    notFound();
  }

  return (
    <div className="space-y-10">
      <header className="space-y-3">
        <div className="text-sm uppercase tracking-widest text-neutral-500">
          AnnexKit trust page
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-neutral-900">
          {overview.tenant.name}
        </h1>
        <p className="text-sm text-neutral-500">
          Slug:{" "}
          <code className="rounded bg-neutral-100 px-1 py-0.5">
            {overview.tenant.slug}
          </code>{" "}
          · As of{" "}
          <time dateTime={overview.as_of}>
            {formatDateTime(overview.as_of)}
          </time>
        </p>
      </header>

      <section className="rounded border border-neutral-200 bg-white p-6">
        <div className="flex flex-wrap items-baseline justify-between gap-4">
          <div>
            <div className="text-sm text-neutral-500">
              Total declared AI systems
            </div>
            <div className="text-3xl font-semibold text-neutral-900">
              {overview.total_systems}
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {TIER_ORDER.filter((t) => overview.by_tier[t] > 0).map((t) => (
              <span key={t} className="flex items-center gap-2">
                <RiskBadge tier={t} size="sm" />
                <span className="text-sm font-semibold text-neutral-900">
                  ×{overview.by_tier[t]}
                </span>
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-neutral-900">
          Declared AI systems
        </h2>
        {list.systems.length === 0 ? (
          <p className="text-neutral-500">
            No AI systems declared yet for this tenant.
          </p>
        ) : (
          <ul className="space-y-3">
            {list.systems.map((s) => (
              <li
                key={s.system_id}
                className="rounded border border-neutral-200 bg-white p-5 hover:border-neutral-400"
              >
                <Link
                  href={`/trust/${overview.tenant.slug}/systems/${encodeURIComponent(s.system_id)}`}
                  className="block"
                >
                  <div className="flex flex-wrap items-baseline justify-between gap-3">
                    <div className="font-mono text-sm text-neutral-900">
                      {s.system_id}
                    </div>
                    <RiskBadge tier={s.risk_tier} size="sm" />
                  </div>
                  {s.purpose && (
                    <p className="mt-2 text-sm text-neutral-700">
                      {s.purpose}
                    </p>
                  )}
                  <div className="mt-3 flex flex-wrap gap-2 text-xs text-neutral-500">
                    {s.is_gpai && (
                      <span className="rounded bg-neutral-100 px-2 py-0.5">
                        GPAI
                      </span>
                    )}
                    {s.annex_iii_categories.map((c) => (
                      <span
                        key={c}
                        className="rounded bg-neutral-100 px-2 py-0.5"
                      >
                        Annex III: {c}
                      </span>
                    ))}
                    {s.transparency_triggers.map((c) => (
                      <span
                        key={c}
                        className="rounded bg-neutral-100 px-2 py-0.5"
                      >
                        Article 50: {c}
                      </span>
                    ))}
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <Disclaimer />
    </div>
  );
}
