/**
 * How it works — three numbered steps + a compact "Under the hood" strip
 * with the four architectural invariants.
 *
 * The 3-step sequence is the developer's mental rehearsal: install →
 * decorate → fetch PDF. Each step shows the actual command/code so a
 * skim is enough to plan the integration.
 *
 * Under the strip: the four invariants that are wired into the data
 * layer (not toggles a PM can flip). This block replaces the standalone
 * <Architecture> section (the box-and-arrows diagram). Reasoning: the
 * diagram was visually heavy for two facts the buyer cares about (it's
 * deterministic, the audit log can't be tampered with). A pill-strip
 * carries those facts in 1/4 of the scroll.
 *
 * Anti-vapor notes (2026-05-24 sweep):
 *   - Step 3 dropped "Average 75 KB" — the byte-count was unverified
 *     marketing detail (ANTI_VAPOR B8). Replaced with "regulator-grade,
 *     bilingual EN / IT" which is verifiable.
 *   - Invariant 2 "Risk classifier" dropped "LLM advisors can suggest"
 *     — the advisor call-site doesn't exist in v0.1 (ANTI_VAPOR F3).
 */

import {
  FileCheck2,
  FileLock2,
  Gauge,
  Lock,
  Server,
  type LucideIcon,
} from "lucide-react";

export function HowItWorks() {
  return (
    <section className="border-b border-border/60 bg-secondary/30">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="max-w-2xl space-y-3">
          <span className="eyebrow">How it works</span>
          <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Three steps from <code className="inline-code">pip install</code>{" "}
            to a downloadable Annex IV PDF.
          </h2>
        </div>

        <ol className="mt-12 grid gap-6 lg:grid-cols-3">
          <Step
            n={1}
            title="Install the SDK"
            body="Python 3.10+. The track decorator emits a span on every wrapped LLM call."
            code={["pip install annexkit"]}
            language="shell"
          />
          <Step
            n={2}
            title="Decorate your inference"
            body="Set ANNEXKIT_API_KEY to ship spans to the collector. Without it, spans print on stderr — useful for local dev."
            code={[
              "@track(",
              "    system_id=\"loan-screener\",",
              "    purpose=\"pre-screen credit\",",
              ")",
              "def screen(applicant):",
              "    ...",
            ]}
            language="python"
          />
          <Step
            n={3}
            title="Pull the Annex IV PDF"
            body="On demand from the API or via your trust page. Bilingual EN / IT, regulator-grade per system."
            code={[
              "GET /api/v1/systems/",
              "    loan-screener/annex-iv",
              "    ?format=pdf",
            ]}
            language="http"
          />
        </ol>

        <UnderTheHood />
      </div>
    </section>
  );
}

interface StepProps {
  n: number;
  title: string;
  body: string;
  code: string[];
  language: string;
}

function Step({ n, title, body, code, language }: StepProps) {
  return (
    <li className="surface-card flex flex-col gap-5 p-6">
      <div className="flex items-center gap-3">
        <span className="display-num inline-flex size-9 items-center justify-center rounded-md bg-[var(--brand-cobalt)]/10 text-base font-semibold text-[var(--brand-cobalt)]">
          {n}
        </span>
        <h3 className="text-lg font-semibold tracking-tight text-foreground">
          {title}
        </h3>
      </div>
      <p className="text-sm text-muted-foreground">{body}</p>

      <pre className="mt-auto overflow-x-auto rounded-md border border-border/60 bg-background/60 p-4 font-mono text-xs leading-relaxed">
        <span className="mb-2 inline-block text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
          {language}
        </span>
        {"\n"}
        <code className="text-foreground">{code.join("\n")}</code>
      </pre>
    </li>
  );
}

/* ----------------------------------------------------------------------- */
/* Under the hood — 4 invariants that replace the old Architecture section */
/* ----------------------------------------------------------------------- */

interface InvariantProps {
  icon: LucideIcon;
  art: string;
  title: string;
  body: string;
}

/**
 * Four architectural invariants the buyer (compliance officer or
 * engineering lead) will actually probe in a procurement call. Each
 * pairs a 1-line claim with the AI Act article it maps to, so the
 * mapping is visible without reading paragraphs.
 *
 * All four are verified in the codebase per AUDIT.md §2 ("seven
 * non-negotiables"). No vapor here — every claim resolves to a file.
 */
const INVARIANTS: InvariantProps[] = [
  {
    icon: Gauge,
    art: "Annex III",
    title: "Deterministic risk classifier",
    body: "Pure-Python rules. Strict precedence. Never declassifies.",
  },
  {
    icon: FileLock2,
    art: "Art. 12",
    title: "Append-only audit log",
    body: "Postgres trigger raises on UPDATE / DELETE. No service-layer mutation API.",
  },
  {
    icon: Lock,
    art: "Art. 12",
    title: "Privacy by default",
    body: "SHA-256 hashes I/O at the host. Plaintext is opt-in (v0.2).",
  },
  {
    icon: Server,
    art: "Hosting",
    title: "EU-hosted",
    body: "Hetzner Falkenstein for the collector. Mistral Paris for advisor calls.",
  },
];

function UnderTheHood() {
  return (
    <div className="mt-16 border-t border-border/60 pt-10">
      <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <span className="eyebrow">Under the hood</span>
        <span className="text-xs text-muted-foreground">
          Four invariants wired into the data layer
        </span>
      </div>
      <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {INVARIANTS.map((inv) => (
          <Invariant key={inv.title} {...inv} />
        ))}
      </ul>
      <p className="mt-6 flex items-center gap-2 text-xs text-muted-foreground">
        <FileCheck2 className="size-3.5 shrink-0" aria-hidden />
        Verified in code, not policy. See{" "}
        <code className="inline-code">AGENTS.md</code> for the full list of
        seven non-negotiables.
      </p>
    </div>
  );
}

function Invariant({ icon: Icon, art, title, body }: InvariantProps) {
  return (
    <li className="rounded-md border border-border/70 bg-background/60 p-4">
      <div className="flex items-center gap-2">
        <Icon className="size-3.5 text-[var(--brand-cobalt)]" aria-hidden />
        <span className="rounded-sm bg-[var(--brand-cobalt)]/10 px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-[var(--brand-cobalt)]">
          {art}
        </span>
      </div>
      <h3 className="mt-2.5 text-sm font-semibold text-foreground">
        {title}
      </h3>
      <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
        {body}
      </p>
    </li>
  );
}
