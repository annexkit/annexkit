# Test walkthrough — three paying-customer personas

End-to-end exercise of the full AnnexKit pipeline against three
realistic customer profiles, one per pricing tier. Run it before
shipping anything publicly: every endpoint, every regex, every
template gets exercised against representative data.

By the end you will have **eight files** in [`out/`](out/):

| File | Persona | Tier | Format |
|---|---|---|---|
| `annex-iv-customer-support-bot.pdf` + `.md` | Acme SaaS | Pro $49/mo | LIMITED risk |
| `annex-iv-cv-screener.pdf` + `.md` | TechHire | Team $199/mo | HIGH (Annex III §4) |
| `annex-iv-interview-scheduler.pdf` + `.md` | TechHire | Team $199/mo | LIMITED |
| `annex-iv-loan-prescreen.pdf` + `.md` | Banca Esempio | Enterprise €5K/yr | HIGH (Annex III §5) |

The PDFs are what the customer would download from the AnnexKit
dashboard at `annexkit.dev/dashboard/<system>/annex-iv` once that lands
in M4. The walkthrough validates the underlying API path that powers
that dashboard today.

---

## Prerequisites

  1. Stack running: `make up` from the project root.
  2. Postgres has at least one tenant with an API key. Easiest:
     `make seed` from the project root and copy the printed key.
  3. Python `uv` available on the host (already required for the SDK).

---

## Two ways to run

### One-shot (recommended)

From the **project root**:

```bash
make walkthrough
```

This seeds a fresh tenant, exports the API key for the duration of
the run, and executes `walkthrough.py`. You'll see roughly:

```
=== Acme SaaS S.r.l. — customer-support chatbot =========
  Tier: Pro — $49/month
  ...
  [PUT  /api/v1/systems] customer-support-bot     -> tier LIMITED, rules v1.0.0
  [POST /api/v1/spans]    customer-support-bot     -> 6 spans ingested
  [GET annex-iv format=md] customer-support-bot     ->  10,847 bytes  saved annex-iv-customer-support-bot.md
  [GET annex-iv format=pdf] customer-support-bot     ->  73,021 bytes  saved annex-iv-customer-support-bot.pdf
=== TechHire S.p.A. — HR-tech, two AI systems ==========
  ...
=== Banca Esempio S.p.A. — loan pre-screening (regulated) ==========
  ...

=== Walkthrough complete ===
  3 personas walked end-to-end
  4 AI systems declared
  21 spans ingested
  8 output files saved to .../examples/test-walkthrough/out/
```

When it finishes, open the `out/` directory and inspect each PDF.

### Manual (use your own API key)

```bash
cd examples/test-walkthrough
cp .env.example .env
# Paste the ak_... key from `make seed` into .env
uv sync
uv run python walkthrough.py
```

---

## Persona 1 — Acme SaaS S.r.l. (Pro $49/month)

**Profile**: small SaaS company in Bologna. One LLM-powered customer-
support chatbot answering shipping, returns, and account questions
via OpenAI gpt-4o-mini + a 47-article FAQ knowledge base.

**AI Act fit**: no high-risk Annex III categories, but the chatbot
form factor triggers Article 50 transparency obligations. The
classifier returns **LIMITED** risk.

**What this persona tests**:

- Provider info partially populated (legal name, address, country,
  contact, system version, software environment, hardware, notes —
  everything except `validation_methods`, intentionally left blank
  to verify the gap-analysis output handles partial data).
- 6 spans ingested across 5 days, including 1 OpenAI rate-limit
  error to verify the §8.2 error-breakdown table.
- 3 retrieval sources cited (`kb://faq/shipping-times`,
  `kb://faq/return-policy`, `kb://faq/account-management`).
- Article 50 transparency trigger declared but no Annex III categories.

**What to verify in the generated PDF**:

- Cover page badge: **LIMITED RISK / RISCHIO LIMITATO** (teal).
- §1.4 Risk classification: triggered rule
  `art50_chat_interaction` (Article 50, transparency).
- §2.2 Models in use: 6 invocations, openai/gpt-4o-mini, single version.
- §2.3 Retrieval sources: 3 distinct `kb://faq/*` URIs with citations.
- §3.3 Latency: p50/p95/p99 in the 700-2400ms range.
- §8.2 Error breakdown: 1 × `openai.APIError` (rate limit).
- §9.2 Limitations callout: Article 50 disclosure obligation for deployers.
- Appendix A gap analysis: §2.4 validation methodology = MANUAL
  (provider input required) — Acme didn't fill it.

---

## Persona 2 — TechHire S.p.A. (Team $199/month)

**Profile**: 30-person HR-tech scaleup in Milano. Two AI systems in
production:

  1. `cv-screener` — pre-ranks CVs against role profiles (HuggingFace
     sentence-transformers + a fine-tuned ranking head).
  2. `interview-scheduler` — chatbot that schedules first-round
     interviews via Google Calendar (Anthropic Claude Sonnet).

**AI Act fit**:

  - `cv-screener` → Annex III §4 employment + workers management →
    **HIGH** risk.
  - `interview-scheduler` → no Annex III categories, but chatbot →
    Article 50 → **LIMITED** risk.

**What this persona tests**:

- Multi-system tenant: two declarations under one tenant; each
  generates its own Annex IV PDF with system-specific aggregations.
