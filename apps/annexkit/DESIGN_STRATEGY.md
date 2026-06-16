# DESIGN STRATEGY — AnnexKit frontend

> Creative direction + frontend roadmap. Read top-to-bottom; the
> first 2 sections are the verdict and the *why*, the rest is the *how*.
> Author: independent audit, 2026-05-23.

---

## 0. Verdict

**The current design is competent — and that's exactly the problem.**

You hit the same notes every modern dev-tool SaaS hits: dark canvas, cobalt-blue
primary, grid background, terminal-mockup hero, surface-card pattern, OKLCH
tokens, tabular numerics. Each individual choice is correct. Together they
produce a site that is **indistinguishable from Vanta, Drata, Vercel,
LangSmith, Helicone, Sentry, Resend, Modal**, and every YC-batch B2B
infrastructure landing page shipped in the last 18 months.

A visitor scrolling LinkedIn at 11pm can't tell us apart from a portfolio of
"good SaaS landings". That's the differentiation problem.

**My recommendation**: shift the visual identity from "another cobalt dev-tool"
to **"editorial engineering"** — pair the editorial-italic monogram you already
have (`a` + `iv` superscript in EB Garamond italic) with a warm-ink-and-sage
palette, serif display headlines, and an aggressively reduced color
vocabulary. One bold non-blue accent. No gradients in the marketing default.
Generous editorial whitespace.

Three reasons this works for AnnexKit specifically:
1. The product *is* an editorial artifact — a regulatory document (Annex IV
   PDF). The visual identity should telegraph "this generates official
   documents", not "this is a streaming platform".
2. Your monogram already commits to editorial. Honour the commitment instead
   of fighting it with a generic dev-tool body.
3. The blue/cobalt neighbourhood is saturated and your competitors own the
   space. Pulling out of it is cheaper than competing inside it.

If you don't want to commit to a palette change, there's still ~3 days of
quick wins below that lift perceived quality without touching the brand.

---

## 1. Current state audit

### What's working (don't break)

