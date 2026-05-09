# AnnexKit — Piano Strategico ed Esecutivo

> Documento di lavoro. Status: **proposta di pivot/spin-off da Konformia**.
> Data: 2026-05-07.
> Lingua del prodotto: inglese primaria (target globale EU). Lingua interna: italiano.

---

## 0. TL;DR

**Cos'è**: SDK + collector + Annex IV generator + trust center pubblico per la
**conformità runtime all'EU AI Act**. Si installa con `pip install annexkit`
(Python first, TS dopo). Ogni chiamata LLM in produzione viene strumentata,
classificata sul tier di rischio Annex III, mappata agli Article 11–13–15 e
trasformata in evidenze audit-ready (log Article 12, documentazione tecnica
Annex IV, transparency records, post-market monitoring).

**Buyer**: CTO / AI lead / ML engineer di scaleup EU che ha LLM in produzione
e ha bisogno di dimostrare conformità AI Act dal **2 agosto 2026**. Non un
avvocato. Non un DPO. Non una PMI italiana. Un developer.

**Tesi**: i tool LLM-ops attuali (LangSmith, Langfuse, Confident AI, Helicone,
Arize) fanno *evals tecniche*. Non mappano la telemetria al testo dell'AI
Act. Le piattaforme AI governance (Credo AI, Holistic AI, VenVera) fanno
enterprise sales a $200K+/anno. Esiste un buco self-serve, dev-first,
AI-Act-first, EU-hosted. Quel buco è AnnexKit.

**Bet sul tempo**: 12 mesi per arrivare a **$10K MRR** con prodotto open-core,
distribuzione GitHub + HN, zero sales B2B, zero credibilità giuridica
richiesta al founder.

**Riuso Konformia**: ~70-80% del codebase esistente (`annex_iii.json`, risk
classifier, LLM advisor, audit log append-only, FastAPI/Postgres async stack,
Pydantic schemas, disclaimer pattern). Il pivot non butta Konformia — la
trasforma in *un'istanza italiana consumer* dello SDK più ampio.

**Risolve il problema di credibilità**: il buyer è tecnico, compra evidenze
tecniche. Il disclaimer "Konformia / AnnexKit non è uno studio legale"
diventa naturale: il dev capisce che il SDK produce *prove*, e il legal team
del cliente le interpreta.

---

## 1. Il problema

### 1.1 Pressione regolamentare imminente

Il **Regolamento UE 2024/1689 (AI Act)** entra in vigore in modo scaglionato:

- **2 agosto 2025**: GPAI obbligations già attive.
- **2 agosto 2026**: piena applicabilità ai sistemi high-risk Annex III.
- **2 agosto 2027**: applicabilità ai sistemi high-risk integrati in prodotti
  regolati (Annex I).

Sanzioni fino a **€35M o 7% del fatturato globale** (Article 99). I sistemi
"high-risk" Annex III includono settori in cui CHIUNQUE oggi sta integrando
LLM: HR/recruitment, credit scoring, education assessment, law enforcement
support, critical infrastructure decisioning, biometrics.

### 1.2 Cosa richiede tecnicamente l'AI Act

Per ogni sistema high-risk il provider deve produrre:

| Obbligo | Cosa significa in pratica per chi scrive codice |
|---|---|
| **Article 11 + Annex IV** | Documentazione tecnica scritta, *vivente*, su 9 punti specifici (general description, design choices, monitoring, risk management, data, validation, post-market plan, EU declaration of conformity) |
| **Article 12** | Logging automatico durante l'intero ciclo di vita del sistema, conservato e tracciabile |
| **Article 13** | Transparency: gli utenti devono sapere che stanno interagendo con un AI system; documentazione di accompagnamento |
| **Article 14** | Human oversight design: pulsanti di stop, override, escalation |
| **Article 15** | Accuracy, robustness, cybersecurity tracking + adversarial test logs |
| **Article 72** | Post-market monitoring system attivo |

Per un dev medio, questo significa: ogni call OpenAI/Anthropic/Mistral nella
mia app deve produrre evidenze persistenti, mappate a testo legale, in
formato che un auditor può ispezionare.

### 1.3 Cosa fanno gli strumenti esistenti (e cosa NON fanno)

**Categoria A — LLM observability/evals**: Confident AI, LangSmith, Langfuse,
Helicone, Arize Phoenix. Tutti fanno bene span tracking, eval pipelines,
prompt management. **Nessuno** mappa output al testo AI Act. Nessuno produce
Annex IV. Nessuno classifica risk tier.

**Categoria B — AI governance enterprise**: Credo AI, Holistic AI, VenVera,
Saidot. Fanno mapping AI Act, ma:
- Pricing $50K-$500K/anno
- Sales cycle 3-12 mesi
- Self-serve inesistente
- US-centric (data residency dubbia)
- Workflow human-driven (form, review, sign-off) anziché automatic-from-runtime

**Categoria C — General GRC**: Vanta, Drata, SafeBase. SOC2/ISO27001/HIPAA
focus, AI Act è feature minore o assente.

**Il gap**: nessuno offre `pip install` + decoratore + Annex IV auto-generato
+ trust center pubblico, sub-€100/mese, EU-hosted, dev-first. È whitespace.

### 1.4 Scenari concreti di pain (non astratti)

1. **Scaleup tedesca SaaS B2B** integra GPT-4 per email triage. Vende a
   banca svizzera. Banca chiede "give us your AI Act conformity evidence".
   Lo scaleup non sa cosa rispondere. Tempo perso: 3 settimane di un AI
   engineer + un consulente legale esterno €15K.

2. **Banca italiana** usa LLM per pre-screen credit applications. Audit
   interno (KYC + Bankitalia) chiede log Article 12. La banca ha logs
   applicativi non strutturati. Dev team deve retroactively normalizzare
   3 mesi di traffico.

