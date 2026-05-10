/**
 * Privacy Policy.
 *
 * Status: starter content authored to GDPR + Italian Codice Privacy
 * (D.lgs. 196/2003 as amended by D.lgs. 101/2018) baseline. Not legal
 * advice — have an Italian privacy lawyer review before claiming "live"
 * compliance. Placeholders marked with [BRACKETS] must be replaced with
 * real values before publishing the live site.
 */

import type { Metadata } from "next";

import {
  LegalProseStyles,
  LegalShell,
} from "@/components/legal-shell";

export const metadata: Metadata = {
  title: "Privacy policy",
  description:
    "How AnnexKit collects, stores, and processes personal data under " +
    "GDPR (Reg. (EU) 2016/679) and the Italian Codice Privacy.",
  alternates: { canonical: "/privacy" },
};

const SECTIONS = [
  { id: "controller", title: "Data controller" },
  { id: "data-collected", title: "What we collect" },
  { id: "purposes", title: "Why we process it" },
  { id: "storage", title: "Where it's stored" },
  { id: "retention", title: "How long we keep it" },
  { id: "sharing", title: "Who we share it with" },
  { id: "rights", title: "Your rights" },
  { id: "transfers", title: "International transfers" },
  { id: "changes", title: "Changes to this policy" },
];

