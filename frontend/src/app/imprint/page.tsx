/**
 * Imprint / Informazioni obbligatorie.
 *
 * Required by Italian e-commerce law (D.lgs. 70/2003 art. 7) for any
 * commercial site reaching Italian consumers, and by German Telemedia
 * Act § 5 for any site reaching German users (Hetzner customers
 * commonly serve DE traffic too).
 *
 * Replace [BRACKETS] with real values before launch. The Imprint must
 * be reachable in two clicks from any page — the footer link satisfies
 * that.
 */

import type { Metadata } from "next";

import {
  LegalProseStyles,
  LegalShell,
} from "@/components/legal-shell";

export const metadata: Metadata = {
  title: "Imprint",
  description:
    "Legal information about AnnexKit, the company behind this site.",
  alternates: { canonical: "/imprint" },
};

const SECTIONS = [
  { id: "provider", title: "Provider" },
  { id: "contact", title: "Contact" },
  { id: "registration", title: "Registration" },
  { id: "vat", title: "VAT identification" },
  { id: "responsible", title: "Editorial responsibility" },
  { id: "dispute", title: "Dispute resolution" },
];

export default function ImprintPage() {
  return (
    <>
      <LegalProseStyles />
      <LegalShell
        title="Imprint"
        updated="2026-05-10"
        preLaunch
        sections={SECTIONS}
      >
        <section id="provider">
          <h2>Provider</h2>
          <p>
            <strong>[LEGAL NAME — e.g. AnnexKit S.r.l.]</strong>
            <br />
            [REGISTERED ADDRESS LINE 1]
            <br />
            [POSTAL CODE] [CITY], Italy
          </p>
          <p>
            Legal representative: <strong>[FOUNDER NAME]</strong>.
          </p>
        </section>

        <section id="contact">
          <h2>Contact</h2>
          <ul>
            <li>
              General:{" "}
              <a href="mailto:founder@annexkit.dev">
                founder@annexkit.dev
              </a>
            </li>
            <li>
              Privacy:{" "}
              <a href="mailto:privacy@annexkit.dev">
                privacy@annexkit.dev
              </a>
            </li>
            <li>
              Legal:{" "}
              <a href="mailto:legal@annexkit.dev">legal@annexkit.dev</a>
            </li>
            <li>
              Security:{" "}
              <a href="mailto:security@annexkit.dev">
                security@annexkit.dev
              </a>
            </li>
          </ul>
        </section>

        <section id="registration">
          <h2>Registration</h2>
          <p>
            Registered with the Italian Business Register (Registro delle
            Imprese) at the Chamber of Commerce of [CITY] under number{" "}
            <strong>[REA / Registration number]</strong>.
          </p>
        </section>

        <section id="vat">
          <h2>VAT identification</h2>
          <p>
            Italian VAT (Partita IVA): <strong>[VAT number]</strong>
          </p>
          <p>
            EU VAT identification (where applicable):{" "}
            <strong>IT[VAT number]</strong>
          </p>
        </section>

        <section id="responsible">
          <h2>Editorial responsibility</h2>
          <p>
            Responsible for content under § 18 paragraph 2 MStV / Italian
            press law equivalent: <strong>[FOUNDER NAME]</strong>, at
            the address above.
          </p>
        </section>

        <section id="dispute">
          <h2>Dispute resolution</h2>
          <p>
            The European Commission provides a platform for online
            dispute resolution (ODR) at{" "}
            <a href="https://ec.europa.eu/consumers/odr">
              ec.europa.eu/consumers/odr
            </a>
            . We are not obliged to participate in dispute-resolution
            proceedings before a consumer arbitration board and currently
            do not.
          </p>
        </section>
      </LegalShell>
    </>
  );
}
