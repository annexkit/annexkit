/**
 * Stakes — three big numbers that make the AI Act real.
 *
 * Goal: a CTO scrolling past should walk away with three facts they can
 * repeat to their CEO before lunch:
 *   1. Full force date — the deadline can't move
 *   2. Max fine — yes, the EU went hard
 *   3. Articles in scope for an LLM-using company — there's a list, it's finite
 *
 * The numbers are computed once at module level so they stay deterministic
 * and don't shift between dev and prod.
 */

const FULL_FORCE = new Date("2026-08-02T00:00:00Z");
const MS_IN_DAY = 1000 * 60 * 60 * 24;

function daysUntil(date: Date): number {
  return Math.max(0, Math.ceil((date.getTime() - Date.now()) / MS_IN_DAY));
}

export function Stakes() {
  const days = daysUntil(FULL_FORCE);

  return (
    <section className="border-b border-border/60">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="max-w-2xl space-y-3">
          <span className="eyebrow">The deadlines don&rsquo;t move</span>
          <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Every team running an LLM in production is on the AI Act
            clock.
          </h2>
          <p className="text-muted-foreground">
            Article 11 (technical doc), Article 12 (logging), Article 13
            (transparency to deployers), and Article 72 (post-market
            monitoring) all kick in on the same day. AnnexKit gives you
            the evidence.
          </p>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-3">
          <Stat
            value={days.toLocaleString("en-GB")}
            unit="days"
            label="until full force on 2 Aug 2026"
          />
          <Stat
            value="€35M"
            unit="or 7%"
            label="of global turnover — max fine for prohibited-AI breaches"
          />
          <Stat
            value="4 + 2"
            unit="articles"
            label="Reg. (EU) 2024/1689 obligations + Annex III & IV"
          />
        </div>
      </div>
    </section>
  );
}

interface StatProps {
  value: string;
  unit: string;
  label: string;
}

function Stat({ value, unit, label }: StatProps) {
  return (
    <div className="surface-card p-6">
      <div className="display-num text-4xl font-bold text-foreground sm:text-5xl">
        {value}
        <span className="ml-2 text-base font-medium text-muted-foreground">
          {unit}
        </span>
      </div>
      <p className="mt-3 text-sm text-muted-foreground">{label}</p>
    </div>
  );
}
