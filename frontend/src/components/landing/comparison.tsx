/**
 * Comparison — places AnnexKit on the map of "what else does this
 * problem look like in a buyer's head". Three rows: LLM observability,
 * AI-governance enterprise platforms, manual.
 *
 * The table is opinionated by design. Buyers benchmark in 30 seconds
 * and won't read paragraphs; surface the exact axes they care about
 * (AI Act mapping, price, lead-time) and let the cells do the work.
 */

import { Check, Minus, X } from "lucide-react";

interface Row {
  category: string;
  examples: string;
  aiActMapping: "yes" | "partial" | "no";
  price: string;
  shipTime: string;
  developerFirst: boolean;
}

const ROWS: Row[] = [
  {
    category: "LLM observability",
    examples: "LangSmith · Langfuse · Confident AI",
    aiActMapping: "no",
    price: "$50-500/mo",
    shipTime: "Hours",
    developerFirst: true,
  },
  {
    category: "AI governance platforms",
    examples: "Credo AI · Holistic AI · Saidot",
    aiActMapping: "yes",
    price: "€100K+/yr",
    shipTime: "3-6 mo sales cycle",
    developerFirst: false,
  },
  {
    category: "Manual",
    examples: "Engineers + lawyers + spreadsheet",
    aiActMapping: "partial",
    price: "Internal time",
    shipTime: "Weeks per system",
    developerFirst: false,
  },
];

export function Comparison() {
  return (
    <section className="border-b border-border/60">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="max-w-2xl space-y-3">
          <span className="eyebrow">Where AnnexKit fits</span>
          <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            The gap between observability and governance.
          </h2>
          <p className="text-muted-foreground">
            Compliance teams have enterprise-priced platforms. Engineers
            have observability tools that don&rsquo;t map to the AI Act.
            AnnexKit serves both ends without the procurement cycle.
          </p>
        </div>

        <div className="surface-card mt-12 overflow-x-auto">
          <table className="w-full min-w-[720px] border-collapse text-sm">
            <thead className="border-b border-border/60 bg-secondary/40">
              <tr className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                <th className="px-5 py-4">Approach</th>
                <th className="px-5 py-4">AI Act mapping</th>
                <th className="px-5 py-4">Price</th>
                <th className="px-5 py-4">Time to ship</th>
                <th className="px-5 py-4">Developer-first</th>
              </tr>
            </thead>
            <tbody>
              {ROWS.map((row) => (
                <ComparisonRow key={row.category} row={row} />
              ))}
              {/* AnnexKit row, highlighted */}
              <tr className="border-t border-border/60 bg-[var(--brand-cobalt)]/5">
                <td className="px-5 py-5">
                  <div className="flex items-center gap-2 font-semibold text-foreground">
                    <span
                      aria-hidden
                      className="size-1.5 rounded-full bg-[var(--brand-cobalt)]"
                    />
                    AnnexKit
                  </div>
                  <div className="mt-0.5 text-xs text-muted-foreground">
                    Open-core · EU-hosted · self-serve
                  </div>
                </td>
                <td className="px-5 py-5 text-foreground">
                  <span className="inline-flex items-center gap-1.5 font-medium text-[var(--brand-cobalt)]">
                    <Check className="size-4" />
                    Annex III + IV native
                  </span>
                </td>
                <td className="px-5 py-5 text-foreground">
                  €49 — €5K/mo
                </td>
                <td className="px-5 py-5 text-foreground">10 minutes</td>
                <td className="px-5 py-5 text-foreground">
                  <Check className="size-4 text-[var(--brand-cobalt)]" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function ComparisonRow({ row }: { row: Row }) {
  return (
    <tr className="border-t border-border/40 align-top text-muted-foreground">
      <td className="px-5 py-5">
        <div className="font-semibold text-foreground">{row.category}</div>
        <div className="mt-0.5 text-xs">{row.examples}</div>
      </td>
      <td className="px-5 py-5">
        <MappingCell mapping={row.aiActMapping} />
      </td>
      <td className="px-5 py-5">{row.price}</td>
      <td className="px-5 py-5">{row.shipTime}</td>
      <td className="px-5 py-5">
        {row.developerFirst ? (
          <Check className="size-4 text-muted-foreground" />
        ) : (
          <Minus className="size-4 text-muted-foreground/60" />
        )}
      </td>
    </tr>
  );
}

function MappingCell({ mapping }: { mapping: Row["aiActMapping"] }) {
  if (mapping === "yes") {
    return (
      <span className="inline-flex items-center gap-1.5">
        <Check className="size-4 text-foreground" /> Yes
      </span>
    );
  }
  if (mapping === "partial") {
    return (
      <span className="inline-flex items-center gap-1.5">
        <Minus className="size-4 text-muted-foreground" /> Partial
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5">
      <X className="size-4 text-muted-foreground/60" /> No
    </span>
  );
}
