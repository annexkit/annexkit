# AnnexKit — Cos'è e come funziona

> Guida progressiva per chi parte da zero. Sei livelli, dal "non so niente" al
> "lo capisco come un ingegnere senior". Leggi in ordine. Dopo l'ultimo
> livello sei in grado di rispondere a qualsiasi domanda tecnica o
> commerciale che ti faranno su AnnexKit.

---

## TL;DR (il prodotto in tre frasi)

AnnexKit è uno strumento per sviluppatori che integrano l'intelligenza
artificiale nelle loro applicazioni. Quando l'EU AI Act entra in piena
applicazione (2 agosto 2026), tutte le aziende che usano AI per decisioni
"importanti" — ad es. screening CV, pre-screen prestiti, sistemi di
sicurezza, etc. — devono produrre documentazione tecnica obbligatoria
("Annex IV") da mostrare agli auditor. AnnexKit fa quella documentazione
**automaticamente**, partendo da una sola riga di codice (`@track`)
aggiunta dal developer alla propria funzione AI.

Il loop completo, in tre comandi:

```
pip install annexkit         (1) installa la libreria
@track on your_function      (2) decora la funzione che usa l'AI
GET /annex-iv?format=pdf     (3) ricevi il PDF Annex IV
```

---

## Livello 1 — Il mondo in cui AnnexKit vive

*Questo livello assume zero conoscenza tecnica e zero conoscenza legale.
Lo leggi e capisci l'opportunità.*

### 1.1 Cos'è l'EU AI Act?

L'AI Act è la legge UE n. 2024/1689, approvata dal Parlamento Europeo
nel 2024. Entra in vigore in modo scaglionato:

- **2 agosto 2025**: GPAI (modelli AI generali, tipo GPT-4) sono già
  obbligati a rispettare alcuni requisiti.
- **2 agosto 2026**: piena applicabilità per i sistemi "high-risk".
- **2 agosto 2027**: piena applicabilità per sistemi high-risk integrati
  in prodotti regolati (medical devices, automotive, etc.).

Sanzioni fino a **€35M o 7% del fatturato globale annuo**, qualsiasi sia
maggiore. Per Apple sarebbe ~€26 miliardi. Per una scaleup italiana
da €5M di fatturato sarebbe €350K — abbastanza da chiudere bottega.

### 1.2 Cosa cambia per le aziende?

Se la tua azienda usa AI per fare decisioni in queste aree, sei
classificato **"high-risk"** sotto l'Annex III dell'AI Act:

- **Educazione e formazione professionale** — es. sistema che valuta
  esami online.
- **Occupazione e gestione del personale** — es. screening CV, scoring
  candidati per promozioni.
- **Servizi essenziali** — es. credit scoring, eligibility per
  assicurazioni, pre-screening prestiti.
- **Forze dell'ordine** — es. analisi probatoria automatica.
- **Migrazione, asilo, controllo frontiere** — es. valutazione
  domande di asilo.
- **Giustizia e processi democratici** — es. supporto decisionale
  giudiziario.
- **Identificazione biometrica** — es. riconoscimento facciale (dove
  non è prohibito).
- **Infrastrutture critiche** — es. sistemi che gestiscono reti
  elettriche, acqua, traffico.

Se rientri in una di queste categorie, l'AI Act ti obbliga a:

1. **Classificare il sistema** (Article 6 + Annex III).
2. **Produrre documentazione tecnica** (Article 11 + Annex IV — le 9
   sezioni che AnnexKit genera automaticamente).
3. **Loggare il funzionamento** (Article 12 — ogni invocazione del
   modello deve essere registrata in modo tamper-evident).
4. **Garantire trasparenza** (Article 13 — gli utenti devono sapere
   che stanno interagendo con un AI).
5. **Garantire sorveglianza umana** (Article 14 — non puoi affidare
   decisioni automatiche al 100%, deve esserci un umano nel loop).
6. **Monitoraggio post-mercato** (Article 72 — devi continuare a
   tracciare il sistema dopo il deployment).
7. **Dichiarazione UE di conformità** (Article 47 — un documento
   firmato dal tuo legale che dichiara che hai fatto tutto il sopra).

### 1.3 Cosa fanno le aziende oggi?

Tre comportamenti che osserviamo:

