/**
 * Cookie Policy.
 *
 * Status: AnnexKit currently uses ONE first-party cookie / localStorage
 * key (the theme preference). No tracking, no analytics by default.
 * When analytics land (Plausible / Umami) update the table below
 * accordingly — both are cookieless by default but the policy needs to
 * reflect their inclusion.
 */

import type { Metadata } from "next";

import {
  LegalProseStyles,
  LegalShell,
} from "@/components/legal-shell";

export const metadata: Metadata = {
  title: "Cookie policy",
  description:
    "AnnexKit uses one first-party storage key for theme preference. " +
    "No tracking cookies, no third-party analytics by default.",
  alternates: { canonical: "/cookies" },
};

const SECTIONS = [
  { id: "overview", title: "Overview" },
  { id: "what-we-use", title: "What we use" },
  { id: "what-we-dont", title: "What we don't use" },
  { id: "manage", title: "How to manage" },
  { id: "changes", title: "Changes" },
];

export default function CookiePolicyPage() {
  return (
    <>
      <LegalProseStyles />
      <LegalShell
        title="Cookie policy"
        updated="2026-05-10"
        summary={
          <>
            <strong>Plain-English summary:</strong> we don&rsquo;t track
            you. The site uses a single browser localStorage entry to
            remember your theme preference (light / dark / system).
            That&rsquo;s it.
          </>
        }
        sections={SECTIONS}
      >
        <section id="overview">
          <h2>Overview</h2>
          <p>
            This page covers cookies and similar local-storage technologies
            used by{" "}
            <a href="https://annexkit.dev">annexkit.dev</a> and any
            sub-domain we operate. It explains what we use, why, how
            long it lasts, and how you can disable it.
          </p>
        </section>

        <section id="what-we-use">
          <h2>What we use</h2>
          <p>
            We currently use one first-party browser-storage entry. It is{" "}
            <strong>not a cookie</strong> in the strict sense (we use
            <code>localStorage</code>, which sits outside the Cookie
            Consent regulation envelope), but we list it here for full
            transparency.
          </p>
          <ul>
            <li>
              <strong>
                <code>annexkit-theme</code>
              </strong>{" "}
              — stores your chosen theme (<code>light</code>,{" "}
              <code>dark</code>, or <code>system</code>). Set when you
              click the theme toggle. First-party, no expiry, no PII,
              never transmitted to the server.
            </li>
          </ul>
        </section>

        <section id="what-we-dont">
          <h2>What we don&rsquo;t use</h2>
          <ul>
            <li>
              <strong>No advertising cookies.</strong> Ever.
            </li>
            <li>
              <strong>No third-party analytics.</strong> If we add
              analytics in the future, they will be cookieless (Plausible
              or Umami) and this page will be updated.
            </li>
            <li>
              <strong>No social-media tracking pixels.</strong>
            </li>
            <li>
              <strong>No fingerprinting.</strong>
            </li>
          </ul>
          <p>
            Stripe (our payment processor) sets its own cookies on the
            checkout page — those are subject to Stripe&rsquo;s privacy
            and cookie policies and are necessary to process payment.
            They never appear on annexkit.dev itself, only on the Stripe
            checkout page if/when you choose to subscribe.
          </p>
          <p>
            Cloudflare (our CDN) may set short-lived security cookies on
            edge requests for DDoS / bot protection. Those are{" "}
            &ldquo;strictly necessary&rdquo; under EU rules and do not
            require consent.
          </p>
        </section>

        <section id="manage">
          <h2>How to manage</h2>
          <p>
            Because the only entry we set is theme preference, you can
            clear it at any time:
          </p>
          <ul>
            <li>
              In your browser&rsquo;s site-data settings, clear storage
              for <code>annexkit.dev</code>.
            </li>
            <li>
              Or open DevTools → Application → Local Storage →{" "}
              <code>annexkit.dev</code> → delete{" "}
              <code>annexkit-theme</code>.
            </li>
            <li>
              Cycling the theme toggle will rewrite the entry on next
              click.
            </li>
          </ul>
          <p>
            Disabling localStorage entirely (e.g. private-mode Safari)
            still works — the site falls back to your operating-system
            preference each load.
          </p>
        </section>

        <section id="changes">
          <h2>Changes</h2>
          <p>
            If we add analytics or any other client-side storage, we
            update this page and the &ldquo;last updated&rdquo; date at
            the top before shipping the change.
          </p>
          <p>
            Privacy questions:{" "}
            <a href="mailto:privacy@annexkit.dev">privacy@annexkit.dev</a>.
          </p>
        </section>
      </LegalShell>
    </>
  );
}
