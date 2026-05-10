import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { ChevronRight } from "lucide-react";

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
    <div className="mx-auto max-w-4xl px-6 py-14">
      <div className="space-y-12">
        <header className="space-y-4">
          <span className="eyebrow">AnnexKit trust page</span>
          <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            {overview.tenant.name}
          </h1>
          <p className="text-sm text-muted-foreground">
            Slug: <code className="inline-code">{overview.tenant.slug}</code>{" "}
            · As of{" "}
            <time dateTime={overview.as_of}>
              {formatDateTime(overview.as_of)}
            </time>
          </p>
        </header>

        <section className="surface-card p-6">
          <div className="flex flex-wrap items-baseline justify-between gap-4">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                Total declared AI systems
              </div>
              <div className="display-num mt-1 text-4xl font-bold text-foreground">
                {overview.total_systems}
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              {TIER_ORDER.filter((t) => overview.by_tier[t] > 0).map((t) => (
                <span key={t} className="flex items-center gap-2">
                  <RiskBadge tier={t} size="sm" />
                  <span className="text-sm font-semibold text-foreground">
                    ×{overview.by_tier[t]}
                  </span>
                </span>
              ))}
            </div>
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">
            Declared AI systems
          </h2>
          {list.systems.length === 0 ? (
            <p className="text-muted-foreground">
              No AI systems declared yet for this tenant.
            </p>
          ) : (
            <ul className="space-y-3">
              {list.systems.map((s) => (
                <li key={s.system_id}>
                  <Link
                    href={`/trust/${overview.tenant.slug}/systems/${encodeURIComponent(s.system_id)}`}
                    className="surface-card surface-hoverable group block p-5"
                  >
                    <div className="flex flex-wrap items-baseline justify-between gap-3">
                      <div className="flex items-center gap-2 font-mono text-sm text-foreground">
                        <span>{s.system_id}</span>
                        <ChevronRight className="size-3.5 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
                      </div>
                      <RiskBadge tier={s.risk_tier} size="sm" />
                    </div>
                    {s.purpose && (
                      <p className="mt-2 text-sm text-muted-foreground">
                        {s.purpose}
                      </p>
                    )}
                    <div className="mt-3 flex flex-wrap gap-2 text-xs">
                      {s.is_gpai && (
                        <span className="rounded-md bg-secondary px-2 py-0.5 font-medium text-foreground/80">
                          GPAI
                        </span>
                      )}
                      {s.annex_iii_categories.map((c) => (
                        <span
                          key={c}
                          className="rounded-md bg-secondary px-2 py-0.5 font-medium text-foreground/80"
                        >
                          Annex III: {c}
                        </span>
                      ))}
                      {s.transparency_triggers.map((c) => (
                        <span
                          key={c}
                          className="rounded-md bg-secondary px-2 py-0.5 font-medium text-foreground/80"
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
    </div>
  );
}