| Strategia | % aziende | Risultato |
|---|---|---|
| **Niente** | ~95% | Aspettano che il regolatore arrivi. Rischiano sanzioni grosse. |
| **Manuale** | ~4% | Un dev (3 settimane) + un avvocato (1 settimana) per ogni sistema AI. ~€10-15K per sistema. |
| **Tool enterprise** | ~1% | Comprano Credo AI o Holistic AI a $200K-500K/anno. Solo grandi corporate. |

Il **gap di mercato**: tutto ciò che è in mezzo. PMI italiane, scaleup
tedesche, startup AI con LLM in prod — non possono pagare $200K/anno e
non vogliono perdere 4 settimane interne per ogni sistema. Hanno
bisogno di un approccio "developer-first": qualcosa che si installa
con `pip install`, costa €49/mese, e produce il PDF Annex IV in
automatico.

### 1.4 Il perché di AnnexKit

Tre vincoli che il prodotto rispetta e nessun altro tool fa
contemporaneamente:

1. **Self-serve** — niente venditori, niente "richiedi demo". Provi
   il prodotto, paghi se ti piace.
2. **Developer-first** — `pip install` + decorator, non un workflow
   che chiede agli avvocati di compilare un form.
3. **EU-hosted** — Hetzner Falkenstein per l'hosting, Mistral La
   Plateforme (Parigi) per le chiamate LLM. Niente AWS US, niente
   OpenAI per dati sensibili. Post-Schrems II + post-CLOUD Act
   questo è un vincolo reale per i clienti EU.

---

## Livello 2 — La storia di Mario (esempio concreto)

*Questo livello ti porta dal capire l'opportunità al capire come si
usa il prodotto, attraverso un esempio realistico.*

### 2.1 Mario, il fondatore

Mario ha 32 anni, vive a Milano, fa il CTO di una startup HR-tech che
usa OpenAI gpt-4o per fare screening dei CV in arrivo. Il suo prodotto
si chiama "TopTalent" e ha 50 clienti aziendali italiani che gli pagano
€500/mese per ricevere shortlist di candidati.

A ottobre 2025 Mario riceve un'email da uno dei suoi clienti più grossi:
*"Salve Mario, dato l'AI Act, ci servono i documenti tecnici Annex IV
del vostro sistema entro fine 2025 per il nostro audit interno.
Allegate per favore il PDF + classificazione di rischio."*

Mario non sa cosa sia l'Annex IV. Cerca su Google. Capisce: deve
produrre 9 sezioni di documentazione tecnica per il sistema di
screening CV, classificarlo (è "alto rischio" sotto Annex III §4
employment), e spedirlo al cliente. Non avendo budget per un consulente
e non avendo tempo da perdere, cerca uno strumento.

### 2.2 Quello che Mario fa concretamente con AnnexKit

**Giorno 1**:

```bash
pip install annexkit
```

Aggiunge una riga al codice del suo CV-screener:

```python
from annexkit import track

@track(
    system_id="cv-screener",
    risk_tier="auto",
    purpose="Pre-screen incoming CVs and produce ranked shortlist for human recruiters."
)
def score_cv(candidate_data: dict) -> dict:
    response = openai.chat.completions.create(...)
    return parse_scoring_response(response)
```

**Giorno 2**:

Mario va sulla dashboard AnnexKit (annexkit.dev), si registra, riceve
una API key. La mette nelle env var della sua app. Da ora in poi, ogni
volta che `score_cv()` viene chiamata in produzione, AnnexKit registra
silenziosamente:

- Quale modello è stato usato (gpt-4o version 2024-11-20)
- Hash SHA-256 del CV in input (mai il testo in chiaro, privacy-preserving)
- Hash SHA-256 della risposta del modello
- Latenza, errori
- Chi ha invocato la funzione (loan_officer / candidate / api_caller)

**Giorno 3**:

Mario fa una chiamata API per dichiarare formalmente il suo sistema:

```bash
curl -X PUT https://collector.annexkit.dev/api/v1/systems \
  -H "Authorization: Bearer ak_..." \
  -d '{
    "system_id": "cv-screener",
    "purpose": "Pre-screen incoming CVs...",
    "annex_iii_categories": ["annex3_4_employment"],
    "provider_info": {
      "legal_name": "TopTalent S.r.l.",
      "address": "Via Manzoni 1, Milano",
      "country": "IT",
      "system_version": "v3.2.0",
      "software_environment": "Python 3.13, FastAPI, OpenAI gpt-4o",
      "validation_methods": "Holdout test set di 500 CV...",
    }
  }'
```

