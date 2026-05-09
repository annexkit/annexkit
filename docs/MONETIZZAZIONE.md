# AnnexKit — Piano monetizzazione (analisi onesta)

> Questo è il documento più importante che leggerai su AnnexKit.
> Niente cheerleading. Numeri specifici, probabilità onesti, scenari
> realistici. Se dopo aver letto questo decidi di NON investire altri
> 6 mesi nel prodotto, è un investimento di tempo che ti ho già fatto
> risparmiare.

---

## La verità che voglio dire all'inizio

Prima ancora del piano:

**1. AnnexKit non è un'idea da unicorno.** Probabilità di diventare
una company da $100M ARR in 5 anni: <2%. Probabilità di diventare un
*lifestyle business sostenibile* a $10-30K MRR in 18-24 mesi: ~40%.
Probabilità di flame-out (founder burnout, MRR <$500): ~30-40%.

**2. È un ottimo "secondo prodotto" o "consulting upsell"**. Se hai
già un income stream stabile (consulting, day job, secondo SaaS),
AnnexKit può essere un add-on profittevole con bassa probabilità di
distruggerti finanziariamente. Se invece è il TUO unico income:
serve un piano di sopravvivenza per i primi 12 mesi.

**3. Il mercato è REALE ma il timing è critico**. L'AI Act enforcement
piena è ad agosto 2026. Quel mese (e i 6-9 successivi) saranno il
picco di domanda. Fuori da quella finestra, la domanda esiste ma è
più tiepida.

**4. La concorrenza arriverà**. LangSmith, Langfuse, Confident AI
hanno 12-24 mesi prima che capiscano l'opportunità e shippino un loro
modulo "AI Act compliance". Devi essere il marchio di default in
quella finestra.

**5. Solo founder è sostenibile fino a $10K MRR**. Oltre, devi
assumere o burn-out. Non c'è founder eroico che scala da solo a $50K
MRR senza co-founder o team.

Procedi solo se accetti queste premesse.

---

## 1. Il mercato (TAM/SAM/SOM)

Le stime sotto sono basate su dati pubblici (Eurostat, EU Commission,
McKinsey EU AI Survey 2025). I numeri sono indicativi entro ±30%.

### 1.1 TAM — Total Addressable Market

| Bucket | Stima |
|---|---|
| Aziende UE con almeno un dipendente | ~24.000.000 |
| Aziende UE che usano qualche AI in prod (2026) | ~500.000 |
| ...di cui in categorie Annex III high-risk | ~50.000 (10%) |
| ...disposte a pagare per compliance tooling | ~25.000 (50%) |
| **TAM annuo a €500/cliente blended** | **~€12.5M** |

Il "blended €500/cliente" è una media tra i tier (Free $0, Pro $588/anno,
Team $2.388/anno, Enterprise €5K/anno). Realisticamente:
$0 × 0.7 + $588 × 0.2 + $2,388 × 0.08 + $5,000 × 0.02 ≈ $410.

### 1.2 SAM — Serviceable Addressable Market

Restringi al mercato che ANNEXKIT può realisticamente servire nei
prossimi 18 mesi:

- **Geografia**: Italia + DACH (Germania-Austria-Svizzera) +
  UK + Nordics. Approssimativamente il 50% del TAM EU.
- **Stack tecnologico**: aziende che usano Python/JS in prod e
  capiscono `pip install` (vs aziende che hanno solo SAP/Oracle).
  Approssimativamente il 30% di quelle compliance-aware.
- **Maturità AI**: aziende con LLM in prod, non solo "ChatGPT
  occasionalmente per email". Approssimativamente il 40%.

| Cosa | %TAM | Aziende |
|---|---|---|
| Geografia (IT/DACH/UK/Nordics) | 50% | 12.500 |
| × Stack dev-friendly | × 30% | 3.750 |
| × Maturità AI in prod | × 40% | 1.500 |
| **SAM** | **~6%** | **~1.500 aziende** |

A €500 blended: SAM annuo ≈ **€750K**.

### 1.3 SOM — Serviceable Obtainable Market

Quanto puoi realisticamente catturare anno per anno:

