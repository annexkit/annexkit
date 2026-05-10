/**
 * How it works — three numbered steps with the actual command/code per
 * step, so a developer can mentally execute the path before clicking
 * "Get started". Each step is its own card to make the sequence visually
 * skimmable; the cobalt step number ties them to the brand.
 */

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
            body="On demand from the API or via your trust page. Bilingual EN / IT. Average 75 KB, regulator-grade."
            code={[
              "GET /api/v1/systems/",
              "    loan-screener/annex-iv",
              "    ?format=pdf",
            ]}
            language="http"
          />
        </ol>
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