AnnexKit risponde immediatamente con la classificazione automatica:
**HIGH RISK**, sotto Annex III §4 "Employment and workers management".

**Giorno 21** (dopo 3 settimane di traffico in produzione):

Quando il cliente chiede il PDF, Mario fa:

```bash
curl -O https://collector.annexkit.dev/api/v1/systems/cv-screener/annex-iv?format=pdf
```

Riceve un PDF di ~70KB, ~30 pagine, con:

- **Cover page** con badge "HIGH RISK / ALTO RISCHIO" rosso
- **Executive summary** auto-generato: *"Tra il 1 ottobre e il 21
  ottobre 2025, il sistema ha registrato 1.247 invocazioni via OpenAI
  gpt-4o, con un error rate del 0,32%. Il sistema è currently active..."*
- **Sezione 1 — Descrizione generale**: scopo, ID, GPAI flag, nome
  legale TopTalent S.r.l., indirizzo Milano, versione v3.2.0, ambiente
  Python+FastAPI+gpt-4o
- **Sezione 1.4 — Classificazione di rischio**: HIGH, regola triggata
  `annex3_4_employment` con descrizione bilingue EN/IT
- **Sezione 2 — Modelli usati**: tabella con OpenAI gpt-4o
  v2024-11-20, 1.247 invocazioni, prima vista, ultima vista
- **Sezione 3 — Article 12 logging**: stats reali della telemetria
- **Sezione 3.3 — Latency performance**: p50/p95/p99 per finestre 24h,
  7d, 30d, all-time
- **Sezione 5 — Storico modifiche**: dal log di audit (quando il sistema
  è stato dichiarato, quando il `purpose` è stato aggiornato)
- **Sezione 8 — Post-market monitoring**: error breakdown per classe
- **Sezione 9 — Article 13 informazioni per deployer**: cosa il cliente
  finale (il deployer) deve sapere — il sistema è high-risk, ricade
  sotto Article 26 deployer obligations
- **Appendix A — Compliance gap analysis**: tabella che dice
  "§1.1 Purpose: AUTO ✓", "§4 Risk management: MANUAL — provider
  input required", "§7 EU declaration of conformity: MANUAL — your
  legal counsel signs"
- **Appendix B — Glossario**: tutti i termini tecnici
- **Appendix C — Sample evidence**: 10 trace_id reali con cui
  l'auditor può fare spot check
- **Appendix D — Sign-off**: linee per la firma del provider e
  del compliance officer

Mario manda il PDF al cliente. Il cliente lo accetta. Mario ha
risparmiato 3-4 settimane di lavoro suo + €4-8K che avrebbe pagato a
un consulente.

### 2.3 Cosa AnnexKit ha fatto sotto il cofano

In automatico, senza che Mario abbia dovuto:

- ✓ Implementare logging strutturato compliant con Article 12
- ✓ Hashare ogni input/output (privacy-preserving)
- ✓ Mappare il suo sistema a una categoria Annex III specifica
- ✓ Tenere un audit log append-only delle modifiche
- ✓ Aggregare 3 settimane di telemetria in metriche compatibili con
  Article 72 (post-market monitoring)
- ✓ Renderizzare un PDF audit-grade con cover, executive summary,
  9 sezioni, 4 appendici, sign-off
- ✓ Esporre una pagina pubblica `https://annexkit.dev/trust/toptalent`
  che il cliente di Mario può visitare per "vedere" che TopTalent
  ha un compliance setup serio

### 2.4 Cosa Mario NON ha dovuto fare