| Asset | Where | Why it's good |
|---|---|---|
| OKLCH everything | [globals.css:78-152](frontend/src/app/globals.css#L78) | Future-proof, perceptually uniform — better than every HSL competitor's site |
| Editorial heading tracking | [globals.css:168-172](frontend/src/app/globals.css#L168) | `-0.028em` on h1 is the single biggest "looks designed" lever vs default Tailwind |
| Tabular numerics on stats | [globals.css:277-280](frontend/src/app/globals.css#L277) | `tnum` + `cv11` on display numbers — pricing tables and stats actually align |
| Cobalt selection colour | [globals.css:181-184](frontend/src/app/globals.css#L181) | The kind of detail premium products get right |
| Surface-card system | [globals.css:196-228](frontend/src/app/globals.css#L196) | Multi-stop shadow + hairline border — better than 90% of shadcn defaults |
| The `a` + `iv` monogram | [logo.tsx](frontend/src/components/logo.tsx) | Genuinely distinctive. The single most ownable asset in the brand |
| Geist + Geist Mono | [layout.tsx](frontend/src/app/layout.tsx) | Right choice for dev-tool; pairs with editorial serif if added |
| No-flash theme script | [layout.tsx](frontend/src/app/layout.tsx) | First-paint discipline |
| Konformia-style hub pattern | [tools/page.tsx](frontend/src/app/tools/page.tsx) | Eyebrow → big title → cards → brand-wash CTA. Rhythm is correct |

### Where it's generic / dated / weak

| # | Issue | Where | Why it hurts |
|---|---|---|---|
| W1 | **Brand-wash hero** is a radial cobalt gradient over ink | [globals.css:233-260](frontend/src/app/globals.css#L233) | Identical to ~50 SaaS landings. Reads as "default" |
| W2 | **Surface-grid** is the Vercel/Linear background pattern at this point | [globals.css:264-274](frontend/src/app/globals.css#L264) | Was distinctive in 2021; now table stakes |
| W3 | **All-caps eyebrows** (`tracking-[0.12em]`) | [globals.css:284-286](frontend/src/app/globals.css#L284) | Default shadcn/Linear/Vercel/Tailwind UI pattern. Generic |
| W4 | **Single typeface family** (Geist + Geist Mono) | [layout.tsx](frontend/src/app/layout.tsx) | Misses the chance to honour the EB Garamond commitment in the logo |
| W5 | **Hero terminal mockup** — code panel in dark window with traffic-light dots | [hero.tsx](frontend/src/components/landing/hero.tsx) | Vercel/Resend/Modal all do this. No-op for differentiation |
| W6 | **Tier badges** are flat coloured pills | [RiskBadge.tsx](frontend/src/components/RiskBadge.tsx) | Reads as "shadcn Badge"; should look like a regulatory stamp |
| W7 | **Button system** has 6 variants but all default-shaped | [components/ui/button.tsx](frontend/src/components/ui/button.tsx) | Default radii (rounded-md), default sizes. Nothing memorable |
| W8 | **Focus state** is generic ring | [globals.css:175-177](frontend/src/app/globals.css#L175) | Could carry a brand cue (e.g. cobalt → brass underline) |
| W9 | **No mobile nav drawer** | [site-header.tsx:13](frontend/src/components/site-header.tsx#L13) | The 4 nav links + GitHub + Get-started CTA all collide < md |
| W10 | **No active-page indicator** in header | [site-header.tsx](frontend/src/components/site-header.tsx) | Visitor on /tools can't tell from the nav |
| W11 | **CTA hierarchy collision** | hero + final-cta + pricing | Three "Get started" CTAs without escalating intent — reads as same CTA repeating |
| W12 | **No motion language** | everywhere | Static. Premium products have at least one signature interaction (Linear's command-K, Stripe's gradient pan, Arc's morphs) |
| W13 | **Dark-only canonical**, light is "secondary citizen" | [globals.css:79-117](frontend/src/app/globals.css#L79) comments | Misses the half of buyers who're compliance officers reviewing in daylight. Editorial direction loves light mode |
| W14 | **Risk-tier swatches are hex not OKLCH** | [globals.css:66-75](frontend/src/app/globals.css#L66) | Inconsistent with the rest of the system; can't reuse the chroma elsewhere |
| W15 | **No spacing scale beyond Tailwind defaults** | tailwind | Means components drift; we'd benefit from explicit `--space-section`, `--space-block`, `--space-stack` tokens |

### Component coverage gap

We have these components: Button, RiskBadge, Disclaimer, BackendUnavailable, ThemeToggle, Logo. We're missing the premium-feel staples:
- Input / TextInput (we inline raw `<input>` in the form — see [generator-form.tsx](frontend/src/app/tools/annex-iv-generator/generator-form.tsx))
- Card primitive (we apply `surface-card` via class)
- Tabs (we built one inline in [schema-tool.tsx](frontend/src/app/tools/logging-schema/schema-tool.tsx))
- Toast / notification
- Tooltip
- Dialog / Modal
- Skeleton loader
- Code block (currently bare `<pre><code>`)

Each is ~30 LOC. Their absence forces ad-hoc styling that drifts.

---

## 2. The core problem (in one paragraph)

Cobalt-on-ink + grid-background + terminal-mockup-hero is the **default
aesthetic of post-2021 B2B dev infrastructure**. Vercel, Resend, Modal,
Linear (until they pivoted to magenta), Sentry, Drata, Vanta, LangSmith,
Helicone, Tinybird, Modal, Inngest — all live in this colour neighbourhood,
all ship the same hero mockup, all use the same shadcn primitives. AnnexKit
sits in this crowd by default. The cost: a prospect scanning 10 EU AI Act
compliance options can't remember which one was AnnexKit by colour or
silhouette. **Distinctiveness is not vanity here — it's recall, which is
top-of-funnel conversion.**

---

## 3. Three alternative directions

For each: palette spec (OKLCH), typography pairing, psychological impact,
reference brands, risks.

### Option A — "Editorial Engineering" ★ recommended

**Palette**
| Token | Light | Dark | Use |
|---|---|---|---|
| `--ink` | `oklch(0.18 0.02 80)` (warm ink, almost black-brown) | `oklch(0.95 0.01 80)` | Body text |
| `--cream` | `oklch(0.97 0.012 80)` (warm cream) | `oklch(0.16 0.018 80)` | Canvas |
| `--accent` | `oklch(0.55 0.13 160)` (sage / eucalyptus) | `oklch(0.72 0.14 160)` | Single accent — CTAs, links |
| `--rule` | `oklch(0 0 0 / 8%)` | `oklch(1 0 0 / 12%)` | Borders, hairlines |
| `--stamp-red` | `oklch(0.42 0.18 25)` (oxblood, "FILED" stamp) | `oklch(0.65 0.2 25)` | Risk-tier HIGH/UNACCEPTABLE only |

**Typography**
- Display: **EB Garamond Italic** (the monogram already commits to it) for hero headlines + section eyebrows
- Body: **Inter** (or keep Geist) for body + UI
- Mono: **Geist Mono** for code

**Visual cues**
- Drop "all-caps tracked" eyebrows; replace with `<em>` italic-serif eyebrows (1–2 words)
- Generous editorial whitespace (1.6× current rhythm)
- One signature: a hairline horizontal rule with italic-serif label centered on it ("§ I — Introduction"), like a printed regulation
- Risk badges become **wax-seal-style stamps**: circular, hairline border, italic-serif tier name, slight registration offset (like ink press)
- Code blocks stay dark even in light theme — printer-page contrast

**Psychology**
- "Editorial" reads as: this product produces *official artefacts*. Aligns with the literal job-to-be-done (Annex IV PDF).
- Sage green is rare in compliance space — distinguishes from Vanta (blue), Drata (purple-blue), Holistic AI (teal), Credo AI (warm orange). Reads as: calm, considered, biological (not "code-monkey aesthetic").
- Warm cream + ink reads as **archival, regulated, EU-establishment** — exactly the trust frame the buyer needs.

**Reference brands**
- *Editorial / publishing*: Substack, Lex, Are.na, The Browser Company
- *Premium tech with restraint*: Linear's typography (just typography), Stripe's marketing essays, Vercel's docs body type
- *Regulatory aesthetic*: Eur-Lex, official EU publication PDFs

**Risk**
- Could read "academic" if overdone. Mitigate by keeping interactive components (buttons, inputs) in the dev-tool register — sharp corners, dense, mono.
- EB Garamond Italic doesn't pair with every Latin character; check that French/German diacritics render correctly.

### Option B — "Instrument"

**Palette**
| Token | Light | Dark | Use |
|---|---|---|---|
| `--canvas` | `oklch(0.98 0.005 240)` (cool white) | `oklch(0.12 0.015 240)` (graphite) | Bg |
| `--ink` | `oklch(0.2 0.02 240)` | `oklch(0.94 0.005 240)` | Text |
| `--accent` | `oklch(0.7 0.18 70)` (honey amber) | `oklch(0.78 0.2 70)` | CTAs, live indicators |
| `--data-red` | `oklch(0.55 0.22 27)` | — | Errors only |
| `--rule` | `oklch(0 0 0 / 10%)` | `oklch(1 0 0 / 10%)` | Grid, table lines |

**Typography**
- Display: **JetBrains Mono / IBM Plex Mono** (yes, mono headlines)
- Body: Inter / Geist
- Numeric: Mono with tabular figures

**Visual cues**
- The product looks like a **measurement instrument** — Grafana / DataDog / Sentry's old brand
- Dense data tables, monospace headlines, amber LED-style indicators for status
- Backgrounds are tactile: subtle dotted graph paper instead of square grid
- Hero is a real dashboard with live numbers (spans, p95, error rate) — *not* a code mockup
- Buttons are sharper (radius 4px, not 8px), with monospace labels

**Psychology**
- "We measure things you can't see, accurately." Reads as serious infrastructure.
- Amber accent is unusual in this space (everyone else uses green or red for status). Memorable + dev-tool credible.

**Reference brands**
- Grafana, Datadog, Sentry (early), Tinybird, Honeycomb, Plausible, Loki/Tempo

**Risk**
- Could feel "too tool, not enough product" — the buyer is also a compliance officer who wants polish.
- Mono headlines are a strong commitment — works on hero, awkward on long-form copy.

### Option C — "Edition"

**Palette**
| Token | Light | Dark | Use |
|---|---|---|---|
| `--paper` | `oklch(0.985 0.008 60)` (warm off-white) | `oklch(0.14 0.015 60)` | Bg |
| `--ink` | `oklch(0.18 0.015 60)` | `oklch(0.93 0.008 60)` | Text |
| `--bordeaux` | `oklch(0.42 0.18 22)` (bound-leather red) | `oklch(0.65 0.2 22)` | Accent — primary CTA only |
| `--gilt` | `oklch(0.72 0.13 90)` (brass) | `oklch(0.78 0.14 90)` | Quiet accents, dividers |

**Typography**
- Display: **EB Garamond** (regular, not italic) for headlines
- Body: **Source Serif Pro** or Inter
- Mono: Geist Mono

**Visual cues**
- The product looks like a **regulated publication** — paperback book / annual report
- Two-column layouts on long-form pages
- Drop caps on the first paragraph of dense sections
- A small brass "filed" mark in the top-right of regulatory-output cards
- Hero is a still-life of a bound document, not a screen

**Psychology**
- "This is what a regulator's office would commission." Reads as gravitas + permanence.
- Bordeaux is one of the most underused accents in B2B — instantly recognisable.

**Reference brands**
- Notion (their long-form aesthetic), Stripe Atlas guides, the Penguin Modern Classics covers, EUR-Lex print editions, Lex (the case-law tool)

**Risk**
- Easy to slip into "too pretty" / "too print" — needs strong digital interaction patterns to avoid feeling like a PDF.
- Bordeaux + cream can read "wine bar" if hue drifts toward purple.

### Side-by-side — which to pick

| Axis | A: Editorial Engineering | B: Instrument | C: Edition |
|---|---|---|---|
| Differentiates from blue SaaS | ✅ strong | ✅ strong | ✅ strong |
| Honours existing logo | ✅ best | ⚠ neutral | ✅ best |
| Buyer-credible (compliance) | ✅ best | ⚠ tool-leaning | ✅ best |
| Developer-credible | ⚠ needs balance | ✅ best | ⚠ needs balance |
| Implementation effort | medium | medium | high |
| "Could you scale to 100 pages" | ✅ | ✅ | ⚠ care needed |
| Reversibility | high | high | medium |
| **My ranking** | **1** | 2 | 3 |

**Pick Option A**. It is the only direction that simultaneously
(a) leverages an asset you already paid the design cost to ship (the
monogram), (b) cleanly differentiates from the cobalt neighbourhood,
and (c) tells the buyer's brain the right story — *this product produces
documents that pass an audit*. Option B is the right answer if you reposition
AnnexKit as observability-first. Option C is the right answer if your buyer
is a public-sector procurement officer (which it isn't yet).

---

## 4. What changes (Option A — concrete)

### 4.1 Tokens (CSS variables)

Replace `--brand-cobalt`, `--brand-cobalt-bright`, `--brand-ink`, `--brand-fog` with:

```css
:root {
  --canvas: oklch(0.97 0.012 80);          /* warm cream */
  --ink: oklch(0.18 0.02 80);              /* warm near-black */
  --ink-muted: oklch(0.42 0.018 80);
  --rule: oklch(0 0 0 / 8%);
  --accent: oklch(0.55 0.13 160);          /* sage */
  --accent-bright: oklch(0.62 0.15 160);   /* hover */
  --accent-soft: oklch(0.92 0.06 160);     /* badge/chip bg */
  --stamp: oklch(0.42 0.18 25);            /* oxblood, sparingly */
}
.dark {
  --canvas: oklch(0.16 0.018 80);
  --ink: oklch(0.95 0.01 80);
  --ink-muted: oklch(0.7 0.015 80);
  --rule: oklch(1 0 0 / 12%);
  --accent: oklch(0.72 0.14 160);
  --accent-bright: oklch(0.78 0.16 160);
  --accent-soft: oklch(0.28 0.08 160);
  --stamp: oklch(0.65 0.2 25);
}
```

Map shadcn tokens (`--primary`, `--secondary`, `--background`, `--foreground`, `--ring`) onto these so existing components inherit the new language without rewrites.

### 4.2 Typography pairing

```css
@theme inline {
  --font-display: var(--font-eb-garamond);   /* already loaded for the monogram */
  --font-sans: var(--font-inter);             /* swap from Geist */
  --font-mono: var(--font-geist-mono);        /* keep */
}
```

```css
h1, h2 {
  font-family: var(--font-display);
  font-style: italic;     /* sparingly — only on h1 and section-eyebrows */
  font-weight: 500;
  letter-spacing: -0.02em;
}
```

Use italic-display only on **hero h1**, **section eyebrows** (replacing all-caps tracked), and **stamp labels** (HIGH-RISK etc.). Body text stays sans for legibility.

### 4.3 Eyebrow refresh

Replace:
```tsx
<span className="eyebrow">Free tools</span>
```

With:
```tsx
<span className="font-display italic text-sm text-[var(--accent)]">
  § Free tools
</span>
```

Effect: pages look authored by an editor, not bullet-pointed by a marketer.

### 4.4 Buttons

Sharpen radius from `rounded-md` (6px) to `rounded` (4px). Primary becomes sage-on-cream with a slight ink-shadow inset (looks letterpressed). Hover lifts 1px AND deepens accent saturation. Add an invisible focus underline that animates in (no rectangle ring).

### 4.5 Cards

Drop the multi-stop shadow on `surface-card`; replace with a single hairline rule above + below, slightly inset from the bg. Cards read as *clippings* on the editorial page, not floating panels. Hover: rule darkens 30%, no lift.

### 4.6 Risk-tier badges → stamps

```tsx
<span className="
  inline-flex items-center justify-center
  rounded-full border border-[var(--stamp)]
  px-3 py-1
  font-display italic text-[var(--stamp)]
  text-xs
  rotate-[-2deg]
">
  HIGH RISK
</span>
```

The slight `rotate(-2deg)` is the signature — looks like a press-stamped certificate. Use only for HIGH and UNACCEPTABLE. LIMITED/MINIMAL keep current quiet badges.

### 4.7 Hero recomposition

Out: cobalt brand-wash + terminal-window code mockup + huge sans h1.

In:
- Cream canvas (or deep ink, depending on theme)
- Headline in EB Garamond Italic, e.g. *"Audit-ready Annex IV docs from your LLM telemetry."* with the italic-serif treatment carrying the gravitas
- Below the headline: a **two-column** layout — left is the snippet (still code-block, but **printed on white** like a regulation excerpt), right is a thumbnail of the generated PDF (real, rotated 2°, with a sage paperclip detail)
- Beneath: 2 CTAs, primary sage solid, secondary outlined ink
- No background gradient. The whitespace IS the design

This single change is what visually separates AnnexKit from every other dev-tool landing.

### 4.8 Section transitions

Replace section bg-color flips with a **horizontal hairline + italic-serif section number**:

```
                              § II — How it works
                              ───────────────────
```

Each section is announced like a chapter. Rhythm reads "this is a long-form pitch", not "this is a card carousel".

### 4.9 Motion language

Pick ONE signature interaction:
- On scroll, the hero PDF thumbnail unrotates gently (CSS scroll-driven animation, no JS)
- All accent-coloured CTAs have a 200ms underline that scribes in on hover (svg path-length animation)
- Page transitions: 80ms fade only, no slide

Avoid Framer-style parallax / 3D / gradient meshes. Restraint *is* the signature.

### 4.10 Code blocks

Style them like **printed monospace excerpts**:
- Cream background (even in dark theme — the code sample is "an excerpt" in both)
- Hairline top + bottom rule, italic-serif caption above (`§ snippet — loan_screener.py`)
- Line numbers in `--ink-muted`, no syntax highlighting on marketing — let the code be the texture
- On hover: a faint sage underline appears under copy-paste-friendly identifiers (function names)

---

## 5. Page-by-page review

| Page | Current state | After Option A |
|---|---|---|
| `/` (homepage) | 9-section vertical scroll, cobalt hero, terminal mockup | Editorial hero with serif italic h1 + sample PDF thumb. § section markers between blocks. Trust preview becomes a clipped excerpt of a real trust page (rotated 1°) |
| `/tools` | Hub with 3 cards | Keep structure, swap eyebrow + add a sage thin hairline above "THE TOOLS" label. Cards become clippings (hairline-rule cards). Final CTA: cream paper, sage CTA |
| `/tools/annex-iv-generator` | 7-section form | Form sections become Annex-IV-styled (`§ 1. What does the system do?` italic-serif). Submit button is the only sage element on the page until success |
| `/tools/logging-schema` | Download cards + tabs + table | Tabs become italic-serif chapter labels. Field reference table gets a top hairline + tabular-numeric column. Code samples on cream |
| `/demo/annex-iv` | 3 scenario cards | Each card becomes a real PDF-cover thumbnail (rotated, with tier stamp top-right). The "Open PDF" button stays sage. Adds a "see what's inside" section showing the actual §1.x table rendered HTML-side |
| `/pricing` | 3 tiers | Replace highlight glow with a top-right brass corner-fold on the Pro tier (looks like a bookmark). Tier names in italic-serif. No "early access" badge — just a footnote in the page-bottom |
| `/trust/[slug]` | Tier breakdown + system list | Becomes a regulator-style page: the tenant name in italic-serif, systems listed as a numbered table (`§ 1. customer-support-bot`), risk badges as small stamps |
| `/trust/[slug]/systems/[id]` | Detail view | Render as a one-column "page proof" — generous side margins, drop cap on §1, tier stamp top-right corner |
| Legal pages (`/privacy`, `/terms`, `/imprint`, `/cookies`) | Default styled | The editorial direction shines here — long-form serif body, italic section numbers, generous leading |

---

## 6. Implementation roadmap

### 6.1 Quick wins — 2 days, NO palette change

These improve perceived quality even if you reject Option A.

1. **Mobile nav drawer** (`site-header.tsx`) — current header collides below md. ~3h
2. **Active-page indicator** in nav links (`site-header.tsx`) — underline current route. ~30min
3. **CTA hierarchy escalation** — hero "Get started → pricing"; final-cta becomes "Talk to the founder → mailto" so they don't compete. ~1h
4. **Risk-tier swatches → OKLCH** ([globals.css:66-75](frontend/src/app/globals.css#L66)) — for consistency with the rest of the system. ~30min
5. **`focus-visible` brand cue** — replace generic ring with an underline-style affordance. ~1h
6. **Code-panel polish** — tighten line-height, add a copy button, real syntax highlighting via Shiki at build time. ~3h
7. **Footer column alignment** — current 5-column grid has uneven rhythm at lg breakpoint. ~1h
8. **Skeleton loaders** on `/demo` and `/tools` while fetching from backend. ~2h
9. **`<Input>` and `<Card>` primitives** — extract from the inline form + cards, prevent style drift. ~2h
10. **JSON-LD on every page** — currently only `/tools` has it. Add to `/pricing`, `/demo/*`, `/tools/*` (BreadcrumbList minimum). ~1h

### 6.2 Medium — 5–7 days, with Option A palette swap

1. **Token swap** — replace cobalt with sage, ink with warm-ink, cream canvas (Tailwind 4 `@theme` block, 1 commit, fully reversible). ~3h
2. **Typography pairing** — load EB Garamond from Google Fonts via `next/font`; map to `--font-display`. ~1h
3. **Heading + eyebrow refresh** — italic-serif `§` markers replace all-caps tracked. Sweep across all pages. ~4h
4. **Card refactor** — `surface-card` becomes "clipping" (hairline rules instead of shadow). ~2h
5. **Button refresh** — sharpen radius, sage primary, focus underline. ~2h
6. **Hero recomposition** — 2-col with PDF thumb + cream background. ~6h
7. **Section dividers** — italic-serif chapter markers between landing sections. ~3h
8. **Risk-stamp component** — replace `RiskBadge` for HIGH/UNACCEPTABLE only. ~3h
9. **Code-block redesign** — cream-in-dark printed-excerpt aesthetic + Shiki syntax. ~4h
10. **Light theme polish** — graduate light from "secondary citizen" to first-class. ~4h
11. **Trust-page restyle** — page-proof layout. ~6h

### 6.3 Advanced — 1–2 weeks

1. **Motion language** — scroll-driven hero animation + signature underline interaction. ~1d
2. **`/demo/annex-iv` interactive** — embed an actual PDF preview iframe with a sidebar showing the AnnexIVContext data driving each section. ~2d
3. **Cmd-K command bar** (Linear-style) — search across tools, pricing, docs, trust slugs. ~1.5d
4. **Section "chapter" navigation** on long pages — sticky right-side TOC like Stripe docs. ~1d
5. **Editorial blog template** for the upcoming 8 posts (Phase 3) — drop caps, generous margins, footnotes. ~1d
6. **A real "look inside the PDF" tour** on /tools/annex-iv-generator — sample answers prepopulate the form sections one at a time, with the generated PDF preview updating live. ~2d
7. **OG image generation per page** with the italic-serif logo + page title (Next.js `opengraph-image.tsx` per route). ~1d
8. **Storybook for the new component system** so the next developer doesn't drift back to generic patterns. ~2d

### 6.4 Anti-patterns to avoid

- Glassmorphism. It peaked in 2021 and reads as "watered-down Apple". Editorial direction doesn't need it.
- Gradient meshes. Stripe's gradient is theirs; everyone else's looks like a Figma plugin output.
- Animated illustration mascots / 3D objects. The product is regulation. Mascots = trust loss.
- Dark mode at every cost. Light mode is part of the editorial proposition. Half your buyers will browse in daylight.
- Buttons with "shine" or "shimmer" hovers. Reads as crypto-app, not compliance.
- Carousels. If content is worth seeing, it's worth stacking vertically.
- Custom scrollbars. Always feel laggy in some browser. Skip.
- Lottie animations on the hero. The hero loads in 80ms; an animation is friction.

---

## 7. Order of execution (if you say "vai")

```
Day 1   — Section 6.1 quick wins (1–10)
          Token swap to Option A (Section 6.2 step 1+2)
          Typography pairing live
Day 2   — Heading + eyebrow sweep (6.2 step 3)
          Card refactor (6.2 step 4)
          Button refresh (6.2 step 5)
Day 3   — Hero recomposition (6.2 step 6)
          Section dividers (6.2 step 7)
Day 4   — Risk stamps (6.2 step 8)
          Code block redesign (6.2 step 9)
Day 5   — Light theme polish (6.2 step 10)
          Trust pages restyle (6.2 step 11)
Day 6   — Section 6.3 motion language
Day 7+  — 6.3 advanced (pick top 2–3, defer the rest)
```

After day 5, the public site reads as a different product. After day 7, it
reads as a *premium* product nobody can mistake for shadcn-default SaaS.

**Reversibility plan**: every step is a separate commit. If a step doesn't
land well in your eye, revert just that commit; the rest holds. The token
swap is the only "all-or-nothing" — but it's a 1-file change and fully
revertable.

---

## 8. What I won't recommend

To prove this isn't generic advice:

- **No glassmorphism.** See §6.4.
- **No moving the brand to a "warmer" cobalt.** That's interior decoration on the same problem.
- **No Lottie / 3D / WebGL hero.** Performance + brand-fit wrong.
- **No subscribing to a design-system-as-a-service.** Linear, Catalyst, Tremor — they're good but you'd inherit their voice. AnnexKit's voice is the differentiator.
- **No swapping Tailwind for CSS-in-JS / Panda / vanilla-extract.** Tailwind 4 + tokens is enough; the bottleneck is design decisions, not tooling.
- **No replacing the monogram.** It's the single most ownable thing you have. Build the rest around it.

---

## 9. Closing

You're closer to a distinctive product than you think. The codebase already
honours editorial typography (heading tracking, tabular figures, the
monogram). The cobalt-and-grid choices were correct early-stage defaults —
they're now the ceiling.

Pick **Option A**, give me a day, and the site stops looking like a
"shadcn-default startup" and starts looking like *the* product that takes
EU AI Act compliance seriously enough to produce documents that read like
official records.

— end —