export default function PrivacyPage() {
  return (
    <>
      <LegalProseStyles />
      <LegalShell
        title="Privacy policy"
        updated="2026-05-10"
        summary={
          <>
            <strong>Plain-English summary:</strong> AnnexKit collects the
            minimum data needed to run the service. By default the SDK
            SHA-256 hashes your prompts and outputs before they leave your
            host — we never see plaintext unless you opt in. Hosting is in
            the EU. You can delete your account and your data at any time.
          </>
        }
        sections={SECTIONS}
      >
        <section id="controller">
          <h2>Data controller</h2>
          <p>
            The data controller for personal data processed in connection
            with the AnnexKit hosted service at{" "}
            <a href="https://annexkit.dev">annexkit.dev</a> is{" "}
            <strong>[LEGAL NAME — e.g. AnnexKit S.r.l.]</strong>, with
            registered office at{" "}
            <strong>[REGISTERED ADDRESS]</strong>, Italy, VAT number{" "}
            <strong>[VAT / Partita IVA]</strong>.
          </p>
          <p>
            Privacy contact:{" "}
            <a href="mailto:privacy@annexkit.dev">privacy@annexkit.dev</a>.
          </p>
        </section>

        <section id="data-collected">
          <h2>What we collect</h2>
          <h3>Account data</h3>
          <p>
            When you sign up for a hosted plan we collect your email
            address, the legal name and address you provide for invoicing,
            VAT number where applicable, and password (stored as a salted
            hash). Payment data is collected and processed by{" "}
            <strong>Stripe Inc.</strong> — we never see your full card
            number.
          </p>
          <h3>Telemetry data</h3>
          <p>
            The AnnexKit SDK emits <strong>spans</strong> describing your
            LLM invocations: timestamps, latency, model identifier, token
            counts, declared system identifier. By default the inputs and
            outputs are <strong>SHA-256 hashed</strong> before they leave
            your host. We never see the plaintext of your prompts or
            generations unless you explicitly opt in to plaintext
            retention (which lands in v0.2 with encryption-at-rest, gated
            behind a per-tenant flag).
          </p>
          <h3>Server logs</h3>
          <p>
            Standard HTTP request logs (IP, user agent, path, status) are
            kept for 30 days for security and abuse prevention. They are
            not cross-referenced with account data unless required to
            investigate a specific incident.
          </p>
        </section>

        <section id="purposes">
          <h2>Why we process it</h2>
          <ul>
            <li>
              <strong>Provide the service</strong> — store your declared
              AI systems, classify them, generate Annex IV documents.
              Legal basis: contract performance (Art. 6(1)(b) GDPR).
            </li>
            <li>
              <strong>Bill you</strong> — send invoices, process payments
              via Stripe, comply with Italian tax law. Legal basis: legal
              obligation (Art. 6(1)(c) GDPR).
            </li>
            <li>
              <strong>Improve the service</strong> — aggregate, anonymised
              usage statistics. Legal basis: legitimate interest (Art.
              6(1)(f) GDPR).
            </li>
            <li>
              <strong>Send transactional emails</strong> — receipts,
              account notifications, security alerts. Legal basis:
              contract performance.
            </li>
          </ul>
          <p>
            We do not use your data to train any AI model. We do not sell
            your data.
          </p>
        </section>

        <section id="storage">
          <h2>Where it&rsquo;s stored</h2>
          <ul>
            <li>
              <strong>Hosted collector + database</strong>: Hetzner Cloud,
              Falkenstein, Germany.
            </li>
            <li>
              <strong>LLM advisor</strong> (when used for ambiguous
              declarations): Mistral La Plateforme, Paris, France.
            </li>
            <li>
              <strong>Payment processing</strong>: Stripe, Inc. (Ireland
              for EU customers).
            </li>
            <li>
              <strong>Transactional email</strong>: [TBD — likely Resend
              or Postmark, EU region where available].
            </li>
          </ul>
          <p>
            All hosted-product data stays in the EU/EEA. There are no
            transfers to third countries for the data we control directly
            (see <a href="#transfers">International transfers</a> for
            sub-processor exceptions).
          </p>
        </section>

        <section id="retention">
          <h2>How long we keep it</h2>
          <ul>
            <li>
              <strong>Account data</strong> — for the duration of the
              subscription, plus 10 years for invoicing records (Italian
              tax law obligation).
            </li>
            <li>
              <strong>Telemetry / spans</strong> — by default 90 days
              rolling. Adjustable per tenant on Team and Enterprise.
            </li>
            <li>
              <strong>Audit log entries</strong> — append-only, retained
              for the duration of the subscription. Customers can export
              the full log at any time.
            </li>
            <li>
              <strong>Server logs</strong> — 30 days.
            </li>
          </ul>
          <p>
            On account deletion, we delete personal data within 30 days
            except where retention is legally required (e.g. invoicing).
          </p>
        </section>

        <section id="sharing">
          <h2>Who we share it with</h2>
          <p>
            We use the following sub-processors. Each is listed with the
            data they receive and the legal basis for the transfer.
          </p>
          <ul>
            <li>
              <strong>Hetzner Online GmbH</strong> (Germany) — hosting.
              Data: all customer data. Basis: DPA + EU residency.
            </li>
            <li>
              <strong>Mistral AI</strong> (France) — LLM advisor for
              ambiguous declarations. Data: declaration text only, no
              spans, no PII. Basis: DPA + EU residency.
            </li>
            <li>
              <strong>Stripe, Inc.</strong> (Ireland for EU billing) —
              payment processing. Data: billing email, billing address,
              payment instrument. Basis: DPA + Standard Contractual
              Clauses for any US transfers.
            </li>
            <li>
              <strong>Cloudflare, Inc.</strong> (Ireland for EU traffic) —
              DNS, CDN, DDoS protection. Data: IP, request metadata.
              Basis: DPA + SCCs.
            </li>
          </ul>
          <p>
            Enterprise customers receive the full sub-processor list with
            their DPA. Material changes are notified by email at least 30
            days before they take effect.
          </p>
        </section>

        <section id="rights">
          <h2>Your rights</h2>
          <p>
            Under GDPR you have the right to:
          </p>
          <ul>
            <li>Access the personal data we hold about you (Art. 15).</li>
            <li>Have inaccurate data corrected (Art. 16).</li>
            <li>Have your data deleted (Art. 17).</li>
            <li>Restrict processing (Art. 18).</li>
            <li>Export your data in a portable format (Art. 20).</li>
            <li>Object to processing based on legitimate interest (Art. 21).</li>
          </ul>
          <p>
            Email{" "}
            <a href="mailto:privacy@annexkit.dev">privacy@annexkit.dev</a>{" "}
            to exercise any of these rights — we respond within 30 days.
            You also have the right to lodge a complaint with the Italian
            data protection authority (<a href="https://www.garanteprivacy.it">
              Garante per la protezione dei dati personali
            </a>).
          </p>
        </section>

        <section id="transfers">
          <h2>International transfers</h2>
          <p>
            Customer-controlled data (account, spans, declarations) stays
            in the EU/EEA at all times. Some sub-processors (Stripe,
            Cloudflare) are US-headquartered but operate EU regions for
            our traffic. Where personal data is transferred outside the
            EU/EEA, we rely on the European Commission&rsquo;s Standard
            Contractual Clauses.
          </p>
        </section>

        <section id="changes">
          <h2>Changes to this policy</h2>
          <p>
            Material changes are announced by email to all active
            customers and posted on this page. The &ldquo;last
            updated&rdquo; date at the top reflects the most recent
            revision.
          </p>
        </section>
      </LegalShell>
    </>
  );
}