- HIGH-risk system with full validation methodology populated
  (precision@20, recall, adverse-impact testing description).
- Different model providers per system (HuggingFace for the ranker,
  Anthropic for the scheduler) — exercises the §2.1 model inventory
  table per system.
- 4 spans per system over 4 days.

**What to verify in the generated PDFs**:

- `annex-iv-cv-screener.pdf`:
  - Cover badge: **HIGH RISK / ALTO RISCHIO** (orange).
  - §1.4: triggered rule `annex3_4_employment`.
  - §2.4 Validation methodology: full text (precision@20 = 0.78 etc.).
  - §9.2 Limitations: "Article 26 deployer obligations apply" callout.
- `annex-iv-interview-scheduler.pdf`:
  - Cover badge: **LIMITED RISK / RISCHIO LIMITATO** (teal).
  - §1.4: triggered rule `art50_chat_interaction`.
  - §2.2: anthropic / claude-sonnet-4-5 model row.
  - §9.6: Article 50 transparency disclosures listed.

---

## Persona 3 — Banca Esempio S.p.A. (Enterprise self-hosted €5K/year)

**Profile**: an Italian retail bank. One regulated AI system: a
loan-eligibility pre-screener for SME loans of €10K-€100K, running
on Mistral La Plateforme (Frankfurt) over a policy KB.

**AI Act fit**: Annex III §5 essential services (credit decisioning)
+ Article 50 (chatbot interaction) → **HIGH** risk.

**What this persona tests**:

- Fully populated `provider_info` (legal name, address, country,
  contact, **authorised representative**, system version, software
  + hardware environment, validation methods, notes) — the
  regulator-presentation-grade case.
- Single high-risk system with HIGH-risk Annex III declaration.
- 8 spans across 6 days, including 1 timeout error to verify the
  failure-rate calculation.
- 5 distinct policy-KB URIs cited with versions, exercising the
  §2.3 retrieval-sources table at scale.
- Two distinct user roles observed (`loan_applicant`, `loan_officer`)
  to populate §3.4 human-oversight context.

**What to verify in the generated PDF**:

- Cover badge: **HIGH RISK / ALTO RISCHIO**.
- §1.2 Persons responsible: legal name, address, country, contact,
  authorised representative all present.
- §1.3 System version + environment: v2.4.1, full Python +
  Mistral + AWS Frankfurt description.
- §1.4 Risk classification: 2 triggered rules
  (`annex3_5_essential_services` + `art50_chat_interaction`).
- §2.4 Validation methodology: 4-paragraph regulator-grade text
  (back-testing, parity testing, adversarial testing, retention).
- §3.3 Latency: p50/p95/p99 across the 8 spans (~1700-2350ms).
- §3.4 Human oversight: `loan_applicant` + `loan_officer` user roles.
- §5 Description of changes: at least 1 entry (the
  `ai_system.created` audit-log row from the PUT).
- §8.2 Error breakdown: 1 × `httpx.TimeoutException`.
- Appendix A gap analysis: most rows AUTO, none MANUAL —
  the most complete declaration possible.
- Appendix C sample evidence: 8 `trace_id` rows for forensic
  cross-reference.
- Appendix D sign-off: signature blocks for provider's authorised
  signatory + compliance officer.

---

## After the run — verification checklist

Tick each item before considering the test passed:

  - [ ] `out/` contains 4 PDFs and 4 Markdown files.
  - [ ] Every PDF opens cleanly in Preview / Acrobat / Chrome.
  - [ ] Every PDF's cover page shows the correct risk-tier badge
        (LIMITED for Acme + interview-scheduler, HIGH for cv-screener
        + loan-prescreen).
  - [ ] Every PDF's §3.2 logging table shows the right invocation
        count (Acme: 6, cv-screener: 4, interview-scheduler: 4,
        loan-prescreen: 8).
  - [ ] The Markdown copies of each PDF contain the same content
        (use `diff` or your eyes — they should be byte-aligned
        section by section).
  - [ ] No "AI assistant brief" / "Claude" / similar string appears
        in any generated PDF (the disclosure callouts use neutral
        language like "AI nature of relevant interactions").
  - [ ] All four PDFs include the permanent disclaimer ("AnnexKit
        is not a law firm / non è uno studio legale") on the cover
        + at the end.

If every box is ticked, the v0.1.0 release is operationally
production-ready.

---

## Cleanup

```bash
# from project root
docker compose down       # stops collector + db (PDFs in out/ persist)
rm -rf examples/test-walkthrough/out/  # delete generated PDFs
make db-reset             # ⚠ wipes all tenants; only if you want a fresh start
```

---

## Troubleshooting

**"Collector at http://localhost:8033 is not reachable"** — run
`make up` from the project root.

**"ERROR: ANNEXKIT_API_KEY not set"** — either run via `make
walkthrough` (auto-seeds + injects) or paste an `ak_...` key into
`.env`.

**PDF generation slow / fails** — Annex IV PDFs are rendered
server-side via WeasyPrint inside the backend container. The native
deps (Cairo + Pango) are installed in the image. If a PDF endpoint
returns 500, check `docker compose logs backend` for the WeasyPrint
trace.

**"AI system 'X' not declared for tenant"** — happens if you abort
mid-run and re-execute against a different tenant. Easiest fix:
`make db-reset && make walkthrough`.
