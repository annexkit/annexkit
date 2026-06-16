/**
 * Terms of Service.
 *
 * Status: starter content. Italian law, Verona jurisdiction. Replace
 * placeholders [BRACKETS] before launch and have an Italian commercial
 * lawyer review the liability cap and warranty disclaimers — those are
 * the clauses that get litigated.
 */

import type { Metadata } from "next";

import {
  LegalProseStyles,
  LegalShell,
} from "@/components/legal-shell";

export const metadata: Metadata = {
  title: "Terms of service",
  description:
    "Terms governing use of the AnnexKit hosted product, the AnnexKit " +
    "SDK, and the trust-center frontend.",
  alternates: { canonical: "/terms" },
};

const SECTIONS = [
  { id: "scope", title: "Scope" },
  { id: "service", title: "The service" },
  { id: "licences", title: "Licences" },
  { id: "billing", title: "Billing & cancellation" },
  { id: "acceptable-use", title: "Acceptable use" },
  { id: "no-legal-advice", title: "No legal advice" },
  { id: "warranties", title: "Warranties" },
  { id: "liability", title: "Liability" },
  { id: "termination", title: "Termination" },
  { id: "changes", title: "Changes" },
  { id: "law", title: "Governing law" },
];

export default function TermsPage() {
  return (
    <>
      <LegalProseStyles />
      <LegalShell
        title="Terms of service"
        updated="2026-05-10"
        preLaunch
        summary={
          <>
            <strong>Plain-English summary:</strong> use AnnexKit
            responsibly, pay your invoices, and don&rsquo;t treat the
            generated documents as legal advice. We&rsquo;re responsible
            for keeping the service running and your data safe; you&rsquo;re
            responsible for what you declare and how you use the output.
          </>
        }
        sections={SECTIONS}
      >
        <section id="scope">
          <h2>Scope</h2>
          <p>
            These Terms govern your use of:
          </p>
          <ul>
            <li>
              The hosted AnnexKit collector and trust-center at{" "}
              <a href="https://annexkit.dev">annexkit.dev</a> (the
              &ldquo;<strong>Service</strong>&rdquo;).
            </li>
            <li>
              The Python SDK published as{" "}
              <a href="https://pypi.org/project/annexkit/">
                annexkit on PyPI
              </a>{" "}
              (the &ldquo;<strong>SDK</strong>&rdquo;).
            </li>
          </ul>
          <p>
            By creating an account or installing the SDK with an API key
            you accept these Terms. If you&rsquo;re accepting on behalf
            of a company, you confirm you have authority to bind that
            company.
          </p>
          <p>
            <strong>Provider.</strong> The Service is provided by{" "}
            <strong>[LEGAL NAME — e.g. AnnexKit S.r.l.]</strong>,
            registered in Italy at <strong>[REGISTERED ADDRESS]</strong>,
            VAT <strong>[VAT / Partita IVA]</strong>{" "}
            (&ldquo;<strong>AnnexKit</strong>&rdquo;,
            &ldquo;<strong>we</strong>&rdquo;,
            &ldquo;<strong>us</strong>&rdquo;).
          </p>
        </section>

        <section id="service">
          <h2>The service</h2>
          <p>
            AnnexKit collects spans from your LLM-powered code,
            classifies the systems you declare against the EU AI Act risk
            tiers, persists an append-only audit log, and renders Annex
            IV documentation as PDF and Markdown.
          </p>
          <p>
            We commit to commercially reasonable efforts to keep the
            Service available. Planned maintenance is announced at least
            48 hours in advance where possible. Status and incident
            history are at <a href="https://status.annexkit.dev">
              status.annexkit.dev
            </a>{" "}
            (when launched).
          </p>
        </section>

        <section id="licences">
          <h2>Licences</h2>
          <p>
            The repository is dual-licensed:
          </p>
          <ul>
            <li>
              <strong>SDK</strong> — MIT. You may use, modify, and
              redistribute it freely.
            </li>
            <li>
              <strong>Collector backend + trust-center frontend</strong>{" "}
              — AGPL-3.0. You may self-host. If you expose modifications
              of the AGPL code as a network service, you must publish
              your source under the same licence.
            </li>
          </ul>
          <p>
            These Terms govern your use of the hosted Service in addition
            to the relevant open-source licence. Where they conflict, the
            open-source licence governs your rights to the code; these
            Terms govern your contractual relationship with us as a
            customer.
          </p>
        </section>

        <section id="billing">
          <h2>Billing &amp; cancellation</h2>
          <p>
            Pro and Team are billed monthly in advance via Stripe.
            Enterprise is billed annually in advance per the Order Form.
            All prices exclude VAT, which is added where applicable.
          </p>
          <p>
            You may cancel at any time from the customer dashboard or by
            emailing{" "}
            <a href="mailto:billing@annexkit.dev">billing@annexkit.dev</a>.
            Cancellation takes effect at the end of the current billing
            period; we do not pro-rate monthly fees. Yearly Enterprise
            terms are refundable pro-rata on cancellation.
          </p>
          <p>
            We may suspend the Service if an invoice is more than 30 days
            overdue, after at least 7 days&rsquo; written notice.
          </p>
        </section>

        <section id="acceptable-use">
          <h2>Acceptable use</h2>
          <p>You agree not to:</p>
          <ul>
            <li>Use the Service to declare AI systems you do not own or operate.</li>
            <li>
              Submit telemetry that would mislead an auditor or regulator
              about a system&rsquo;s real risk tier.
            </li>
            <li>
              Probe, scan, or stress-test the Service in ways that affect
              other tenants.
            </li>
            <li>
              Use the Service in ways that breach the EU AI Act, GDPR, or
              applicable export-control law.
            </li>
            <li>
              Resell access to the hosted Service without a written
              partnership agreement.
            </li>
          </ul>
        </section>

        <section id="no-legal-advice">
          <h2>No legal advice</h2>
          <p>
            <strong>
              AnnexKit is not a law firm; AnnexKit non è uno studio
              legale.
            </strong>{" "}
            The classifications, gap-analysis tables, and Annex IV
            documents the Service generates are technical artefacts based
            on the data you declare. They are not a conformity assessment
            and are not a substitute for advice from your lawyer or your
            notified body. You are responsible for reviewing the output
            with qualified legal counsel before relying on it for any
            regulatory submission, audit, or contractual claim.
          </p>
        </section>

        <section id="warranties">
          <h2>Warranties</h2>
          <p>
            We warrant that the Service will materially conform to the
            description in our public documentation and that we will use
            commercially reasonable efforts to keep it secure and
            available.
          </p>
          <p>
            <strong>
              The Service and the SDK are otherwise provided
              &ldquo;as is&rdquo;.
            </strong>{" "}
            We disclaim all other warranties to the maximum extent
            permitted by Italian law, including warranties of
            merchantability, fitness for a particular purpose, and
            non-infringement.
          </p>
        </section>

        <section id="liability">
          <h2>Liability</h2>
          <p>
            To the maximum extent permitted by law, our total aggregate
            liability for any claim arising under these Terms is limited
            to the fees you paid us in the 12 months preceding the event
            giving rise to the claim. We are not liable for indirect,
            incidental, special, consequential, or punitive damages,
            including lost profits, lost data, or regulatory fines.
          </p>
          <p>
            Nothing in these Terms limits liability that cannot be
            limited under Italian law (gross negligence, wilful
            misconduct, personal injury, etc.).
          </p>
        </section>

        <section id="termination">
          <h2>Termination</h2>
          <p>
            Either party may terminate the agreement for material breach
            uncured 30 days after written notice. We may terminate
            immediately for breaches of acceptable-use that affect other
            tenants or applicable law.
          </p>
          <p>
            On termination you can export your data for 30 days. After
            that we delete it except where retention is legally required
            (see the <a href="/privacy">Privacy policy</a>).
          </p>
        </section>

        <section id="changes">
          <h2>Changes</h2>
          <p>
            We may update these Terms. Material changes are announced by
            email at least 30 days before they take effect. Continued use
            of the Service after the effective date constitutes
            acceptance.
          </p>
        </section>

        <section id="law">
          <h2>Governing law</h2>
          <p>
            These Terms are governed by Italian law. Any dispute arising
            under or in connection with them falls under the exclusive
            jurisdiction of the courts of Verona, Italy. EU consumers
            keep their right to bring claims in their home jurisdiction
            where applicable.
          </p>
          <p>
            For questions, write to{" "}
            <a href="mailto:legal@annexkit.dev">legal@annexkit.dev</a>.
          </p>
        </section>
      </LegalShell>
    </>
  );
}