3. **Startup AI HR (recruitment)** = high-risk Annex III definito.
   Investitore lead in Series A chiede "show me your AI Act readiness".
   Founder tecnico non sa cosa mostrare.

4. **Studio legale che consiglia clienti enterprise sull'AI Act** chiede
   ai clienti "datemi log di esempio del vostro sistema". Cliente non li
   ha in formato utile. Studio fattura €40K, founder paga.

In tutti questi scenari, AnnexKit risolve in 5 minuti quello che oggi
richiede settimane.

---

## 2. La soluzione (cosa è AnnexKit)

### 2.1 Componenti core

```
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICAZIONE CLIENTE                        │
│                                                                   │
│   from annexkit import track                                      │
│   from openai import OpenAI                                       │
│                                                                   │
│   @track(system_id="loan-screener", risk_tier="auto")            │
│   def screen_application(applicant, history):                    │
│       resp = OpenAI().chat.completions.create(...)               │
│       return resp.choices[0].message.content                     │
└────────────────────────────┬─────────────────────────────────────┘
                             │  OTLP / HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANNEXKIT COLLECTOR (FastAPI)                   │
│                                                                   │
│   • Ingest spans (OTLP-compatible)                                │
│   • Normalize to AnnexKit schema (model_id, prompt_id,           │
│     input_hash, output_hash, retrieval_sources, user_role,       │
│     latency, error)                                               │
│   • Persist append-only (audit_logs table from Konformia)        │
│   • Run risk classifier (rules from annex_iii.json)              │
│   • Emit conformity events                                        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌──────────┐  ┌──────────────┐  ┌─────────────────┐
       │ Postgres │  │  Annex IV    │  │  Trust Center   │
       │ + S3     │  │  Generator   │  │  (Next.js)      │
       │ blobs    │  │  (markdown   │  │  pubblico:      │
       │          │  │   + PDF)     │  │  inventory,     │
       │          │  │              │  │  CRA SBOM,      │
       │          │  │              │  │  AI systems     │
       └──────────┘  └──────────────┘  └─────────────────┘
```

### 2.2 SDK — interfaccia developer

**Decorator pattern (uso primario)**:

```python
from annexkit import track, Source

@track(
    system_id="customer-support-bot",
    deployment="prod",
    risk_tier="auto",  # classifier decide; "high"|"limited"|"minimal" override
    purpose="answer customer questions on shipping and returns",
)
def chat(user_msg: str, user_role: str, conversation_id: str):
    docs = retrieve_knowledge_base(user_msg)
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *[{"role": "system", "content": d.text} for d in docs],
            {"role": "user", "content": user_msg},
        ],
    )
    return response.choices[0].message.content
```

**Context manager pattern (per chiamate non funzioni)**:

```python
with track.session(system_id="rag-search", user_role="employee") as session:
    docs = retriever.search(query)
    session.attach_sources([Source(uri=d.uri, hash=d.hash) for d in docs])
    answer = llm.generate(query, docs)
    session.set_output(answer)
```

**Middleware pattern (FastAPI/Express)**:

```python
from annexkit.fastapi import AnnexKitMiddleware
app.add_middleware(AnnexKitMiddleware, system_id="api-llm-endpoints")
```

**Auto-instrumentation (zero-touch per integrazioni note)**:

```python
import annexkit
annexkit.auto_instrument(["openai", "anthropic", "langchain", "llama_index"])
# Da qui in poi qualsiasi chiamata viene strumentata automaticamente
```

### 2.3 Schema dello span AI-Act-aware

Estendiamo OpenTelemetry GenAI semantic conventions con campi AI-Act-specific:

```json
{
  "trace_id": "...",
  "span_id": "...",
  "system_id": "loan-screener",
  "deployment": "prod",
  "system_version": "v1.4.2",
  "risk_tier": "high",
  "annex_iii_categories": ["credit_scoring"],
  "model": {
    "provider": "openai",
    "name": "gpt-4o",
    "version": "2024-11-20",
    "id_hash": "sha256:..."
  },
  "prompt": {
    "template_id": "loan-decision-v3",
    "template_hash": "sha256:...",
    "input_hash": "sha256:...",
    "input_redacted": true
  },
  "retrieval": {
    "sources": [
      {"uri": "kb://policies/credit/001", "hash": "...", "version": "..."}
    ]
  },
  "output": {
    "hash": "sha256:...",
    "tokens": 142,
    "decision_class": "denied"
  },
  "user_context": {
    "role": "loan_officer",
    "session_id_hash": "...",
    "human_oversight_link": "https://app/case/12345"
  },
  "performance": {"latency_ms": 1843, "ttft_ms": 320, "error": null},
  "conformity": {
    "article_12_logged": true,
    "article_13_disclosure_shown": true,
    "article_14_human_review_path": "loan_officer_approval"
  }
}
```

Lo schema è **append-only** (riusa il pattern audit log di Konformia,
non-negoziabile in CLAUDE.md), versionato, firmato crittograficamente lato
server con chiave per-tenant.

### 2.4 Annex IV generator

I 9 punti dell'Annex IV vengono auto-popolati da metadata + telemetria:

| Annex IV § | Sorgente del contenuto |
|---|---|
| 1. General description | `system_id`, `purpose`, `deployment` decorator args + manifest YAML opzionale |
| 2. Design choices | Repo metadata (commit hash, dependencies SBOM), prompt templates registrati |
| 3. Monitoring/control | Auto-doc da decorator + middleware presenti |
| 4. Risk management | Output del classifier rules-based (`annex_iii.json` da Konformia) |
| 5. Data | Lista `Source` aggregata da retrieval logs |
| 6. Validation/testing | Eval results se l'utente integra con LangSmith/promptfoo (parser supportato) |
| 7. Post-market plan | Template + slot per incident reporting |
| 8. Changes log | Span timeline + version diffs |
| 9. EU declaration of conformity | Auto-generato da signed manifest |