| Anno | % SAM catturato | Paying customers | ARR |
|---|---|---|---|
| Anno 1 | 1.5-3% | 25-50 | $15-30K |
| Anno 2 | 5-10% | 75-150 | $45-90K |
| Anno 3 | 12-20% | 180-300 | $110-180K |

Numeri da micro-SaaS, non da unicorno. Confronta con i benchmarks:

- 70% dei micro-SaaS sono sotto $500/mese MRR (~$6K ARR) ([SaaSRanger 2024](https://saasranger.com/blog/micro-saas-revenue-reality-what-1000-founders-actually-earn/))
- Mediana time-to-$1K MRR: 12-18 mesi per indie founders eseguiti bene ([Indie Hackers](https://www.indiehackers.com/post/if-i-had-to-start-a-saas-from-scratch-in-2025-i-d-do-this-1b828afc53))
- 75% dei SaaS che hanno toccato $1M ARR nel 2024 erano bootstrapped ([SoftwareSeni](https://www.softwareseni.com/solo-founder-saas-metrics-from-0-to-10k-mrr-in-6-months-with-realistic-timelines/))
- Vertical AI tools convertono 5-15% (vs 1-3% horizontal) — **questo è
  il dato che ci aiuta**: AnnexKit è verticale, non orizzontale.

---

## 2. Pricing tier (recap + razionale)

### 2.1 Free — $0

- 100K spans/mese
- 1 sistema dichiarato
- 1 utente
- SDK MIT (open-source, self-hostable)
- Annex IV markdown only (no PDF)
- Niente trust center pubblico

**Razionale**: leverage marketing + SEO. Costo per utente: ~$0
(infra ammortizzata, non chiama Mistral, niente PDF rendering).

**Conversion expected**: 5-10% di Free → Pro entro 6 mesi.

### 2.2 Pro — $49/mese

- 5M spans/mese
- 10 sistemi dichiarati
- 3 utenti
- Annex IV PDF + markdown
- Trust center pubblico abilitato
- Email support (best-effort, 48h)

**Target customer**: indie dev italiano/europeo, scaleup early-stage,
freelance compliance officer, agency che serve clienti SME.

**ARPU annuo**: $49 × 12 = **$588/anno**.

**Pricing reasoning**: $49 è il sweet spot per "metto la carta e
basta", senza approval del CFO. Sotto-$100 è il classic indie SaaS
self-serve threshold.

### 2.3 Team — $199/mese

- 50M spans/mese
- Sistemi unlimited
- 10 utenti, SSO (Google/GitHub)
- Audit log retention 7 anni (Article 18 obbligo)
- SLA 99.5%, priority email support (24h)
- Annex IV PDF firma digitale (M3)

**Target customer**: scaleup Series A-B, mid-market 50-500 dipendenti.

**ARPU annuo**: $199 × 12 = **$2.388/anno**.

**Pricing reasoning**: questo è il tier dove arriva il decisore IT
Manager / CTO. $200 è "dietro al free trial dell'employee", non chiede
budget approval ricorsivo.

### 2.4 Enterprise self-hosted — €5.000/anno

- Helm chart per Kubernetes
- License check periodica
- Custom contract terms (DPA, SLA bespoke)
- Dedicated Slack/Teams channel
- Onboarding 1:1
- Roadmap influence (priority feature requests)

**Target customer**: banche, assicurazioni, fintech, healthcare —
regulated industries che NON possono comprare SaaS multi-tenant per
policy.

**ARPU annuo**: €5.000.

**Costo di acquisizione**: alto (1-3 mesi sales cycle, demo, security
review). Vendiamo **solo** quando inbound, mai outbound. Il break-even
è ~3 clienti enterprise per giustificare 20% del tempo founder
sull'enterprise sales.

### 2.5 Mix realistico anno 1

| Tier | % paying | Monthly revenue per customer | Contribution |
|---|---|---|---|
| Pro $49 | 70% | $49 | 70% × 49 = $34/avg |
| Team $199 | 25% | $199 | 25% × 199 = $50/avg |
| Enterprise €5K/yr | 5% | $416/mese ammortizzato | 5% × 416 = $21/avg |
| **Blended ARPU** | | | **~$105/mese paying** |

Quindi: 50 paying clienti = $5.250 MRR ≈ **$63K ARR**.

---

## 3. Go-to-market — canali specifici con numeri

Ogni canale qui ha un costo (in tempo o euro), un tempo di "ramp", e
un'aspettativa realistica di lead qualificati. Sono numeri da
benchmark, non da garanzia.

### 3.1 GitHub stars + topic SEO ★ canale principale

**Costo**: $0 (oltre tempo).

**Ramp**: 6-12 mesi compounding.

**Tactics**:
- Topic GitHub `ai-act` (oggi <100 repo seri) — saturare con quality
- README ottimizzato per discovery interno (badge, hero, gif)
- Contributor-magnetic: rispondi a issue in <24h, accept first-PRs
  con grazia

**Aspettativa numerica**:
- M1 launch: 100-300 stars
- M3: 500-800 stars
- M6: 1.000-2.000 stars
- M12: 3.000-5.000 stars

**Conversion**: ~1-2% di star → sign-up entro 30 giorni del view.
3.000 stars × 1.5% = ~45 sign-up cumulativi. Di cui ~5-10% paying.
**Yield M12: ~3-5 paying customers.**

### 3.2 Hacker News ★ catalyst single-shot

**Costo**: $0.

**Ramp**: 1 evento, day 0 dell'effetto.

**Tactics**:
- Titolo specifico: "Show HN: AnnexKit – an OpenTelemetry-style
  collector for the EU AI Act"
- Demo video 90s pre-registrato con `make demo-seed`
- 10 FAQ pre-stampate per i primi commenti (latency, privacy,
  pricing, comparison vs LangSmith)
- Postare martedì mattina UTC 14:00 (post-pranzo US, mid-day EU)

**Aspettativa numerica**:
- Front page (top 10): ~30% di probabilità con prep accurato
- Visitors se in front page: 3K-10K visitors in 48h
- Sign-up rate: ~3-5% di visitors → 90-500 sign-up
- Paying conversion: ~2-3% di sign-up → 2-15 paying

**Yield M1 da HN: 2-15 paying customers in un colpo.**

### 3.3 Reddit + dev forums

**Costo**: $0 (tempo).

**Tactics**:
- r/MachineLearning, r/LocalLLaMA, r/europrivacy, r/programming
- 1 post ogni 2-3 settimane, sempre con valore aggiunto
- Mai "promo" puro — sempre risolvere un dubbio degli altri prima

**Aspettativa numerica**:
- 1 post buono = 5-30 sign-up
- 1 post mediocre = 0-5 sign-up
- Frequenza realistica: 2 post/mese
- **Yield mensile a M3+: ~10-30 sign-up, 1-3 paying**

### 3.4 SEO long-tail ★ strategico, ramp lento

**Costo**: $0 (tempo).

**Ramp**: 6-9 mesi prima di scalare (Google SEO è lento per nuovi domini).

**Tactics**: 1 articolo/settimana per 6 mesi su keyword bassa
concorrenza:
- "Annex IV template"
- "Article 12 AI Act logging requirements"
- "EU AI Act technical documentation example"
- "Annex III categories list"
- "documentazione tecnica AI Act italiano"
- "AI Act compliance for developers"

**Aspettativa numerica**:
- M6: 1K-2K visitors organici/mese
- M9: 2K-5K visitors organici/mese
- M12: 5K-10K visitors organici/mese
- Conversion rate visitors → sign-up: ~2%
- **Yield M12: 100-200 sign-up/mese da SEO, ~10-20 paying/mese**

Questo è il canale più sostenibile a lungo termine.

### 3.5 Italian dev communities

**Costo**: €1.000-3.000/anno (sponsorship).

**Communities**:
- GrUSP (conferenze frontend IT, 2/anno)
- Avanscoperta (workshop tecnici)
- Schrödinger Hat (conf indipendente)
- Continuous Delivery podcast
- Italian Python User Group

**Aspettativa numerica**:
- 1 evento ben fatto (talk + booth + sponsorship): 30-100 hot leads
- Conversion: 5-10% → 3-10 paying customers
- **Yield M12 da 4 eventi: 20-40 paying customers**

Questo è il canale più mirato al beachhead italiano.

### 3.6 LinkedIn content marketing

**Costo**: $0 (tempo founder).

**Ramp**: 6 mesi prima che diventi consistent.

**Tactics**:
- 3 post/sett tecnici (no fluff, niente "5 lessons learned")
- 1 post "behind the scenes" / settimana
- Risposta a ogni commento entro 4h
- Tag persone rilevanti senza essere spammoso

**Aspettativa numerica**:
- M3: 200 followers
- M6: 800 followers
- M12: 2.500 followers
- DM inbound: ~1-3/settimana
- **Yield M12: 5-10 paying customers**

### 3.7 Newsletters (free PR)

**Costo**: $0 (pitching).

**Target**: TLDR, Bytes, Console.dev, JavaScript Weekly, Pycoder's
Weekly, EU Privacy Now.

**Tactics**: pitch via Twitter DM o email a chi cura la newsletter,
1 mention = 500-2.000 visitors.

**Aspettativa numerica**:
- 2 mentions/anno realisticamente
- 3.000 visitors burst per mention
- Conversion: ~3% sign-up → 90 sign-up per mention
- **Yield M12 da 2 newsletters: 4-10 paying customers**

### 3.8 Partnership con commercialisti italiani ★ ad alto leverage, slow

**Costo**: 20% revenue share su clienti referrali.

**Ramp**: 6-12 mesi per setup primo partnership.

**Tactics**:
- Conferenze ANC / ODCEC (Ordine dei Commercialisti)
- Inbound a 50 studi target via email + LinkedIn
- 1 studio = 5-20 PMI clienti con bisogni AI Act

**Aspettativa numerica**:
- 1 studio attivo a M6 = 5-15 paying customers
- 3 studi attivi a M12 = 20-50 paying customers
- **Yield M12 da partnerships: 20-50 paying customers, alto value
  perché blended ARPU sale (i clienti studi tendono Team tier)**

### 3.9 Paid advertising (sconsigliato fino a $5K MRR)

**Costo**: $500-2.000/mese.

**Tactics**: Google Ads su "AI Act compliance", "Annex IV template",
"EU AI Act documentation".

**Aspettativa numerica**:
- CAC stimato €50-200 per click qualificato
- Conversion click → sign-up: ~5%
- Conversion sign-up → paying: ~3%
- CAC per paying customer: €50-200 ÷ 0.05 ÷ 0.03 = **€33K-133K per
  customer**. Inutilizzabile finché non hai economics provate.

**Verdict**: skip fino a $5K MRR organico, poi sperimenta su 1
keyword specifica.

### 3.10 Riepilogo yield M12

Sommando i canali realisticamente:

| Canale | Yield M12 |
|---|---|
| GitHub + SEO compounding | 8-15 paying |
| HN single launch | 2-15 paying |
| Reddit ricorrente | 10-25 paying |
| Italian communities (sponsorship) | 20-40 paying |
| LinkedIn content | 5-10 paying |
| Newsletters | 4-10 paying |
| Partnerships commercialisti | 20-50 paying |
| **Totale stimato M12** | **70-165 paying** |

Con blended ARPU $105/mese: **$7.350-$17.300 MRR a M12 nel range
realistico**.

Allinea con base case più sotto.

---

## 4. Proiezioni finanziarie (3 scenari)

### 4.1 Bear case (probabilità ~30%)

| Mese | MRR | Paying | Note |
|---|---|---|---|
| M1 | $0 | 0 | Launch ok ma flat |
| M3 | $200 | 4-5 | HN andato male |
| M6 | $500 | 10-12 | Slow growth |
| M12 | $1.000 | 20-25 | Founder burnout looming |
| Anno 2 | Stuck $1K | | Pivot o quit |

**Cosa fare se sei qui a M9**: ammettilo. Ripiega su consulting con il
codebase ("offri AI Act compliance audit a €3-5K una tantum") usando
AnnexKit come tool interno. Trasforma il prodotto in un asset di un
pivot.

### 4.2 Base case (probabilità ~50%)

| Mese | MRR | Paying | Note |
|---|---|---|---|
| M1 | $200 | 4 | HN ok |
| M3 | $800 | 16 | Reddit + GitHub starting |
| M6 | $2.000 | 40 | First case study |
| M9 | $3.500 | 70 | First commercialista partner |
| M12 | $5.500 | 110 | Sostenibile |
| Anno 2 | $12-18K MRR | 250-350 | Hire DevRel a $15K |
| Anno 3 | $25-35K MRR | 500-700 | Profitable, decisione: vendere o scale |

**Costi tuoi a M12**: hosting Hetzner $50/mese + Mistral API $200/mese
+ dominio $10/mese ≈ $260/mese. **Margine: ~95%**.

**Salary founder a M12**: con $5.5K MRR, puoi pagarti €40-50K/anno.
Sotto-mercato per Milano dev senior, ma sostenibile se non hai mutuo
+ figli.

### 4.3 Bull case (probabilità ~15-20%)

| Mese | MRR | Paying | Note |
|---|---|---|---|
| M1 | $1.500 | 30 | HN front page top-3 |
| M3 | $4.000 | 80 | Word of mouth |
| M6 | $10K | 200 | Press coverage (Tech.eu, EU-Startups) |
| M9 | $18K | 360 | TS/JS SDK live, US adoption |
| M12 | $25-30K | 500-600 | Pre-seed conversation |
| Anno 2 | $80-100K MRR | 1.5-2K | Series A ready |
| Anno 3 | $200K+ MRR | | Acquired or scale |

**Probabilità di hit del bull case in modo specifico**: 5%. Più
realistico è "una versione attenuata del bull case" al 15%.

### 4.4 Cost structure (tu come solo founder)

Breakdown mensile a $5K MRR:

| Voce | Costo |
|---|---|
| Hetzner CX21 (1 vCPU 4GB) | €5/mese |
| Hetzner CCX13 backup (2 vCPU 8GB) | €15/mese |
| Cloudflare Pro | €0 (free tier) |
| Mistral API budget | €100-300/mese |
| Domain + email | €10/mese |
| GitHub Pro + Vercel + npm | €0 (free tiers) |
| Email transactional (Brevo) | €0 (free tier <300 mail/day) |
| Stripe fee | ~3% del MRR ≈ $150/mese a $5K MRR |
| **Totale infra** | **~€250-500/mese** |
| **Margine lordo** | **90-95%** |

A $5K MRR: **net cash $4.5K-4.7K/mese al founder pre-tax**.

---

## 5. Cosa potrebbe andare storto (rischi onesti)

| Rischio | Probabilità | Mitigazione |
|---|---|---|
| **LangSmith / Langfuse aggiunge AI Act module** | 60% in 12 mesi | Vai veloce, brand "AI Act-first", open-source community è copia-resistant |
| **Credo AI / Holistic AI scendono di prezzo** | 30% | Cultural ground (dev-first) inattaccabile per loro |
| **AI Act enforcement watered down** | 20% | Prodotto serve anche per SOC2 evidence, NIS2, internal audit |
| **Italian SMEs non comprano fino a sanzione** | 50% | Beachhead = scaleup DACH/UK/Nordics |
| **Mistral / Anthropic ship compliance toolkit** | 25% | Noi platform-agnostic, loro sono provider-locked |
| **Founder burnout** | 40% | Time-box 30h/sett, batch routine, no perfectionism |
| **Customer churn dopo PDF singolo (one-and-done)** | 50% | Article 72 post-market monitoring forza traccia continua + cumulative pricing |
| **Auditor reali rifiutano il PDF** | 20% | Partnership con 1-2 studi legali per blessing template + gap analysis explicit |
| **Postgres / Hetzner downtime imbarazzante** | 15% | Health checks + cold standby M6, multi-region M12 |
| **GDPR / DPA chiede modifiche sostanziali** | 10% | Already EU-hosted, privacy-by-default, audit log immutable — basso rischio |
| **Concorrente OSS aggressivo (fork di Langfuse con AI Act)** | 20% | Open-core community + integrazioni difficili da copiare |

**Worst case che NON puoi mitigare**: il regolatore EU posticipa di 18
mesi l'enforcement → la tua finestra di urgency commerciale si chiude.
Probabilità: ~15%. Mitigation: vendi anche per Article 6 (NIS2),
Annex I (Cyber Resilience Act), Article 9 ISO 42001 voluntary.

---

## 6. Piano 30/60/90/180 giorni — concreto

### 6.1 Giorni 1-30 (Mese 1) — Soft launch

Goal: pubblicare l'esistenza del prodotto al mondo.

**Setup user-side (4-6 ore tot)**:
- [ ] Compra dominio `annexkit.dev` su Cloudflare Registrar (10 min, ~€10/anno)
- [ ] Registra account PyPI con 2FA (5 min)
- [ ] `cd sdk && uv build && uv publish` per `annexkit==0.1.0` (5 min)
- [ ] Hetzner Cloud signup (€20 free credit), crea CX21 a €5/mese (10 min)
- [ ] Cloudflare DNS + SSL gratis (15 min)
- [ ] SSH al VPS, install Docker, `docker compose up -d` (30 min)
- [ ] Verifica: `https://annexkit.dev` → trust center risponde
- [ ] Verifica: `pip install annexkit` da PyPI funziona

**Marketing (2-3 giorni di lavoro)**:
- [ ] Demo video 90s con OBS (1h registrazione, 2h editing)
- [ ] Landing page Vercel free tier (4-6h, riusa l'UI Next.js)
- [ ] Show HN draft + post martedì 14:00 UTC
- [ ] LinkedIn launch post + tag 10 amici dev
- [ ] First Reddit post r/MachineLearning

**Target M1**: 100-300 GitHub stars · 5-15 sign-up · 1-3 paying · $50-150 MRR

### 6.2 Giorni 31-60 (Mese 2) — First customer call

Goal: parlare con i primi clienti, capire se il prodotto ha vero
product-market-fit.

- [ ] Calendly 30min slot per ogni sign-up (anche free)
- [ ] First case study scritta (chiedi al primo paying se può essere
      pubblico)
- [ ] Mistral advisor (Day 4.5 deferred): suggerisce categorie ambigue
- [ ] LangChain integration: decorator wrapper che intercetta `LLMChain`
- [ ] Rate limiting su `/api/v1/trust/*` con `slowapi`
- [ ] Newsletter pitch: TLDR Italy, Bytes, Console.dev
- [ ] First commercialista contact via ANC LinkedIn

**Target M2**: 25-50 sign-up · 5-15 paying · $300-1.000 MRR

### 6.3 Giorni 61-90 (Mese 3) — Productize

Goal: chiudere i gap che i clienti chiedono. Non aggiungere features
nuove.

- [ ] TS/JS SDK port (basic decorator wrapper)
- [ ] Trust badge embeddable: `<script src="annexkit.dev/badge.js">`
- [ ] Public Annex IV download endpoint (redacted)
- [ ] CI workflows GitHub Actions
- [ ] Conference talk submission: PyConIT, EuroPython, FOSDEM
- [ ] Refine pricing: se Pro $49 si converte poco, considera $39 o
      gestione "Starter" gratuita per primi 60 giorni

**Target M3**: 50-100 sign-up · 20-40 paying · $1.000-2.500 MRR

### 6.4 Giorni 91-180 (Mese 4-6) — Scale o pivot

Goal: decidere se andare avanti, raise pre-seed, o ripiegare.

- [ ] Konformia consumer dashboard (italiano, FAQ italiana)
- [ ] Multi-tenancy hardening (SSO, audit retention 7 anni)
- [ ] Self-hosted enterprise tier (Helm chart)
- [ ] 1-2 partnership commercialisti italiani con revenue share 20%
- [ ] Frontend test suite (Vitest)
- [ ] M6 review: $3K-5K MRR? scale. <$1K MRR? pivot/quit.

**Target M6**: $3.000-5.000 MRR, 60-100 paying customers

---

## 7. Exit options (onesti)

### 7.1 Lifestyle business (più probabile, 50%)

**Cosa**: $10-30K MRR sostenibile, founder full-salary + 1 part-time
hire, esce 5-10 anni a $1-3M revenue cumulativo. Niente IPO, niente
acquisition fancy. È **un buon outcome** per un solo founder.

**Quando**: a M18-M24 hai $10-15K MRR stable con churn <3%/mese.

### 7.2 Acquisition by compliance player (20%)

**Cosa**: Vanta, Drata, Tugboat Logic, OneTrust comprano per $1-5M.
Tipico multiplo: 5-10x ARR.

**Quando**: a M18-M30 con $200-500K ARR.

**Cosa significa per te**: $300K-500K netti dopo tasse, mantieni
qualche % equity rolled into l'acquirer, lavori 12-24 mesi come
"AnnexKit team lead". Non è ricchezza ma è un buon outcome.

### 7.3 Acquisition by infrastructure player (15%)

**Cosa**: LangSmith, Langfuse, Confident AI, Mistral comprano per
"strategic" — più un acqui-hire che un acquisto valuation-driven.

**Quando**: M12-M18 con $50-200K ARR.

**Tipico**: $300-800K all-in (cash + stock vesting). Inferiore al
compliance acquirer ma più rapido + meno requirements.

### 7.4 Scale to real company (long shot, 10%)

**Cosa**: raise $1-2M seed a valuation $10-15M, runway 18 mesi, hire
4-6 persone, scale a $1M ARR, raise Series A.

**Quando**: M9-M12 con $20K MRR + crescita >40%/mese.

**Probabilità realistica nel mercato 2026 EU**: 10%. Compete con
fund che chiedono $1M ARR per Series A pre-money.

### 7.5 Open-source famous (15%)

**Cosa**: il backend AGPL diventa lo standard de-facto per
self-hosted compliance. Mantieni "managed cloud" come tier premium.
"PostgreSQL of AI compliance".

**Quando**: M18-M36 con community attiva + 5K+ GitHub stars.

**Tipico revenue**: $30-100K MRR sostenibile, vita lunga.

### 7.6 Close shop (15%)

**Cosa**: il prodotto non scala oltre $1-2K MRR e tu hai bisogno di
un income vero. Vendi il dominio + IP a un compliance consultant per
$10-30K e torni a un day job.

**Mai vergognarsi**: 70% delle startup chiudono nei primi 24 mesi.
Riconoscere il momento della chiusura è una skill, non un fallimento.

---

## 8. Mia raccomandazione (opinionata)

Procedi. Con questi vincoli rigorosi:

1. **Time-box il bootstrap a 12 mesi.** Se a M12 sei sotto $3K MRR
   con crescita <30%/mese, ammettilo: ripiega a consulting con il
   codebase o fai pivot. Non costruire una zombie startup.

2. **Solo founder è sostenibile fino a $10K MRR.** Oltre, devi
   assumere o vendere/exit. Niente founder eroico per 24 mesi
   straight.

3. **Beachhead = scaleup tedesche/UK/Nordics, NON Italian SMEs
   all'inizio.** Le SME italiane non comprano fino a sanzione. Le
   scaleup DACH/UK/Nordics comprano oggi per "due diligence per
   il prossimo round" o per "vendere a banche enterprise".

4. **Non aggiungere features finché non hai 50 paying customers.**
   Ogni feature è un tax sul codebase. Doubling down su quello che
   c'è già: TS SDK, LangChain integration, trust badge embeddable.

5. **Lancio HN va fatto BENE.** Hai 1 sola opportunità credibile.
   Prepara titolo + demo video + 10 FAQ pre-stampate per i first 10
   commenti. Posta martedì mattina UTC 14:00.

6. **Track 3 numbers.** GitHub stars/week, sign-up/week, MRR. Tutto
   il resto è vanity. Ogni venerdì, 5 minuti, scrivi i 3 numeri in
   `metrics.md`.

7. **Pricing sotto $99/mese è fatto, sotto $49 è ottimale.** Più
   facile vendere $49 a 100 dev che $499 a 10 enterprise.

8. **Se non sopporti il marketing per 6 mesi, vendi/abbandona dopo
   M3.** Il lavoro reale di una solo SaaS non è scrivere codice — è
   marketing. Se ti piace solo il primo, hai sbagliato job.

9. **Tieni un secondo income stream come piano B.** Freelance Python /
   DevOps consulting al 50%. Riduce stress finanziario, ti permette
   di NON svendere il prodotto a un acquirer scarso per pressione
   cash.

10. **Non raise prima di avere $5K MRR.** I VC pre-seed con <$5K MRR
    fanno bridge che si seccano, ti chiedono 20-30% per nulla, e
    ti aspettano $200K MRR a 12 mesi senza darti i mezzi per
    farlo. Bootstrap fino a $5K MRR poi raise se vuoi scalare oltre.

---

## 9. Cosa fare LUNEDÌ MATTINA (concreto)

Smetti di leggere documentazione e fai questi tre task:

### Task 1 — Compra il dominio (10 minuti)

```
Vai su https://www.cloudflare.com/products/registrar/
Cerca: annexkit.dev
Compra: ~€10/anno
```

Mentre ci sei: compra anche `annexkit.eu` come backup.

### Task 2 — Pubblica il SDK su PyPI (15 minuti)

```bash
# 1. Account PyPI
Vai su https://pypi.org/account/register/
Setup 2FA con app authenticator (obbligatorio per nuovi pacchetti)

# 2. Genera API token PyPI
PyPI → Account settings → API tokens → Add API token
Scope: "Entire account" (o specifico per annexkit dopo il primo upload)

# 3. Pubblica
cd /Users/mykael/PycharmProjects/AnnexKit/sdk
uv build      # produce dist/annexkit-0.1.0-*.whl
uv publish    # ti chiederà il token PyPI
```

Verifica:
```bash
pip install annexkit==0.1.0
python -c "import annexkit; print(annexkit.__version__)"
# → 0.1.0
```

### Task 3 — Setup Hetzner VPS + DNS (45 minuti)

```
1. https://www.hetzner.com/cloud
   Crea progetto AnnexKit
   New Server → CX21 (€5/mese) → Falkenstein DC
   OS: Debian 12
   SSH key: la tua

2. SSH al server, installa Docker:
   curl -fsSL https://get.docker.com | sh

3. Clone il repo + deploy:
   git clone https://github.com/annexkit/annexkit /opt/annexkit
   cd /opt/annexkit
   cp .env.example .env
   # Edita .env: ENV=prod, SECRET_KEY=<genera 48 byte>, CORS_ORIGINS=["https://annexkit.dev"]
   docker compose up -d

4. Cloudflare:
   Aggiungi sito annexkit.dev
   Cambia nameservers su Cloudflare Registrar
   Crea A record: annexkit.dev → IP Hetzner
   Crea CNAME: collector.annexkit.dev → annexkit.dev
   SSL/TLS mode: Full (strict)

5. Verifica:
   curl https://collector.annexkit.dev/health
   → {"status":"ok"}
```

Fatto questi tre task, sei live.

---

## Disclaimer finale

Questo è un mercato reale, con un prodotto reale, in un momento reale.
La probabilità di profitto è REALE ma non garantita.

Le stime numeriche qui dentro hanno un margine di errore del ±30-50%.
Il futuro non è prevedibile in dettaglio, soprattutto per un prodotto
B2B SaaS in un mercato regolamentato che si sta formando.

**Quello che è certo**: l'AI Act entra in piena applicazione il 2
agosto 2026. Le aziende avranno bisogno di strumenti come AnnexKit.
Qualcuno costruirà il prodotto vincente. Tu sei in posizione di farlo
se esegui bene per 12-18 mesi.

**Quello che non è certo**: che TU sia quel qualcuno. Dipende da
esecuzione, fortuna, marketing, e capacità di sopportare 6-9 mesi di
incertezza prima di vedere segnali chiari.

Vai avanti se sei dentro per 12-18 mesi. Non andare avanti se hai un
plan B più solido (lavoro stabile, altra startup più matura, etc.).

In bocca al lupo.
