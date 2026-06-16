"use client";

/**
 * Interactive form for /tools/annex-iv-generator.
 *
 * Single-page form (NOT multi-step — fewer clicks, less state, friendly
 * for sharing as a single deep-link). Sections collapse-on-demand so
 * the page doesn't overwhelm on first paint.
 *
 * On submit:
 *   1. POST to /api/v1/tools/annex-iv-generator with the full payload.
 *   2. On 200: the response body IS the PDF. Read as blob and trigger
 *      a download via a synthesised <a download>; the X-Risk-Tier
 *      header is surfaced in the success message.
 *   3. On 422: validation error (bad email or unknown rule id) —
 *      shown inline.
 *   4. On 429: rate-limit hit — shown as "try again in an hour".
 *   5. On anything else: generic "try again" message.
 *
 * No state library — `useState` is enough for ~10 fields. No form
 * library — native HTML form with controlled inputs is sufficient
 * for the form complexity here.
 */

import { useState, type ChangeEvent, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { CLIENT_API_URL } from "@/lib/api";
import { cn } from "@/lib/utils";

/* eslint-disable @typescript-eslint/no-explicit-any */

// ---- Types mirroring backend annex_iii.json shape ------------------------

export interface AnnexUseCase {
  id: string;
  question_it: string;
}

export interface AnnexCategory {
  id: string;
  annex_ref: string;
  name_it: string;
  name_en: string;
  description_it: string;
  use_cases: AnnexUseCase[];
}

export interface AnnexRule {
  id: string;
  article: string;
  name_it: string;
  name_en: string;
  description_it: string;
  question_it: string;
}

export interface AnnexRules {
  version: string;
  regulation: string;
  high_risk_categories: AnnexCategory[];
  prohibited_practices: AnnexRule[];
  transparency_triggers: AnnexRule[];
  gpai: AnnexRule;
}

// ---- Form state -----------------------------------------------------------

interface ProviderInfoState {
  legal_name: string;
  address: string;
  country: string;
  contact_email: string;
  system_version: string;
  software_environment: string;
  hardware_environment: string;
  validation_methods: string;
  notes: string;
}

interface FormState {
  purpose: string;
  annex_iii: Set<string>;
  prohibited: Set<string>;
  transparency: Set<string>;
  is_gpai: boolean;
  provider: ProviderInfoState;
  email: string;
}

const EMPTY_PROVIDER: ProviderInfoState = {
  legal_name: "",
  address: "",
  country: "",
  contact_email: "",
  system_version: "",
  software_environment: "",
  hardware_environment: "",
  validation_methods: "",
  notes: "",
};

const INITIAL_STATE: FormState = {
  purpose: "",
  annex_iii: new Set(),
  prohibited: new Set(),
  transparency: new Set(),
  is_gpai: false,
  provider: { ...EMPTY_PROVIDER },
  email: "",
};

// ---- Success/error UI ----------------------------------------------------

interface ResultState {
  type: "success" | "error";
  tier?: string;
  message: string;
}

const TIER_COLORS: Record<string, string> = {
  unacceptable: "bg-red-500 text-white",
  high: "bg-orange-500 text-white",
  limited: "bg-amber-400 text-black",
  minimal: "bg-emerald-500 text-white",
};

// ---- Component -----------------------------------------------------------

export function GeneratorForm({ rules }: { rules: AnnexRules }) {
  const [state, setState] = useState<FormState>(INITIAL_STATE);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<ResultState | null>(null);

  function toggleSet(field: "annex_iii" | "prohibited" | "transparency", id: string) {
    setState((prev) => {
      const next = new Set(prev[field]);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return { ...prev, [field]: next };
    });
  }

  function setProvider<K extends keyof ProviderInfoState>(key: K, value: string) {
    setState((prev) => ({
      ...prev,
      provider: { ...prev.provider, [key]: value },
    }));
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    setResult(null);

    const provider: Record<string, string> = {};
    for (const [k, v] of Object.entries(state.provider)) {
      if (v.trim()) provider[k] = v.trim();
    }

    const payload = {
      purpose: state.purpose.trim(),
      annex_iii_categories: Array.from(state.annex_iii),
      prohibited_practices: Array.from(state.prohibited),
      transparency_triggers: Array.from(state.transparency),
      is_gpai: state.is_gpai,
      provider_info: provider,
      email: state.email.trim(),
    };

    try {
      const res = await fetch(`${CLIENT_API_URL}/api/v1/tools/annex-iv-generator`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.status === 429) {
        setResult({
          type: "error",
          message:
            "Rate limit reached (10 generations per hour per IP). " +
            "Try again in an hour, or sign up for an AnnexKit account for higher limits.",
        });
        return;
      }
      if (res.status === 422) {
        const body = (await res.json().catch(() => ({}))) as Record<string, any>;
        const detail = body.detail ?? body.error ?? JSON.stringify(body);
        setResult({
          type: "error",
          message: `Validation error: ${detail}`,
        });
        return;
      }
      if (!res.ok) {
        setResult({
          type: "error",
          message: `Server returned HTTP ${res.status}. Please try again.`,
        });
        return;
      }

      const tier = res.headers.get("X-Risk-Tier") ?? "unknown";
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `annex-iv-${tier}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      setResult({
        type: "success",
        tier,
        message: `PDF generated and downloaded. Risk tier: ${tier.toUpperCase()}.`,
      });
    } catch (err) {
      setResult({
        type: "error",
        message:
          "Network failure reaching the generator endpoint. Check your connection and try again.",
      });
    } finally {
      setSubmitting(false);
    }
  }

  // Granular validation so we can tell the user WHICH field is short.
  const purposeShort = state.purpose.trim().length < 20;
  const emailEmpty = state.email.trim().length === 0;
  const canSubmit = !purposeShort && !emailEmpty && !submitting;

  const submitHint: string | null = (() => {
    if (purposeShort && emailEmpty) {
      return `Add a purpose (need ${20 - state.purpose.trim().length} more chars) and your email to generate.`;
    }
    if (purposeShort) {
      return `Purpose needs ${20 - state.purpose.trim().length} more characters before you can generate.`;
    }
    if (emailEmpty) {
      return "Add your email at the bottom to generate the PDF.";
    }
    return null;
  })();

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* --- 1. Purpose --- */}
      <Section
        title="1. What does the system do?"
        subtitle="Free-form description. Renders as Annex IV §1.1 'Intended purpose'. Min 20 characters."
      >
        <textarea
          required
          minLength={20}
          maxLength={1000}
          rows={4}
          value={state.purpose}
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
            setState({ ...state, purpose: e.target.value })
          }
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--brand-accent)]"
          placeholder="e.g. CV screening AI for HR. Filters incoming candidates against role criteria, produces a ranked shortlist for human recruiters."
        />
        <p className="mt-1 text-xs text-muted-foreground">
          {state.purpose.length} / 1000 characters
        </p>
      </Section>

      {/* --- 2. Annex III high-risk categories --- */}
      <Section
        title="2. Annex III high-risk categories"
        subtitle="Pick any that apply. Triggering any one of these classifies the system as HIGH-risk."
      >
        <div className="space-y-3">
          {rules.high_risk_categories.map((c) => (
            <CheckRow
              key={c.id}
              id={c.id}
              checked={state.annex_iii.has(c.id)}
              onToggle={() => toggleSet("annex_iii", c.id)}
              title={`${c.name_en} (${c.annex_ref})`}
              subtitle={c.description_it}
            />
          ))}
        </div>
      </Section>

      {/* --- 3. Article 5 prohibited --- */}
      <Section
        title="3. Article 5 prohibited practices"
        subtitle="Triggering any one of these makes the system UNACCEPTABLE — banned under the AI Act."
        warningIf={state.prohibited.size > 0}
      >
        <div className="space-y-3">
          {rules.prohibited_practices.map((r) => (
            <CheckRow
              key={r.id}
              id={r.id}
              checked={state.prohibited.has(r.id)}
              onToggle={() => toggleSet("prohibited", r.id)}
              title={`${r.name_en} (${r.article})`}
              subtitle={r.description_it}
            />
          ))}
        </div>
      </Section>

      {/* --- 4. Article 50 transparency --- */}
      <Section
        title="4. Article 50 transparency triggers"
        subtitle="Apply user-facing disclosure obligations even when the system isn't high-risk."
      >
        <div className="space-y-3">
          {rules.transparency_triggers.map((r) => (
            <CheckRow
              key={r.id}
              id={r.id}
              checked={state.transparency.has(r.id)}
              onToggle={() => toggleSet("transparency", r.id)}
              title={`${r.name_en} (${r.article})`}
              subtitle={r.description_it}
            />
          ))}
        </div>
      </Section>

      {/* --- 5. GPAI --- */}
      <Section
        title="5. General-purpose AI"
        subtitle={rules.gpai.description_it}
      >
        <CheckRow
          id="gpai"
          checked={state.is_gpai}
          onToggle={() => setState({ ...state, is_gpai: !state.is_gpai })}
          title="This system is built on a GPAI model (LLM, large multimodal model)."
          subtitle={rules.gpai.article}
        />
      </Section>

      {/* --- 6. Provider info --- */}
      <Section
        title="6. Provider information (Annex IV §1)"
        subtitle="All fields optional, but each missing field shows as 'Provider input required' in the PDF gap analysis."
      >
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <TextInput
            label="Legal entity name"
            value={state.provider.legal_name}
            onChange={(v) => setProvider("legal_name", v)}
            placeholder="Velmara S.r.l."
          />
          <TextInput
            label="Country (ISO 2)"
            value={state.provider.country}
            onChange={(v) => setProvider("country", v)}
            placeholder="IT"
            maxLength={2}
          />
          <TextInput
            label="Registered address"
            value={state.provider.address}
            onChange={(v) => setProvider("address", v)}
            placeholder="Via Manzoni 1, 20121 Milano (MI), Italia"
            className="sm:col-span-2"
          />
          <TextInput
            label="Compliance contact email"
            value={state.provider.contact_email}
            onChange={(v) => setProvider("contact_email", v)}
            placeholder="compliance@velmara.example"
            type="email"
          />
          <TextInput
            label="System version"
            value={state.provider.system_version}
            onChange={(v) => setProvider("system_version", v)}
            placeholder="v1.0.0"
          />
          <TextInput
            label="Software environment"
            value={state.provider.software_environment}
            onChange={(v) => setProvider("software_environment", v)}
            placeholder="Python 3.13, FastAPI, OpenAI gpt-4o-mini"
            className="sm:col-span-2"
          />
        </div>
      </Section>

      {/* --- 7. Email --- */}
      <Section
        title="7. Your email"
        subtitle="Required. We use it to follow up — the PDF itself is generated in memory and not persisted on our servers."
      >
        <input
          required
          type="email"
          value={state.email}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setState({ ...state, email: e.target.value })
          }
          placeholder="founder@your-company.example"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--brand-accent)]"
        />
      </Section>

      {/* --- Submit + result --- */}
      <div className="space-y-4 border-t border-border pt-8">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <Button type="submit" disabled={!canSubmit} className="w-full sm:w-auto">
            {submitting ? "Generating PDF…" : "Generate Annex IV PDF"}
          </Button>
          {submitHint && (
            <span className="text-sm text-amber-600 dark:text-amber-400">
              {submitHint}
            </span>
          )}
        </div>

        {result && (
          <div
            className={cn(
              "rounded-md border p-4 text-sm",
              result.type === "success"
                ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
                : "border-red-500/50 bg-red-500/10 text-red-700 dark:text-red-300",
            )}
          >
            {result.type === "success" && result.tier && (
              <span
                className={cn(
                  "mb-2 inline-block rounded px-2 py-0.5 text-xs font-semibold uppercase",
                  TIER_COLORS[result.tier] ?? "bg-muted",
                )}
              >
                {result.tier}
              </span>
            )}
            <p>{result.message}</p>
          </div>
        )}
      </div>
    </form>
  );
}

// ---- Small helpers -------------------------------------------------------

function Section({
  title,
  subtitle,
  children,
  warningIf,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  warningIf?: boolean;
}) {
  return (
    <section
      className={cn(
        "rounded-lg border p-6",
        warningIf
          ? "border-red-500/50 bg-red-500/5"
          : "border-border bg-card",
      )}
    >
      <h2 className="mb-1 text-lg font-semibold text-foreground">{title}</h2>
      {subtitle && (
        <p className="mb-4 text-sm text-muted-foreground">{subtitle}</p>
      )}
      {children}
    </section>
  );
}

function CheckRow({
  id,
  checked,
  onToggle,
  title,
  subtitle,
}: {
  id: string;
  checked: boolean;
  onToggle: () => void;
  title: string;
  subtitle?: string;
}) {
  return (
    <label
      htmlFor={id}
      className={cn(
        "flex cursor-pointer items-start gap-3 rounded-md border p-3 transition-colors",
        checked
          ? "border-[var(--brand-accent)] bg-[var(--brand-accent)]/5"
          : "border-input hover:border-muted-foreground",
      )}
    >
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={onToggle}
        className="mt-1 h-4 w-4 cursor-pointer"
      />
      <div className="flex-1">
        <div className="text-sm font-medium text-foreground">{title}</div>
        {subtitle && (
          <div className="mt-1 text-xs text-muted-foreground">{subtitle}</div>
        )}
      </div>
    </label>
  );
}

function TextInput({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  maxLength,
  className,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  maxLength?: number;
  className?: string;
}) {
  return (
    <div className={className}>
      <label className="mb-1 block text-xs font-medium text-foreground">
        {label}
      </label>
      <input
        type={type}
        value={value}
        maxLength={maxLength}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--brand-accent)]"
      />
    </div>
  );
}