- Leggere il testo dell'AI Act
- Capire cos'è l'Annex IV (l'ha visto pronto)
- Pagare un consulente legale per la documentazione tecnica
- Implementare log Article 12 a mano
- Costruire un sistema di classificazione del rischio
- Gestire la trasparenza Article 50 (la pagina trust pubblica lo fa)

Tempo totale di Mario: ~3 ore di setup, distribuite su 3 settimane
(perché serve traffico reale per popolare le statistiche).

---

## Livello 3 — Cos'è AnnexKit, tecnicamente

*Da qui in poi richiede minime conoscenze di sviluppo software (cos'è
una libreria, cos'è un'API, cos'è un database). Se non le hai, leggi
il livello 1+2 e torna qui dopo aver chiesto a un dev di amico di
spiegarti i termini.*

### 3.1 L'architettura, in un'immagine testuale

```
┌────────────────────────────────────────────────────────────┐
│  L'APP DEL CLIENTE                                          │
│                                                             │
│   from annexkit import track                                │
│                                                             │
│   @track(system_id="cv-screener", risk_tier="auto")        │
│   def score_cv(candidate):                                  │
│       return openai.chat.completions.create(...)            │
└─────────────────────────┬──────────────────────────────────┘
                          │ HTTPS POST /api/v1/spans
                          │ (input/output hashed, mai plaintext)
                          ▼
┌────────────────────────────────────────────────────────────┐
│  COLLECTOR ANNEXKIT  (FastAPI, hosted Hetzner Falkenstein)  │
│                                                             │
│   - Riceve gli "spans" (uno per chiamata AI)                │
│   - Verifica auth (Bearer ak_...)                           │
│   - Valida (Pydantic strict)                                │
│   - Persiste su Postgres (append-mostly + audit-only)       │
│   - Classifica risk_tier="auto" via rules engine             │
│   - Ritorna 202 Accepted                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────────┐
│  POSTGRES 16  (con trigger APPEND-ONLY su audit_logs)       │
│                                                             │
│   - tenants (ogni cliente AnnexKit)                         │
│   - api_keys (HMAC-hashed, mai plaintext)                   │
│   - ai_systems (dichiarazioni: cos'è il sistema)            │
│   - spans (ogni invocazione AI: hashes, latency, errors)    │
│   - audit_logs (chi ha fatto cosa, quando — IMMUTABILE)     │
└─────────────────────────────────────────────────────────────┘
        │                                          │
        │                                          │
        ▼                                          ▼
┌──────────────────────┐               ┌──────────────────────────┐
│  ANNEX IV GENERATOR  │               │  TRUST CENTER PUBBLICO    │
│  (Jinja + WeasyPrint)│               │  (Next.js 16 SSR)         │
│                      │               │                           │
│  GET /annex-iv?      │               │  /trust/<slug>            │
│    format=pdf        │               │  /trust/<slug>/systems/   │
│                      │               │    <system_id>            │
│  → PDF 70KB          │               │                           │
│  → MD 19KB           │               │  Sensitive fields         │
│                      │               │  redacted (whitelist).    │
└──────────────────────┘               └──────────────────────────┘
```

### 3.2 Tre componenti, in dettaglio

#### A. Il SDK Python (`pip install annexkit`)

Una libreria Python di ~250 righe di codice, MIT licensed. Espone:

- `@track(system_id, risk_tier, purpose)` — decorator. Funziona su
  funzioni `def` e `async def` (auto-detect).
- `annexkit.session(...)` — context manager per casi multi-step (es.
  RAG con retrieval di documenti).
- `annexkit.configure(api_key, collector_url, ...)` — config
  programmatica.
- `annexkit.flush()` — drena il buffer prima di shutdown.

Quando il decorator avvolge la tua funzione, registra:

- `trace_id` + `span_id` (identificatori OpenTelemetry-compatibili)
- `system_id` + `purpose` (li dichiari tu)
- `started_at`, `ended_at`, `latency_ms`
- `model_provider`, `model_name`, `model_version` (se settati)
- `input_hash` (SHA-256 dell'input — **mai il plaintext**)
- `output_hash` (SHA-256 dell'output — **mai il plaintext**)
- `input_chars` / `output_chars` (lunghezza, utile per audit)
- `error` (se la funzione ha lanciato un'eccezione)
- `sources` (lista di documenti retrieval, se sei un sistema RAG)
- `user_role` (es. "loan_officer", "customer" — Article 14 oversight)
- `metadata` (dict free-form per i tuoi tag custom)

L'output finisce in stderr come JSON (default, comodo per testing) o
viene POSTato al collector (quando setti `ANNEXKIT_API_KEY`).

#### B. Il collector backend

Una API FastAPI in Python 3.13 con SQLAlchemy 2.0 async sopra
Postgres 16. AGPL-3.0 licensed. Endpoint principali:

| Endpoint | Cosa fa |
|---|---|
| `POST /api/v1/spans` | Riceve uno span dal SDK. Auth Bearer. 202 Accepted. |
| `PUT /api/v1/systems` | Dichiarazione di un sistema AI (idempotente). Triggera la classificazione automatica. |
| `GET /api/v1/systems` | Lista i sistemi del tenant autenticato. |
| `GET /api/v1/systems/{id}` | Dettaglio di un sistema (con reasoning del classifier). |
| `GET /api/v1/systems/{id}/annex-iv?format=md\|pdf` | Genera l'Annex IV completo. |
| `GET /api/v1/trust/{slug}` | **Pubblico**, no auth. Overview tenant per il trust center. |
| `GET /api/v1/trust/{slug}/systems/{id}` | **Pubblico**, redacted. Dettaglio sistema con sensitive fields rimossi. |

Il collector NON contiene business logic LLM. È un sistema di
ingestion + storage + rendering. Tutta la "intelligenza" è nel
classifier deterministico (vedi 3.3).

#### C. Il classifier (cuore del prodotto)

Un Python module di ~150 righe (`risk_engine.py`) con UNA funzione
pubblica: `classify(answers: dict) → Verdict`.

Le regole sono caricate da un file JSON statico (`annex_iii.json`) che
codifica:

- 8 categorie Annex III (employment, essential services, etc.)
- 8 pratiche prohibite Article 5 (social scoring, manipulation, etc.)
- 4 trigger di trasparenza Article 50 (chatbot interaction, deepfake, etc.)

L'algoritmo:

```
1. Se ANY pratica prohibita è triggerata → tier = UNACCEPTABLE
2. Se ANY categoria Annex III è triggerata → tier = HIGH
3. Se ANY trigger trasparenza è triggerato → tier = LIMITED
4. Altrimenti → tier = MINIMAL
```

**Mai declassifica**. Una volta che un sistema è `HIGH`, l'engine non
può tornare indietro a `LIMITED`. Questa è una proprietà
non-negoziabile: garantisce che la legge sia rispettata anche se
qualcuno (per errore o malizia) prova a mascherare un sistema
high-risk come limited.

LLM (Mistral) può solo **suggerire** che un sistema potrebbe rientrare
in più categorie di quanto dichiarato — mai dire "potresti scendere di
tier".

---

## Livello 4 — I principi non-negoziabili (perché abbiamo fatto certe scelte)

*Questo livello ti permette di spiegare il prodotto a un avvocato o a
un investitore, perché capisci le ragioni delle scelte di design.*

I sette principi che governano ogni linea di codice in AnnexKit. Ogni
PR che li viola viene rifiutato. Sono codificati in `CLAUDE.md`:

### 4.1 Risk Engine deterministico

**Cosa**: la classificazione del rischio è guidata da regole, non da
un LLM. Un LLM può **suggerire** ma non **decidere** o **declassificare**.

**Perché**: la legalità deve essere prevedibile. Se un cliente fa la
stessa dichiarazione due volte e riceve due tier diversi, non può
fidarsi del prodotto. Inoltre, un LLM "creativo" potrebbe declassificare
un sistema high-risk in limited per "comodità" — questo è il bug
catastrofico che chiude la nostra credibilità in un giorno.

**Come**: rules JSON statiche + `classify()` puro Python + hard guard:
una volta che il tier è alto, non scende mai.

### 4.2 Audit log append-only

**Cosa**: la tabella `audit_logs` non può essere modificata o
cancellata. Mai. Da nessun codice path. Da nessun amministratore.

**Perché**: gli auditor devono potersi fidare che i log non sono stati
manipolati post-hoc. Se un cliente potesse riscriversi la storia,
l'audit non ha valore.

**Come**: 3 layer di defense-in-depth:
1. Service layer (`audit_service.py`) espone solo `record()` (insert).
2. No repository / API espone update/delete.
3. **Trigger Postgres** che lancia un'eccezione se qualcuno prova
   `UPDATE audit_logs` o `DELETE FROM audit_logs` — anche da `psql`
   diretto come superuser.

**Verificato live**:
```sql
UPDATE audit_logs SET action = 'tampered' WHERE id = 1;
ERROR:  audit_logs is append-only; UPDATE is not allowed
```

### 4.3 EU data residency

**Cosa**: l'hosting è in Europa, le chiamate LLM avvengono in Europa,
nessun servizio US-only tocca dati personali o telemetria.

**Perché**: post-Schrems II, post-CLOUD Act, i clienti EU hanno
ragione di temere che i dati ospitati negli US (anche su "AWS Frankfurt")
siano accessibili al governo americano. Per un prodotto di compliance
EU questo è un differenziatore non superficiale: i nostri concorrenti
US (Credo AI, Holistic AI, Vanta) sono headquartered negli US e quindi
soggetti al CLOUD Act per design.

**Come**: hosting su Hetzner Cloud (Falkenstein, Germania), LLM advisor
via Mistral La Plateforme (Parigi), niente AWS / GCP / Azure US,
niente OpenAI per dati sensibili (solo per la classificazione
ambigua, e solo come "advisor").

### 4.4 Privacy-by-default nei spans

**Cosa**: il SDK NON manda mai il plaintext degli input/output dell'LLM.
Solo hash SHA-256.

**Perché**: i prompt LLM contengono dati utente (CV con nomi, prestiti
con SSN, query con info personali). Se trasmettessimo plaintext al
collector AnnexKit, saremmo i primi a leakarli — un disastro di privacy.

**Come**: il decorator hashes l'input (e l'output) con SHA-256 prima
di trasmetterlo. Quello che il collector riceve e persiste è un digest
hex di 64 caratteri, irriversibile.

**Cosa puoi fare con un hash**: dimostrare che due invocazioni hanno
visto lo stesso input. Ricostruire un trail di evidenze. NON: vedere
i dati personali.

**Quello che NON facciamo (per ora)**: opt-in al plaintext encrypted-at-rest
per casi di debug. Lo faremo in v0.2 con encryption key per-tenant.

### 4.5 Disclaimer permanente

**Cosa**: ogni superficie UI / PDF / documento che produce output di
compliance dice esplicitamente "AnnexKit is not a law firm /
AnnexKit non è uno studio legale".

**Perché**: AnnexKit produce **evidenze tecniche**, non interpretazione
legale. Se un cliente perdesse causa con un regolatore citando un PDF
AnnexKit, non vogliamo che ci portino in tribunale per "consulenza
legale impropria". L'invarianza fa parte del contratto del prodotto:
generiamo audit-grade tech docs, ma il legale del cliente firma e
interpreta.

**Come**: testo bilingue EN/IT in:
- Cover page del PDF Annex IV
- Footer di ogni pagina del PDF (footer @page CSS)
- Reminder a fine documento
- Trust center pubblico in fondo a ogni pagina
- README + CONTRIBUTING + SECURITY

### 4.6 Thin controllers, fat services + types ovunque

**Cosa**: i route handler FastAPI fanno solo validation + dispatch.
Tutta la business logic vive in `app/services/`. Ogni request/response
ha un Pydantic schema con `extra="forbid"`. Type hints obbligatori.

**Perché**: separation of concerns + testability. Una route che apre
una connessione DB direttamente è un bug perché non si testa senza
docker. Un service puro è una funzione asincrona che si testa con un
in-memory SQLite.

**Come**: review checklist nel CONTRIBUTING. Ogni PR che fa business
logic in route handler viene rifiutato.

### 4.7 Cross-tenant isolation

**Cosa**: il dato di un tenant non può essere letto, mutato, o
falsificato dal codice eseguito per un altro tenant. Mai.

**Perché**: per un prodotto di compliance EU questo è il bug fatale.
Se mai il dato di un cliente fosse leakato a un altro tramite un bug,
è game over per la credibilità del prodotto.

**Come**: 8 test di isolation (`test_cross_tenant_isolation.py`) che
pinnano il contratto:
- Span POSTed da tenant A è ownato da A (anche se il payload finge
  altro)
- Tenant A non può leggere /api/v1/systems/<sistema-di-B>
- /api/v1/systems list ritorna solo i sistemi del caller
- Trust pages non si cross-pollinano
- 404 sono byte-identical (no info leak via differential errors)

Questi test girano a ogni commit. Se uno fallisce, niente merge.

---

## Livello 5 — Architettura senior eng (le scelte di design)

*Questo livello ti porta al "lo capisco come l'autore". Spiega il
ragionamento dietro le scelte non-ovvie.*

### 5.1 Perché monorepo (vs polyrepo)?

AnnexKit ha 4 pacchetti: `sdk/`, `backend/`, `frontend/`,
`examples/chatbot-openai/`. Tutti in un unico repo.

**Pros del monorepo**:
- Refactor cross-package atomico (es. cambiare lo schema span è una
  PR sola che tocca SDK + backend + tests)
- CI unificata, una sola buildchain
- Un solo issue tracker, un solo PR queue

**Cons che accettiamo**:
- Quando l'SDK va su PyPI, i contributori esterni non possono
  PR-are senza vedere tutto il backend AGPL (rumore).
- Un bug nel frontend non dovrebbe bloccare un release del SDK.

**Quando spliteremo**: quando l'SDK supererà 1000 download/giorno o
avremo >50 contributor esterni — circa M9-M12.

### 5.2 Perché dual license MIT (SDK) + AGPL (backend)?

Stessa scelta che hanno fatto Sentry, PostHog, MinIO, Plausible.

**SDK MIT**: vogliamo che chiunque importi `annexkit` nel suo codebase
proprietario senza pensieri. MIT è il path di minor frizione per la
adoption.

**Backend AGPL-3.0**: vogliamo che chi forka il backend e lo deploya
come servizio pubblico modificato debba ripubblicare le modifiche.
Questo protegge il modello business "managed cloud" da fork
commerciali ostili. AGPL > GPL perché copre anche l'uso "as a service".

**Spazio per dual licensing commerciale**: aziende che vogliono
deployare un backend modificato senza obblighi AGPL possono comprarci
una licenza commerciale (revenue stream secondario, modello Sentry).

### 5.3 Perché Postgres + JSONB (vs MongoDB / DynamoDB)?

Il prodotto è scritto sopra Postgres 16 perché:

1. **ACID transactions**: l'audit log + lo span devono essere scritti
   nella stessa transazione. MongoDB tradizionalmente non offriva
   questo (ora sì, con `$transaction`, ma ricordi che 5 anni fa era
   eventually consistent).
2. **JSONB**: per `provider_info`, `metadata`, `sources` — campi
   semi-strutturati. JSONB di Postgres è quasi MongoDB con JOIN.
3. **Trigger SQL**: per il trigger APPEND-ONLY su `audit_logs`,
   serve qualcosa che giri al DB layer, non al app layer.
4. **Single source of truth**: niente eventual consistency, niente
   replica lag, niente "ho appena scritto ma non lo vedo".
5. **pgvector**: in M5 quando aggiungeremo retrieval-augmented Annex
   IV, useremo embedding vector search. pgvector è già nel deploy.

### 5.4 Perché Next.js 16 + Tailwind 4 (vs solo HTML / vs Astro / vs SvelteKit)?

Frontend per il trust center pubblico. Three driver:

1. **Server-side rendering**: le pagine trust devono essere indicizzate
   correttamente da Google (per SEO sulle landing dei clienti) e
   accessibili senza JS abilitato. Next.js App Router fa SSR di default.
2. **Italian SME mercato beachhead**: Tailwind + componenti puliti =
   estetica "professionale enterprise", non "startup leggera". I
   prospect italiani vedono e si fidano.
3. **Vercel deploy gratuito**: zero infra cost per il frontend pubblico
   (Hetzner per il backend, Vercel free tier per il front). Riduciamo
   il burn.

Tailwind 4 anziché v3 perché v4 elimina il file `tailwind.config.ts`
(theme via CSS @theme) e ha PostCSS plugin diretto. Meno configurazione,
meno superfici di errore.

### 5.5 Trade-off accettati per v0.1

Scelte deliberatamente rinviate a v0.2+:

| Cosa rinviato | Perché ora ok | Quando lo aggiungo |
|---|---|---|
| Rate limiting su `/api/v1/trust/*` | Cloudflare default rate limit copre | M2 con `slowapi` |
| Frontend test suite | `next build` + `tsc strict` cattura regressioni grosse | M3 con Vitest |
| Multi-region deploy | Single Hetzner VPS sufficiente per <1K paying customers | M6 con read replicas |
| OAuth / SSO | API key Bearer copre dev use-case | M4 con Auth0 / Keycloak |
| Mistral advisor | Deterministic engine sufficiente per declarations chiare | M2 (Day 4.5) |
| Public Annex IV PDF download | Risk di leak di info sensibile | M3 con redazione esplicita |
| Stripe / billing | Free + invoice manuale per primi 50 clienti | M2 quando arriva pricing tier |
| LangChain / LlamaIndex integration | Diretto con OpenAI SDK già dimostrato | M2 |
| TS/JS SDK | Python copre 70% del mercato AI dev | M3 |

---

## Livello 6 — Roadmap (la traiettoria da qui in avanti)

*Questo livello chiude il cerchio: capisci dove siamo e dove andremo.*

### 6.1 Dove siamo oggi (Day 7 code-side, fine 2025/inizio 2026)

- 14 commit
- 7 giorni di MVP completi
- 113 test green (64 backend + 48 SDK + 1 PDF skipped sull'host)
- Audit pass eseguito (security + correctness + frontend resilience)
- Ready per launch user-side (PyPI publish + dominio + demo video +
  Hetzner deploy + HN post)

### 6.2 M1 (mese 1): Soft launch

- PyPI publish: `pip install annexkit==0.1.0` funziona davvero
- Dominio annexkit.dev + landing page Vercel
- Demo video 90 secondi (`make demo-seed` → screencast)
- Hetzner VPS €5-10/mese, deploy `docker compose up`
- Cloudflare DNS + SSL gratuito
- Show HN post — 1 evento, prepara il titolo + le FAQ
- LinkedIn launch post + 5 amici dev italiani che ritwittano
- **Metrica target**: 100-300 GitHub stars, 5-15 sign-up, 1-3 paying

### 6.3 M2-M3: Productization

- Mistral advisor (Day 4.5): suggerisce categorie ambigue dal `purpose`
- LangChain + LlamaIndex integration (decorator wrapper)
- Rate limiting su `/api/v1/trust/*` con slowapi
- TS/JS SDK (port di base del Python SDK)
- Trust badge embeddable: i clienti incollano `<script>` nel loro footer
- Frontend test suite (Vitest)
- First case study scritta + pubblicata
- **Metrica target**: $1K-3K MRR, 25-60 paying customers

### 6.4 M4-M6: Scale

- SSO (Google + GitHub) via Auth0 free tier
- Konformia consumer dashboard: il "frontend italiano" per PMI con UI
  italiana, FAQ in italiano, link a CNDCEC
- Multi-tenancy hardening: audit retention 7 anni, SLA, priority support
- Self-hosted enterprise tier: Helm chart per Kubernetes, license check
- 1-2 partnership con commercialisti italiani (referral 20%)
- **Metrica target**: $5K-10K MRR, 100-200 paying customers, decisione
  raise pre-seed o continuare bootstrap

### 6.5 M7-M12: Compound

- LangSmith / Langfuse importer (per chi ha già osservabilità)
- CRA (Cyber Resilience Act) SBOM module: stesso prodotto, regulation
  diversa, usa lo stesso trust center
- Public benchmark "AI Act readiness score" (PR magnet)
- Conference talk circuit: PyConIT, EuroPython, FOSDEM, AICON
- 5-10 partnership con studi legali italiani (revenue share)
- **Metrica target**: $15K-30K MRR, 300-600 paying customers, primo
  full-time hire (DevRel)

---

## Per concludere

Se hai letto tutto sei in grado di:

- Spiegare cos'è AnnexKit a tua nonna in 30 secondi (livello 1)
- Spiegarlo a un imprenditore italiano in 2 minuti (livello 2)
- Spiegarlo a un dev tecnico in 5 minuti (livello 3)
- Spiegare le scelte di design a un avvocato/CTO (livello 4)
- Spiegare l'architettura a un investor / advisor (livello 5)
- Discutere la traiettoria del prodotto con un cofounder (livello 6)

Riferimenti per i dubbi:

- **Strategia / mercato / piano 12 mesi**: [docs/ANNEXKIT_PLAN.md](ANNEXKIT_PLAN.md)
- **Come fare soldi / business plan**: [docs/MONETIZZAZIONE.md](MONETIZZAZIONE.md)
- **Invarianti tecniche per chi scrive codice**: [CLAUDE.md](../CLAUDE.md)
- **Quickstart sviluppatore**: [README.md](../README.md)
- **Vulnerabilities + security model**: [SECURITY.md](../SECURITY.md)

Disclaimer finale, perché è il principio più importante:

> AnnexKit is not a law firm / AnnexKit non è uno studio legale. Le
> classificazioni, i PDF Annex IV, le pagine trust che il prodotto
> genera sono **evidenze tecniche** prodotte strumentando il runtime
> dei sistemi AI. **L'interpretazione legale, il sign-off, la
> dichiarazione UE di conformità Article 47 sono responsabilità del
> consulente legale del cliente.** Sempre.
