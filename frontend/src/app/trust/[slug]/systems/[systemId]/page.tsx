import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { ArrowLeft } from "lucide-react";

import { BackendUnavailable } from "@/components/BackendUnavailable";
import { Disclaimer } from "@/components/Disclaimer";
import { RiskBadge } from "@/components/RiskBadge";
import { formatDateTime } from "@/lib/format";
import { BackendUnavailableError, trustApi } from "@/lib/api";

interface PageProps {
  params: Promise<{ slug: string; systemId: string }>;
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug, systemId } = await params;
  try {
    const detail = await trustApi.getSystem(slug, systemId);
    if (!detail) return { title: "AI system not found" };
    const { tenant, system } = detail;
    const description =
      system.purpose ??
      `Declared AI system ${system.system_id} for ${tenant.name}.`;
    const title = `${system.system_id} — ${tenant.name}`;
    return {
      title,
      description,
      openGraph: {
        title: `${title} (${system.risk_tier} risk)`,
        description,
        type: "article",
      },
      twitter: {
        card: "summary",
        title: `${title} (${system.risk_tier} risk)`,
        description,
      },
    };
  } catch {
    return { title: "AI system" };
  }
}

interface FieldProps {
  label: string;
  value: string | null | undefined;
}

function Field({ label, value }: FieldProps) {
  return (
    <div className="border-b border-border/50 py-2.5 text-sm last:border-b-0">
      <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
        {label}
      </div>
      <div className="mt-0.5 text-foreground">
        {value ? (
          value
        ) : (
          <span className="italic text-muted-foreground/60">
            not declared
          </span>
        )}
      </div>
    </div>
  );
}

export default async function SystemDetailPage({ params }: PageProps) {
  const { slug, systemId } = await params;

  let detail;
  try {
    detail = await trustApi.getSystem(slug, systemId);
  } catch (err) {
    if (err instanceof BackendUnavailableError) {
      return <BackendUnavailable />;
    }
    throw err;
  }
  if (!detail) notFound();

  const { tenant, system } = detail;
  const pi = system.provider_info;

  return (
    <div className="mx-auto max-w-5xl px-6 py-14">
      <div className="space-y-12">
        <nav className="text-sm">
          <Link
            href={`/trust/${tenant.slug}`}
            className="inline-flex items-center gap-1.5 text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="size-4" />
            Back to {tenant.name}
          </Link>
        </nav>

        <header className="space-y-4">
          <span className="eyebrow">
            {tenant.name} · AI system declaration
          </span>
          <h1 className="font-mono text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            {system.system_id}
          </h1>
          <div className="flex flex-wrap items-center gap-3">
            <RiskBadge tier={system.risk_tier} size="lg" bilingual />
            {system.is_gpai && (
              <span className="rounded-md bg-secondary px-3 py-1 text-sm font-medium text-foreground">
                GPAI
              </span>
            )}
            <span className="text-sm text-muted-foreground">
              Rules version {system.rules_version}
            </span>
          </div>
          {system.purpose && (
            <p className="max-w-3xl text-lg text-muted-foreground">
              {system.purpose}
            </p>
          )}
        </header>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">
            Risk classification
          </h2>
          {system.reasoning.length === 0 ? (
            <p className="text-muted-foreground">
              No prohibited practices, high-risk Annex III categories, or
              Article 50 transparency triggers were declared. The system
              is classified as{" "}
              <strong className="text-foreground">minimal</strong> under
              the rules engine.
            </p>
          ) : (
            <div className="surface-card overflow-x-auto">
              <table className="w-full min-w-[720px] border-collapse text-sm">
                <thead>
                  <tr className="border-b border-border/60 bg-secondary/40 text-left text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                    <th className="p-4">Rule ID</th>
                    <th className="p-4">Type</th>
                    <th className="p-4">Article</th>
                    <th className="p-4">Description (EN)</th>
                    <th className="p-4">Descrizione (IT)</th>
                  </tr>
                </thead>
                <tbody>
                  {system.reasoning.map((r) => (
                    <tr
                      key={r.rule_id}
                      className="border-b border-border/40 last:border-b-0 align-top"
                    >
                      <td className="p-4 font-mono text-xs text-foreground">
                        {r.rule_id}
                      </td>
                      <td className="p-4 text-foreground">{r.rule_type}</td>
                      <td className="p-4 text-foreground">{r.article}</td>
                      <td className="p-4 text-muted-foreground">
                        {r.name_en}
                      </td>
                      <td className="p-4 text-muted-foreground">
                        {r.name_it}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="grid gap-5 md:grid-cols-2">
          <div className="surface-card p-6">
            <h2 className="mb-4 text-xl font-semibold tracking-tight text-foreground">
              Provider information
            </h2>
            <Field label="Legal name" value={pi.legal_name} />
            <Field label="Registered address" value={pi.address} />
            <Field label="Country (ISO)" value={pi.country} />
            <Field
              label="Authorised representative"
              value={pi.authorised_representative}
            />
            <Field label="System version" value={pi.system_version} />
            <Field
              label="Software environment"
              value={pi.software_environment}
            />
            <Field
              label="Hardware environment"
              value={pi.hardware_environment}
            />
            <p className="mt-4 text-xs text-muted-foreground">
              Sensitive provider fields (contact email, validation
              methods, internal notes) are intentionally not exposed on
              this public page.
            </p>
          </div>

          <div className="surface-card p-6">
            <h2 className="mb-4 text-xl font-semibold tracking-tight text-foreground">
              Categories &amp; triggers
            </h2>
            {system.annex_iii_categories.length > 0 && (
              <CategoryGroup
                title="Annex III — high-risk categories"
                items={system.annex_iii_categories}
              />
            )}
            {system.prohibited_practices.length > 0 && (
              <CategoryGroup
                title="Article 5 — prohibited practices"
                items={system.prohibited_practices}
              />
            )}
            {system.transparency_triggers.length > 0 && (
              <CategoryGroup
                title="Article 50 — transparency triggers"
                items={system.transparency_triggers}
              />
            )}
            {system.annex_iii_categories.length === 0 &&
              system.prohibited_practices.length === 0 &&
              system.transparency_triggers.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No categories or triggers declared.
                </p>
              )}
          </div>
        </section>

        <section className="surface-card p-6">
          <h2 className="mb-4 text-xl font-semibold tracking-tight text-foreground">
            Lifecycle
          </h2>
          <Field
            label="First declared"
            value={formatDateTime(system.created_at)}
          />
          <Field
            label="Last reclassification"
            value={formatDateTime(system.classified_at)}
          />
          <Field
            label="Last update"
            value={formatDateTime(system.updated_at)}
          />
        </section>

        <Disclaimer />
      </div>
    </div>
  );
}

function CategoryGroup({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <div className="mb-5 last:mb-0">
      <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
        {title}
      </div>
      <ul className="mt-2 space-y-1 text-sm">
        {items.map((c) => (
          <li key={c} className="font-mono text-foreground">
            {c}
          </li>
        ))}
      </ul>
    </div>
  );
}