Output: Markdown + PDF. PDF generato via WeasyPrint (già in stack
Konformia) con disclaimer permanente in footer.

### 2.5 Trust Center pubblico

Sotto-dominio per-tenant: `https://<co>.annexkit.eu/trust`.

Pagine:
- `/trust` — overview, ultima conformity check, badge "AI Act ready".
- `/trust/systems` — inventory pubblico dei sistemi AI dichiarati.
- `/trust/systems/<id>` — Annex IV pubblico (versione redacted).
- `/trust/policy` — policy AI use, linkata in footer del prodotto cliente.
- `/trust/incidents` — incident log redacted.

Ispirato a SafeBase/Conveyor, ma AI-Act-first invece che SOC2-first.

### 2.6 Cosa AnnexKit NON è (esplicito)

- **Non è uno studio legale.** Non interpreta l'AI Act. Produce evidenze.
- **Non sostituisce un DPO.** Lo aiuta.
- **Non è un sostituto di LangSmith/Langfuse.** Si integra con loro.
- **Non è un AI eval framework.** Si integra con promptfoo, DeepEval ecc.
- **Non classifica autonomamente come "minimal" un sistema dichiarato
  high-risk.** Il classifier è deterministico e l'LLM advisor non può
  *declassificare* (regola ereditata da Konformia, non-negoziabile).

---

## 3. Perché ora

