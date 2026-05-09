import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";

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
    <div className="border-b border-neutral-100 py-2 text-sm">
      <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">
        {label}
      </div>
      <div className="mt-0.5 text-neutral-900">
        {value ? (
          value
        ) : (
          <span className="italic text-neutral-400">not declared</span>
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
    <div className="space-y-10">
      <nav className="text-sm">
        <Link
          href={`/trust/${tenant.slug}`}
          className="text-blue-700 hover:underline"
        >
          ← Back to {tenant.name}
        </Link>
      </nav>

      <header className="space-y-4">
        <div className="text-sm uppercase tracking-widest text-neutral-500">
          {tenant.name} · AI system declaration
        </div>
        <h1 className="font-mono text-3xl font-bold tracking-tight text-neutral-900">
          {system.system_id}
        </h1>
        <div className="flex flex-wrap items-center gap-3">
          <RiskBadge tier={system.risk_tier} size="lg" bilingual />
          {system.is_gpai && (
            <span className="rounded bg-neutral-100 px-3 py-1 text-sm font-medium text-neutral-700">
              GPAI
            </span>
          )}
          <span className="text-sm text-neutral-500">
            Rules version {system.rules_version}
          </span>
        </div>
        {system.purpose && (
          <p className="max-w-3xl text-lg text-neutral-700">
            {system.purpose}
          </p>
        )}
      </header>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold text-neutral-900">
          Risk classification
        </h2>
        {system.reasoning.length === 0 ? (
          <p className="text-neutral-500">
            No prohibited practices, high-risk Annex III categories, or
            Article 50 transparency triggers were declared. The system is
            classified as <strong>minimal</strong> under the rules engine.
          </p>
        ) : (
          <table className="w-full border-collapse rounded border border-neutral-200 bg-white text-sm">
            <thead>
              <tr className="border-b border-neutral-200 bg-neutral-50 text-left">
                <th className="p-3 font-medium">Rule ID</th>
                <th className="p-3 font-medium">Type</th>
                <th className="p-3 font-medium">Article</th>
                <th className="p-3 font-medium">Description (EN)</th>
                <th className="p-3 font-medium">Descrizione (IT)</th>
              </tr>
            </thead>
            <tbody>
              {system.reasoning.map((r) => (
                <tr key={r.rule_id} className="border-b border-neutral-100">
                  <td className="p-3 font-mono text-xs">{r.rule_id}</td>
                  <td className="p-3">{r.rule_type}</td>
                  <td className="p-3">{r.article}</td>
                  <td className="p-3">{r.name_en}</td>
                  <td className="p-3">{r.name_it}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded border border-neutral-200 bg-white p-6">
          <h2 className="mb-3 text-xl font-semibold text-neutral-900">
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
          <Field label="Software environment" value={pi.software_environment} />
          <Field label="Hardware environment" value={pi.hardware_environment} />
          <p className="mt-3 text-xs text-neutral-500">
            Sensitive provider fields (contact email, validation methods,
            internal notes) are intentionally not exposed on this public
            page.
          </p>
        </div>

        <div className="rounded border border-neutral-200 bg-white p-6">
          <h2 className="mb-3 text-xl font-semibold text-neutral-900">
            Categories &amp; triggers
          </h2>
          {system.annex_iii_categories.length > 0 && (
            <div className="mb-4">
              <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                Annex III — high-risk categories
              </div>
              <ul className="mt-2 space-y-1 text-sm">
                {system.annex_iii_categories.map((c) => (
                  <li key={c} className="font-mono text-neutral-900">
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {system.prohibited_practices.length > 0 && (
            <div className="mb-4">
              <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                Article 5 — prohibited practices
              </div>
              <ul className="mt-2 space-y-1 text-sm">
                {system.prohibited_practices.map((c) => (
                  <li key={c} className="font-mono text-neutral-900">
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {system.transparency_triggers.length > 0 && (
            <div className="mb-4">
              <div className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                Article 50 — transparency triggers
              </div>
              <ul className="mt-2 space-y-1 text-sm">
                {system.transparency_triggers.map((c) => (
                  <li key={c} className="font-mono text-neutral-900">
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {system.annex_iii_categories.length === 0 &&
            system.prohibited_practices.length === 0 &&
            system.transparency_triggers.length === 0 && (
              <p className="text-sm text-neutral-500">
                No categories or triggers declared.
              </p>
            )}
        </div>
      </section>

      <section className="rounded border border-neutral-200 bg-white p-6 text-sm text-neutral-700">
        <h2 className="mb-3 text-xl font-semibold text-neutral-900">
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
  );
}
