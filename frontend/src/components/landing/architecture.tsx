/**
 * Architecture — visual rendering of the box-and-arrows diagram from the
 * project README. Built as composed divs (no SVG asset), so it scales
 * with the theme and stays crisp at any zoom.
 *
 * Pattern: top stack = "your code", arrow down, bottom stack = "what
 * AnnexKit does". The four boxes inside the bottom stack each reference
 * an article number so the AI Act mapping is visible without reading
 * paragraphs of marketing.
 */

import { ArrowDown } from "lucide-react";

interface CapabilityProps {
  art: string;
  title: string;
  body: string;
}

const CAPABILITIES: CapabilityProps[] = [
  {
    art: "Art. 12",
    title: "Span ingest",
    body: "SHA-256 hashes I/O at the host. Plaintext is opt-in.",
  },
  {
    art: "Annex III",
    title: "Risk classifier",
    body: "Deterministic rules. LLM advisors can suggest, never declassify.",
  },
  {
    art: "Art. 12",
    title: "Append-only audit log",
    body: "Postgres trigger raises on UPDATE / DELETE. By design.",
  },
  {
    art: "Annex IV",
    title: "PDF generator",
    body: "Bilingual EN / IT, ~75 KB, regulator-grade per system.",
  },
];

export function Architecture() {
  return (
    <section className="border-b border-border/60">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="max-w-2xl space-y-3">
          <span className="eyebrow">Under the hood</span>
          <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            One collector. Three architectural invariants.
          </h2>
          <p className="text-muted-foreground">
            Determinism, append-only logs, and privacy-by-default are wired
            into the data layer — not policies a product manager can flip
            off in a config screen.
          </p>
        </div>

        <div className="mt-12 flex flex-col items-center gap-6">
          {/* Top — your code */}
          <div className="surface-card flex w-full max-w-3xl flex-col gap-2 p-6 text-center">
            <span className="eyebrow">Your application</span>
            <p className="font-mono text-sm text-foreground">
              <span className="text-[var(--brand-cobalt)]">@</span>annexkit
              .track(...)
              <span className="text-muted-foreground">
                {" "}
                on each LLM call
              </span>
            </p>
          </div>

          <ArrowDown
            className="size-5 text-muted-foreground"
            aria-hidden
          />
          <span className="font-mono text-xs text-muted-foreground">
            HTTPS · HMAC-authenticated
          </span>
          <ArrowDown
            className="size-5 text-muted-foreground"
            aria-hidden
          />

          {/* Bottom — collector with 4 capability cards */}
          <div className="surface-card w-full max-w-3xl p-6">
            <div className="mb-5 flex items-center justify-between">
              <span className="eyebrow">AnnexKit collector</span>
              <span className="text-xs text-muted-foreground">
                FastAPI · Postgres 16 · EU-hosted
              </span>
            </div>
            <ul className="grid gap-3 sm:grid-cols-2">
              {CAPABILITIES.map((cap) => (
                <Capability key={cap.title} {...cap} />
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

function Capability({ art, title, body }: CapabilityProps) {
  return (
    <li className="rounded-md border border-border/70 bg-background/60 p-4">
      <div className="flex items-center gap-2">
        <span className="rounded-sm bg-[var(--brand-cobalt)]/10 px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-[var(--brand-cobalt)]">
          {art}
        </span>
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      </div>
      <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
        {body}
      </p>
    </li>
  );
}