| Driver | Perché conta | Fonte |
|---|---|---|
| 2 agosto 2026 = piena enforcement AI Act | "Y2K-like" deadline. Ogni team con LLM in prod deve essere pronto | [artificialintelligenceact.eu/article/11](https://artificialintelligenceact.eu/article/11/) |
| Sanzioni 7% fatturato globale | C-level attention guaranteed | Article 99 AI Act |
| LLM in produzione esplosi 2024-2026 | Surface area enorme di sistemi da documentare | Public adoption metrics |
| Sovereign cloud demand post-CLOUD Act | "AWS EU region" non è data sovereignty. EU-hosted è moat | [Lyceum](https://lyceum.technology/magazine/eu-data-residency-ai-infrastructure/) |
| LLM-ops tools mancano AI Act mapping | Confermato in landscape scan: zero copertura nei top-5 | [confident-ai.com](https://www.confident-ai.com/), [langchain.com/langsmith](https://www.langchain.com/langsmith/observability) |
| AI governance enterprise è inaccessibile | Pricing 100x troppo alto per scaleup/startup | [VenVera competitor list](https://venvera.com/best/eu-ai-act-compliance-software/) |
| CRA Settembre 2026 si sovrappone | Sinergia: SBOM (CRA) + Annex IV (AI Act) condividono il trust center | [OpenSSF blog](https://openssf.org/blog/2025/10/22/sboms-in-the-era-of-the-cra-toward-a-unified-and-actionable-framework/) |

Finestra realistica di vantaggio: **6-12 mesi** prima che un Confident AI o
una LangSmith pivotino su AI Act. In quei 6-12 mesi devi conquistare il brand
"AI Act-first" e stabilire integrazioni di default.

---

## 4. Perché tu (founder fit)

### 4.1 Asset tecnici già pronti (Konformia)

| Konformia → AnnexKit | Riuso | Modifiche |
|---|---|---|
| `app/data/annex_iii.json` | 100% riuso | Espandere edge cases dagli early users |
| Risk classifier rules-driven | 100% riuso | Wrap come funzione pura `classify(metadata) -> tier` |
| LLM advisor (Mistral/Anthropic fallback) | 100% riuso | Stessi guardrails (no-declassify rule) |
| Audit log append-only pattern | 100% riuso | Diventa lo span store |
| FastAPI + SQLAlchemy 2.0 async + Postgres 16 | 100% riuso | Aggiungere pgvector se non c'è già |
| Pydantic schemas (request/response) | 100% riuso | Schema per OTLP-extended span |
| Disclaimer permanente UI | 100% riuso | Stesso disclaimer in PDF Annex IV |
| Next.js 16 frontend | 60% riuso | Trust center pubblico è una nuova route group, dashboard interno è simile |
| Docker Compose dev stack | 100% riuso | + collector container |
| Hetzner deploy | 100% riuso | + Cloudflare in front |

### 4.2 Asset di dominio

- Hai già letto Annex III/IV, L. 132/2025, AgID linee guida. Vantaggio
  cumulativo non banale: la maggior parte dei dev EU non l'ha letto.
- Hai già pensato il pattern "deterministico-primario, LLM-advisor secondario,
  mai declassifica" — questo è un differenziatore epistemico importante che
  US tools non hanno.

### 4.3 Match con il buyer

Il buyer è un dev. Tu sei un dev. Parli il suo linguaggio. Confident AI e
LangSmith sono fondate da PhD ML researchers, parlano di "evals" e
"benchmarks". Credo AI è fondata da policy folks, parla di "governance
frameworks". **Nessuno parla "AI Act + OpenTelemetry + GitHub Action"**.
Quel linguaggio è il tuo.

### 4.4 Moat strutturali

1. **Lingua e data residency**: AnnexKit-hosted gira su Hetzner Falkenstein,
   inferenza LLM via Mistral La Plateforme (Parigi). Un competitor US deve
   spostare infra E rinegoziare contratti — barriera reale.
2. **Knowledge depth normativa**: L. 132/2025, AgID, eIDAS2, NIS2 — sono
   contesti specifici EU/IT che US tools non documenteranno mai bene.
3. **Konformia come canale italiano già scaldato**: outreach/email lavoro
   già fatto, lista contatti, etc. È seme.
4. **Open-source community**: il SDK MIT su GitHub è impossibile da copiare
   con marketing solo, va costruito con commit history.

---

## 5. Architettura tecnica

### 5.1 Repo layout proposto

```
annexkit/                                 (monorepo)
├── README.md
├── CLAUDE.md                             (eredita pattern da Konformia)
├── Makefile
├── docker-compose.yml
├── .env.example
│
├── packages/
│   ├── annexkit-py/                      (SDK Python — pubblicato su PyPI)
│   │   ├── annexkit/
│   │   │   ├── __init__.py
│   │   │   ├── decorator.py              (@track)
│   │   │   ├── context.py                (track.session)
│   │   │   ├── auto_instrument.py
│   │   │   ├── exporters/
│   │   │   │   ├── otlp.py
│   │   │   │   └── http.py
│   │   │   ├── integrations/
│   │   │   │   ├── openai.py
│   │   │   │   ├── anthropic.py
│   │   │   │   ├── langchain.py
│   │   │   │   ├── llama_index.py
│   │   │   │   └── fastapi.py
│   │   │   └── schema.py                 (Pydantic span schema)
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   └── annexkit-ts/                      (SDK TypeScript — Q2/Q3 milestone)
│       └── ...
│
├── backend/                              (collector + dashboard API)
│   ├── app/
│   │   ├── routes/                       (thin controllers)
│   │   │   ├── ingest.py                 (POST /v1/spans/otlp)
│   │   │   ├── systems.py
│   │   │   ├── annex_iv.py
│   │   │   └── trust_center.py
│   │   ├── services/                     (fat services — riusa Konformia)
│   │   │   ├── classifier.py             ← riuso annex_iii.json
│   │   │   ├── annex_iv_generator.py
│   │   │   ├── conformity_checker.py
│   │   │   └── llm_advisor.py            ← riuso pattern Konformia
│   │   ├── models/                       (SQLAlchemy)
│   │   │   ├── audit_log.py              ← riuso Konformia, append-only
│   │   │   ├── span.py
│   │   │   ├── system.py
│   │   │   └── tenant.py
│   │   ├── schemas/                      (Pydantic)
│   │   └── data/
│   │       └── annex_iii.json            ← copia da Konformia
│   ├── alembic/
│   └── tests/
│
├── frontend/                             (Next.js 16, App Router)
│   ├── app/
│   │   ├── (dashboard)/                  (auth, internal)
│   │   ├── (trust)/                      (pubblico, per-tenant)
│   │   └── (marketing)/                  (landing, docs)
│   └── ...
│
├── docs/
│   ├── architecture.md
│   ├── ai_act_mapping.md
│   └── integrations/
│
└── examples/
    ├── chatbot-openai/
    ├── rag-llamaindex/
    └── credit-scorer-langchain/
```

### 5.2 Stack invariato rispetto a Konformia (Section CLAUDE.md)

- Backend: Python 3.13 + FastAPI + SQLAlchemy 2.0 async + Postgres 16
  (pgvector se serve per matching semantic dei prompt template).
- Frontend: Next.js 16 + shadcn/ui + Tailwind 4.
- Auth: stesso pattern Konformia (JWT cookie).
- Dev: Docker Compose. Prod: Hetzner + Cloudflare.

Le **non-negoziabili Konformia** restano valide:
1. Risk Engine deterministico, LLM solo advisor, **mai** declassifica.
2. `audit_logs` append-only.
3. EU data residency (Mistral EU + storage Hetzner).
4. Thin controllers, fat services.
5. Type hints + Pydantic ovunque.
6. Disclaimer permanente.

### 5.3 Choices critiche di design

**Span ingest path**: OTLP-compatible su `/v1/spans/otlp` (compatibile con
qualsiasi OpenTelemetry collector); fallback HTTP JSON su `/v1/spans` per
SDK semplici. Consente al cliente di mandare span via il suo otel-collector
esistente.

**Storage**: Postgres per metadata + indexed query, S3-compatible (Hetzner
Object Storage o MinIO self-hosted) per blob (prompt templates redacted,
PDF Annex IV firmati). Retention configurabile (default 7 anni per
high-risk, allineato a Article 18).

**Hashing & redaction**: input/output **mai** loggati in chiaro by default.
Si logga `sha256(input)` + length + token count + classification class.
Opt-in per logging plaintext con encryption at rest (per debugging dev).

**Multi-tenancy**: schema-per-tenant in Postgres; row-level security come
defense-in-depth.

**Async-first**: nessun `time.sleep`, `httpx.AsyncClient` per qualsiasi
out-of-process call (Mistral, Anthropic, S3).

---

## 6. Riuso da Konformia — checklist puntuale

| Item Konformia | Azione | Effort |
|---|---|---|
| `app/data/annex_iii.json` | Copy as-is | 5 min |
| `app/services/classifier.py` (rule engine) | Copy + wrap come funzione pura | 1 h |
| `app/services/llm_advisor.py` (Mistral/Anthropic fallback) | Copy as-is | 30 min |
| `app/models/audit_log.py` (append-only) | Copy + estendi schema per span | 2 h |
| `app/services/annex_iv_generator.py` | Copy + adatta input source da form a span aggregation | 1 giorno |
| Pydantic schemas | Copy + crea schema span OTLP-extended | 1 giorno |
| FastAPI app skeleton + `Depends()` pattern | Copy as-is | 1 h |
| Docker Compose dev stack | Copy as-is | 30 min |
| Frontend disclaimer component | Copy as-is | 30 min |
| Auth (JWT cookie) | Copy as-is | 1 h |
| Health/ping endpoints | Copy as-is | 15 min |
| Makefile targets (`up`, `lint`, `test`) | Copy + estendi | 30 min |

**Tempo totale di setup riuso**: ~3 giorni di lavoro effettivo. È il motivo
per cui questo pivot ha senso e non è un rebuild from scratch.

---

## 7. MVP della prima settimana — giorno per giorno

Obiettivo giorno 7: una repo pubblica, un `pip install`, un README che funziona,
una demo end-to-end in 60 secondi, un video di 90 secondi caricato.

### Giorno 1 — Setup infra
- Compra dominio: `annexkit.dev` (primario) + `annexkit.eu` (trust center).
- Crea repo GitHub `annexkit/annexkit` pubblico, README iniziale.
- Setup monorepo (pnpm workspace o uv workspace).
- Copy delle non-negoziabili da Konformia (`annex_iii.json`, classifier,
  audit_log model, disclaimer pattern).
- Skeleton package `annexkit-py` (PyPI registration, namespace check).
- Docker Compose: `db` + `collector` services.

### Giorno 2 — SDK core
- `annexkit/decorator.py`: `@track` decorator con cattura args, output, latency,
  errori. Async + sync.
- `annexkit/schema.py`: Pydantic span schema (riuso pattern Konformia).
- `annexkit/exporters/http.py`: HTTP JSON POST a collector (OTLP arriva
  giorno 5).
- Test: una funzione decorata produce uno span valido.

### Giorno 3 — Collector ingest
- FastAPI route `POST /v1/spans` (HTTP JSON ingest).
- Persist append-only su `audit_logs` (riuso schema Konformia + extension).
- Auth: API key per tenant (header `Authorization: Bearer ak_...`).
- Health check, OpenAPI docs.

### Giorno 4 — Risk classifier integration
- `services/classifier.py`: prendi metadata span (`system_id`, `purpose`,
  `annex_iii_categories`), restituisci `risk_tier`.
- LLM advisor opzionale per ambiguity: se classifier rules dicono "ambiguo",
  LLM advisor suggerisce ma non declassifica.
- Test: spans di esempio classificate correttamente.

### Giorno 5 — Annex IV generator
- `services/annex_iv_generator.py`: genera markdown coprendo i 9 punti per
  un `system_id` aggregando span + metadata.
- Render PDF via WeasyPrint (riuso da Konformia).
- Endpoint `GET /v1/systems/{id}/annex-iv?format=md|pdf`.
- Disclaimer permanente nel footer.

### Giorno 6 — Demo end-to-end
- Cartella `examples/chatbot-openai/`: un mini-chatbot Flask/FastAPI che usa
  OpenAI con `@track` decorator, sistema dichiarato `customer-support-bot`.
- Run del demo: 50 chiamate generate, span fluiti al collector.
- `curl /v1/systems/customer-support-bot/annex-iv` produce un PDF leggibile.
- Screenshot + GIF + esempi pdf in `docs/examples/`.

### Giorno 7 — Lancio soft
- Landing page minimale (`annexkit.dev`): hero + 3 sezioni (Problem, Demo,
  Quickstart) + GitHub link. Build con Next.js 16 (riuso template Konformia).
- Demo video 90s: pip install → @track → /annex-iv → PDF aperto. Script
  pre-scritto, registrato con OBS, no editing fancy.
- README polish: badges, quickstart 3 righe, link a docs minimal.
- PyPI publish `annexkit==0.1.0`.
- **Non** lanciare ancora su HN. Il giorno 7 è "soft live": condividi solo
  con 5-10 amici tecnici per feedback. HN va il giorno 14, dopo iterazione.

---

## 8. Roadmap 12 mesi

| Mese | Milestone tecnico | Milestone business |
|---|---|---|
| **M1** | MVP live (Giorni 1-7), iterazione su feedback (Giorni 8-21), Show HN (Giorno ~14-21) | 50 GitHub stars, 3 dev "production users" gratis (volontari) |
| **M2** | Integrazioni: LangChain, OpenAI auto-instrument, Anthropic auto-instrument. Trust center pubblico v0. | 200 stars, 10 paying customers Pro $49 → $490 MRR |
| **M3** | TS/JS SDK (`@annexkit/node`). Vercel AI SDK integration. | 25 paying → $1.2K MRR. 1 case study scritto |
| **M4** | Multi-tenancy hardening, SSO (Google/GitHub), API key management UI | 50 paying → $2.5K MRR |
| **M5** | LangSmith/Langfuse importer (porta i tuoi span esistenti) | 80 paying → $4K MRR |
| **M6** | CRA SBOM module (riuso del trust center per SBOM publishing) | 120 paying → $6K MRR. Primo Team tier $199 (10 customers) |
| **M7** | Self-hosted enterprise tier (Helm chart) | 1-2 enterprise self-hosted €5K/anno |
| **M8** | Eval framework adapters (promptfoo, DeepEval, Inspect AI) | 200 paying → $10K MRR target raggiunto |
| **M9** | Italian dashboard/PDF mode (Konformia consumer integrato) | Lancio "Konformia by AnnexKit" mercato IT |
| **M10** | SOC2 Type I lite (via OpenStatus/Vanta-clone) | Trust center features per regulated industries |
| **M11** | Audit-readiness simulator (mock auditor questions) | Partnership con 1-2 studi legali EU per channel |
| **M12** | Public benchmark suite "AI Act readiness score" per LLM apps | Conference talk (DjangoCon EU / EuroPython / FOSDEM) |

**North Star metric**: span tracked / mese.
- M1: 100K · M3: 10M · M6: 100M · M12: 1B.

**Revenue milestones**:
- M3: $500 MRR · M6: $3K MRR · M12: $10K MRR.

I numeri sono volutamente conservativi e allineati con i benchmark
solo-founder SaaS (mediana 12-18 mesi a $1K MRR; AnnexKit punta più alto
per la pressione regolamentare).

---

## 9. Distribuzione (go-to-market self-serve)

Vincolo: zero sales calls, zero "richiedi demo", zero outbound B2B telefonico.

### 9.1 Canali primari

1. **GitHub stesso**: SDK pubblico MIT. Ogni `pip install` è marketing.
   Topic GitHub `ai-act` (oggi ~80 repo seri — saturare il topic con quality
   commits). README ottimizzato per discovery interna GitHub.

2. **Hacker News**: 1 lancio "Show HN" ben preparato (Giorno ~14-21).
   Pattern proven: titolo "Show HN: AnnexKit – OpenTelemetry-style collector
   for the EU AI Act". HN ama EU regulation discussion + dev tools pratici.
   Tasso di successo realistico: front page se eseguito bene.

3. **Reddit**: r/MachineLearning (cautela, mod severi), r/LocalLLaMA,
   r/europrivacy, r/programming, r/Italian (per beachhead IT).
   1 post ogni 2-3 settimane, sempre con valore aggiunto, mai shilling.

4. **SEO long-tail**: parole chiave bassa concorrenza:
   - "Annex IV AI Act template"
   - "Article 12 AI Act logging requirements"
   - "EU AI Act technical documentation example"
   - "AI Act high-risk system checklist"
   - "Annex III AI Act categories"
   - "documentazione tecnica AI Act italiano"
   - "AI Act compliance for developers"
   Pubblicare 1 articolo lungo / settimana per 6 mesi → 24 articoli =
   ~2K-5K visitatori organici/mese a M6.

5. **Newsletter dev EU**: ottenere mention/menzione in TLDR, Bytes,
   Console, JavaScript Weekly, Pycoder's Weekly. Costo: pitching mirato.

6. **Italian dev community** come beachhead/early adopters:
   - GrUSP (conferenze frontend IT)
   - Avanscoperta (workshop)
   - Italian Python User Group
   - Schrödinger Hat (conf indipendente)
   - Sponsorship leggero (€500-2000 per evento) in cambio di visibility.

### 9.2 Canali secondari

7. **LinkedIn**: profilo founder posta 3x/settimana su AI Act in pratica
   (no policy talk — sempre con codice/screenshot). Non DM outbound, solo
   inbound.
8. **Twitter/X**: thread tecnici. Solidarity con altri indie dev EU.
9. **Podcast guest spots**: Continuous Delivery (IT), Web Rush, Software
   Engineering Daily.
10. **Open-source contributions**: PR a LangChain/LlamaIndex per adapter
    AnnexKit nativo. Visibilità reciproca.

### 9.3 NON fare

- ❌ Cold email B2B a CTO. Brand-damaging in dev community.
- ❌ Banner ads Google. Bruci soldi senza targeting.
- ❌ Listing Capterra/G2 prima di avere $5K MRR. Diluisce il messaging.
- ❌ Webinar "thought leadership". Stesso reason.
- ❌ Sales-y messaging. Dev sniffano subito e bouncano.

---

## 10. Modello di pricing

### 10.1 Tier

| Tier | Prezzo | Spans/mese | AI Systems | Utenti | Features chiave |
|---|---|---|---|---|---|
| **Free / OSS** | $0 | 100K | 1 | 1 | SDK MIT, collector self-host, no Annex IV PDF, no trust center |
| **Pro** | $49/mese | 5M | 10 | 3 | Annex IV PDF, trust center pubblico, support email |
| **Team** | $199/mese | 50M | unlimited | 10 | SSO, audit log retention 7 anni, SLA, priority support |
| **Enterprise self-hosted** | €5K/anno | unlimited | unlimited | unlimited | Helm chart, custom support, contract terms |

### 10.2 Razionali

- **Free generoso** è il marketing. 100K span = un piccolo prodotto reale
  per 1-2 settimane di traffico, abbastanza per innamorarsi del prodotto.
- **Pro $49** è il sweet spot solopreneur — copre 95% dei micro-team.
- **Team $199** unlocka ciò che gli enterprise buyer chiedono (SSO, retention).
- **Enterprise self-hosted** = exit valve per regulated industries (banking,
  health) che NON faranno SaaS multi-tenant. Single-time setup, ricorrente.

### 10.3 Free trial vs freemium

Freemium > free trial per dev tools. Il free tier deve essere usabile
indefinitamente per progetti piccoli. Conversion happens quando il dev sta
già amando il prodotto e prende un secondo cliente / scala.

### 10.4 Payment

Stripe Checkout, niente sales/quotes. Annual discount 20%. Cancellazione
self-serve.

---

## 11. Metriche e milestone

### 11.1 KPI principali

- **Spans tracked / mese** (north star) — segnale di adozione reale
- **Number of paying customers** — segnale di willingness to pay
- **MRR** — segnale di sostenibilità
- **GitHub stars** — segnale di brand awareness (vanity ma utile early)
- **Time to first span** dopo install (target: < 5 min) — segnale di UX

### 11.2 Funnel atteso (steady state, dopo M3)

```
1000 unique landing visitors / mese
 ↓ 30%
300 GitHub repo visits
 ↓ 20%
60 pip install
 ↓ 50%
30 first span ingestato
 ↓ 30%
9 active users (>10 spans / day per 7 giorni)
 ↓ 25%
2-3 conversion to Pro $49
```

= **~$120 MRR added / mese** a steady state con 1000 visitors. Per arrivare
a $10K MRR servono ~80 paying = ~30 mesi a quel rate. Per accelerare:
crescere visitors (SEO + HN spike) + alzare conversion.

### 11.3 Decision points

- **M3 ($500 MRR)**: se non raggiunto, indagare se è prodotto, messaging
  o canale. Pivot tactical, non strategico.
- **M6 ($3K MRR)**: se non raggiunto, considerare channel pivot a
  studi/consulenti (Idea 3 dal report di mercato).
- **M9 ($6K MRR)**: se raggiunto, double-down su Italian beachhead per
  rilanciare Konformia consumer.
- **M12 ($10K MRR)**: se raggiunto, considera primo full-time hire (DevRel).

---

## 12. Concorrenti — analisi puntuale

| Concorrente | Cosa fa | Pricing | Cosa NON fa | Wedge AnnexKit |
|---|---|---|---|---|
| **Confident AI** ([confident-ai.com](https://www.confident-ai.com/)) | LLM evals + observability | Free + Enterprise | AI Act mapping, Annex IV, EU residency | AI Act-first; integrabile come complement |
| **LangSmith** ([langchain.com/langsmith](https://www.langchain.com/langsmith/observability)) | LLM tracing + evals | Free → $39/seat | AI Act mapping, conformity docs | Focus regulatory; può importare span da LangSmith |
| **Langfuse** ([langfuse.com](https://langfuse.com/)) | LLM observability OSS | Free OSS + cloud | AI Act mapping | Stesso wedge, Langfuse è friendly: integrazione bidirezionale |
| **Helicone** ([helicone.ai](https://www.helicone.ai/)) | LLM proxy + analytics | $0-$500 | AI Act mapping | Complementare; possibile partnership |
| **Arize Phoenix** ([phoenix.arize.com](https://phoenix.arize.com/)) | LLM/ML observability OSS | Free OSS | AI Act, EU residency | Stesso wedge regulatory |
| **Credo AI** ([credo.ai](https://www.credoai.com/)) | AI governance enterprise | $200K+/anno | Self-serve, SDK, dev-first | Self-serve $49, SDK, dev-first |
| **Holistic AI** ([holisticai.com](https://www.holisticai.com/)) | AI governance enterprise | $100K+/anno | Self-serve, SDK | Self-serve, SDK |
| **VenVera** ([venvera.com](https://venvera.com/)) | GRC platform | Sales-led | Self-serve, SDK runtime | Runtime instrumentation, not workflow |
| **Saidot** ([saidot.ai](https://www.saidot.ai/)) | AI registry + assurance | Sales-led | SDK, OSS | Open core + dev-first |
| **systima-ai/aiact-docs** ([github](https://github.com/systima-ai/aiact-docs)) | CLI scanner per docs statici | OSS | Runtime telemetria | Runtime, non static — complementare |
| **Comp AI** | OSS compliance broad-scope | OSS + Cloud | AI-Act-specific deep | AI-Act-deep, runtime |

**Sintesi competitiva**: nessun concorrente combina (a) `pip install` self-serve
+ (b) AI Act-first deep mapping + (c) EU-hosted by default + (d) trust center
pubblico + (e) sub-$100/mese starting tier. Quel set è AnnexKit.

---

## 13. Rischi e mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| LangSmith/Langfuse aggiungono modulo AI Act | Media | Alto | Vai veloce. Brand "AI Act-first" va stabilito in 6 mesi. Open-source per moat di community |
| AI Act enforcement viene posticipato/ammorbidito | Bassa | Alto | Pipeline serve comunque per audit interni, SOC2 evidence, cliente enterprise checks. Pivot opzionale verso CRA SBOM (Idea #2 dal report) |
| Standard CEN-CENELEC slittano oltre il previsto | Media | Medio | La pipeline produce evidenze tecniche valide in ogni caso |
| Adozione italiana lenta | Alta | Basso | Targeting primario non-italiano (DACH, UK, Nordici). IT è beachhead, non target |
| Confident AI viene a fare AI Act seriamente | Media | Alto | Loro sono brand "evals", non "compliance". Ma saranno minaccia in M6+. Mitigazione = community + integrazioni difficili da copiare |
| Solo founder burnout | Alta | Critico | Time-box rigido (35h/sett dopo M2). Preferire qualità su velocità dopo MVP |
| Pricing troppo basso | Media | Medio | $49 è ancorato a cap dell'IndieMaker — facile alzare a $99 a M6 se la traction lo permette |
| Customer churn dopo che ottengono il PDF Annex IV una volta | Alta | Medio | Posiziona come *vivente* (rigenerato a ogni release/incident) + post-market monitoring (Article 72) come hook recurring |
| Auditor reali contestano il PDF generato | Media | Critico | Disclaimer chiaro: "evidence collection, not legal advice". Partnership con 1-2 studi legali per blessing del template (M9-12) |
| Enterprise buyer chiede SOC2 prima di firmare | Alta | Medio | M10 milestone esplicito |
| Concorrente OSS aggressivo (es. fork di Langfuse con AI Act mapping) | Bassa | Alto | Open-core community + integrazioni verticali profonde (LangChain, LlamaIndex, Vercel AI) |

---

## 14. Domande aperte (decisioni da prendere)

Queste sono decisioni che vanno prese **prima di scrivere codice**. Mettile
in TODO/issue e datti deadline esplicita.

1. **Licenza SDK**: MIT (massima adozione, US enterprise comfortable) o
   AGPLv3 (forza self-hosters a contribute back)?
   *Raccomandazione preliminare*: **MIT sul SDK**, AGPLv3 sul backend
   collector. Pattern proven da PostHog, Sentry.

2. **Backend collector self-hostable da day-1 o cloud-only inizialmente**?
   *Raccomandazione*: cloud-only fino a M3, self-host docs da M3, Helm
   chart Enterprise da M7. Permette iterazione rapida senza pressione di
   compatibility burden.

3. **Pricing per span vs per system vs flat**?
   *Raccomandazione*: flat con quota generosa. Per-span pricing scoraggia
   adozione.

4. **Beachhead segment**: SaaS B2B con LLM, AI-first startups, financial
   services regolati, public sector EU?
   *Raccomandazione*: SaaS B2B con LLM (più numeroso, conversion path più
   chiaro). Financial services come tier 2 (richiede enterprise self-host).

5. **Branding**: "AnnexKit" + tagline `AI Act compliance pipeline for
   developers` o naming più technical (`aiact-collector`, `eu-ai-trace`)?
   *Raccomandazione*: AnnexKit (memorable, brandabile, dominio disponibile).

6. **Posizione di Konformia attuale**: continua MVP per PMI italiane in
   parallelo o pause finché AnnexKit ha traction?
   *Raccomandazione*: pausa l'outreach attivo per 60 giorni per concentrarsi
   su AnnexKit MVP. Riattiva al M3 con messaging "Konformia by AnnexKit"
   (Italian instance of the broader product).

7. **Partnership studio legale**: cercare uno studio italiano/EU come
   advisor early-on (no equity, ma "powered by AnnexKit, validated by
   <studio>" sul trust center)?
   *Raccomandazione*: sì, da M3 in poi quando hai customer evidence di
   bisogno.

8. **AI advisor LLM provider primario**: Mistral La Plateforme (EU-hosted,
   data residency story chiara) o Anthropic Claude (qualità superiore ma US)?
   *Raccomandazione*: Mistral primario per coerenza EU residency. Anthropic
   Anthropic Claude come fallback.

---

## 15. Prossimi passi concreti — checklist questa settimana

### Lunedì-Martedì: validazione prima del codice
- [ ] Compra `annexkit.dev` e `annexkit.eu` (15 min, ~$30/anno).
- [ ] Crea repo GitHub `annexkit/annexkit` privato per ora; pubblicalo a Giorno 7.
- [ ] Riserva nome PyPI `annexkit` (registrati come maintainer, upload 0.0.1
      placeholder per blocco squatting).
- [ ] Riserva handle Twitter/X `@annexkit_dev`.
- [ ] Decisioni delle domande aperte sezione 14 — scrivi le risposte in
      `docs/decisions.md` di AnnexKit.

### Mercoledì: spike tecnico
- [ ] Branch nuova in Konformia: `feature/annexkit-spike`. NON è ancora
      pivot. È spike per validare riuso.
- [ ] Implementa decorator `@track` minimo che cattura args + output e
      stampa span su stdout (no collector ancora).
- [ ] Verifica che Konformia classifier funzioni come funzione pura
      `classify(metadata) -> tier`. Se sì, il riuso è confermato.

### Giovedì-Venerdì: scaffolding
- [ ] Inizia Giorno 1-2 della roadmap MVP (Sezione 7).

### Weekend: messaging
- [ ] Scrivi homepage hero text (max 15 parole).
- [ ] Scrivi README quickstart 3 righe.
- [ ] Definisci 5 esempi concreti di "AI system high-risk Annex III" da
      menzionare in marketing copy (HR screening, credit scoring, fraud
      detection, biometric verification, education assessment).

### Lunedì successivo: Giorno 3 della roadmap MVP
Continua come da Sezione 7 (Giorno 3-7 in 5 giorni di lavoro effettivo).

---

## Appendice A — Riferimenti regolamentari chiave

- **Regolamento (UE) 2024/1689** — AI Act testo completo
- **Article 11** — Documentazione tecnica
- **Article 12** — Logging
- **Article 13** — Transparency & information to deployers
- **Article 14** — Human oversight
- **Article 15** — Accuracy, robustness, cybersecurity
- **Article 16** — Obligations of providers
- **Article 17** — Quality management system
- **Article 72** — Post-market monitoring
- **Annex III** — High-risk AI systems (lista categorie)
- **Annex IV** — Technical documentation (9 punti)
- **L. 132/2025** — Legge italiana di adattamento
- **AgID linee guida** — Per pubblica amministrazione italiana

## Appendice B — Riferimenti tecnici

- OpenTelemetry GenAI Semantic Conventions:
  https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OTLP HTTP spec:
  https://opentelemetry.io/docs/specs/otlp/
- CycloneDX SBOM format (per CRA module M6):
  https://cyclonedx.org/
- Sigstore (signing):
  https://www.sigstore.dev/

## Appendice C — Bibliografia di mercato

- [EU-Startups Italian tech 2026](https://www.eu-startups.com/2026/02/from-milan-to-liguria-10-of-the-most-promising-italian-startups-shaping-the-next-tech-cycle/)
- [Tracxn Italy 2026](https://tracxn.com/d/geographies/italy/)
- [Indie Hackers — solopreneur SaaS 2025](https://www.indiehackers.com/post/if-i-had-to-start-a-saas-from-scratch-in-2025-i-d-do-this-1b828afc53)
- [SaaSRanger Micro-SaaS Reality](https://saasranger.com/blog/micro-saas-revenue-reality-what-1000-founders-actually-earn/)
- [Sapphire Ventures — vertical AI markets](https://sapphireventures.com/blog/the-biggest-vertical-ai-markets-are-hiding-in-plain-sight/)
- [VenVera — best AI Act compliance software](https://venvera.com/best/eu-ai-act-compliance-software/)
- [TrustCloud — Trust Centers replace questionnaires](https://www.trustcloud.ai/trust-assurance/how-trust-centers-and-ai-are-replacing-security-questionnaires-and-accelerating-b2b-sales/)
- [Lyceum — EU data residency AI](https://lyceum.technology/magazine/eu-data-residency-ai-infrastructure/)
- [SoftwareSeni — sovereign cloud mandatory](https://www.softwareseni.com/dora-nis2-and-the-eu-ai-act-are-making-sovereign-cloud-mandatory-for-some-workloads/)
- [Ritz Herald — EU cloud compliance 2026](https://ritzherald.com/eu-cloud-compliance-2026-how-to-build-for-gdpr-nis2-dora-and-the-ai-act/)

---

**Disclaimer**: questo documento è strategico e tecnico, non legale.
AnnexKit (e Konformia) non è uno studio legale. Le interpretazioni
dell'AI Act qui contenute riflettono la migliore comprensione tecnica
del founder + ricerca pubblica al 2026-05-07 e devono essere validate
con consulente legale prima di affermazioni pubbliche di conformità.
