#!/usr/bin/env python3
"""
generate-architecture-pdf.py — produce two PDF architecture briefs
(English + Italian) summarising the AnnexKit v0.1.x system.

Audience: the founder, preparing for engineering interviews,
investor architecture diligence, or any technical conversation where
"how is this built" comes up.

Usage:
    python3 scripts/generate-architecture-pdf.py

Outputs (to the user's Desktop):
    annexkit-architecture-en.pdf
    annexkit-architecture-it.pdf

Both PDFs share the exact same structure and section ordering; only
the prose is translated. Code samples, table rows that are technical
names, and ASCII diagrams are identical in both languages.

The structure is held in `SECTIONS` — a list of blocks where each
block carries an English version and an Italian version. To update
the doc: edit `SECTIONS`, re-run.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


# ----------------------------------------------------------------------------
# Brand colours — same palette the website ships (Editorial Engineering)
# ----------------------------------------------------------------------------

SAGE = colors.HexColor("#008757")          # accent (light theme)
SAGE_SOFT = colors.HexColor("#d9efe5")     # accent backdrop (badge bg)
INK = colors.HexColor("#1d1809")           # warm near-black body text
INK_MUTED = colors.HexColor("#5d5641")     # muted text
RULE = colors.HexColor("#c9c1ad")          # hairline borders
CANVAS = colors.HexColor("#faf6ee")        # warm cream page background
CODE_BG = colors.HexColor("#f1ece1")       # code block bg


# ----------------------------------------------------------------------------
# Content — every block has an EN + IT variant
# ----------------------------------------------------------------------------

Lang = Literal["en", "it"]


@dataclass
class Heading:
    """Section heading (H1)."""
    en: str
    it: str
    number: int


@dataclass
class Subheading:
    """Subsection heading (H2) inside a section."""
    en: str
    it: str


@dataclass
class Para:
    """Body paragraph. Reportlab markup OK (<b>, <i>, <br/>)."""
    en: str
    it: str


@dataclass
class Code:
    """Code block — same content for both languages."""
    text: str
    caption_en: str = ""
    caption_it: str = ""


@dataclass
class Bullets:
    """Bulleted list — items are pairs (en, it)."""
    items: list[tuple[str, str]]


@dataclass
class KV:
    """Key/value table — first column language-neutral, second column has en+it."""
    rows: list[tuple[str, tuple[str, str]]]
    header_en: tuple[str, str] | None = None
    header_it: tuple[str, str] | None = None


@dataclass
class Note:
    """Small italicised callout."""
    en: str
    it: str


Block = Heading | Subheading | Para | Code | Bullets | KV | Note


# ============================================================================
# THE CONTENT
# ============================================================================

SECTIONS: list[Block] = [
    # ------------------------------------------------------------------------
    # 1. What is AnnexKit
    # ------------------------------------------------------------------------
    Heading(
        number=1,
        en="What is AnnexKit",
        it="Cos'è AnnexKit",
    ),
    Para(
        en=(
            "AnnexKit is a <b>compliance pipeline for the EU AI Act</b> "
            "(Reg. EU 2024/1689). It turns runtime telemetry from "
            "LLM-powered code into audit-ready Annex IV technical "
            "documentation — one decorator on the inference call, a "
            "collector that classifies the AI system against Annex III "
            "risk tiers, an append-only audit log, and a PDF + Markdown "
            "renderer that procurement teams or external auditors will "
            "actually accept."
        ),
        it=(
            "AnnexKit è una <b>pipeline di compliance per l'EU AI Act</b> "
            "(Reg. UE 2024/1689). Trasforma la telemetria runtime di "
            "codice che usa LLM in documentazione tecnica Annex IV pronta "
            "per audit — un decoratore sulla chiamata di inferenza, un "
            "collector che classifica il sistema AI secondo i tier di "
            "rischio Annex III, un audit log append-only, e un renderer "
            "PDF + Markdown che un team procurement o un auditor esterno "
            "accettano davvero."
        ),
    ),
    Subheading(
        en="The problem AnnexKit solves",
        it="Il problema che AnnexKit risolve",
    ),
    Para(
        en=(
            "The EU AI Act enters full force on <b>2 August 2026</b>. "
            "Every team running an LLM in production must produce "
            "evidence for Article 11 (technical documentation), "
            "Article 12 (logging), Article 13 (transparency to deployers), "
            "Article 50 (chatbot disclosure), and Article 72 (post-market "
            "monitoring). Today the buyer faces three options, all bad:"
        ),
        it=(
            "L'EU AI Act entra in piena vigenza il <b>2 agosto 2026</b>. "
            "Ogni team che usa un LLM in produzione deve produrre "
            "evidenze per Articolo 11 (documentazione tecnica), "
            "Articolo 12 (logging), Articolo 13 (trasparenza ai deployer), "
            "Articolo 50 (disclosure chatbot) e Articolo 72 (monitoraggio "
            "post-market). Oggi il buyer ha tre opzioni, tutte pessime:"
        ),
    ),
    Bullets(
        items=[
            (
                "<b>LLM observability</b> (LangSmith, Langfuse, Confident AI) "
                "— solid on tracing, zero AI Act mapping.",
                "<b>LLM observability</b> (LangSmith, Langfuse, Confident AI) "
                "— ottime per tracing, zero mapping verso l'AI Act.",
            ),
            (
                "<b>AI governance platforms</b> (Credo AI, Holistic AI, Saidot) "
                "— full coverage but €100K+/yr, enterprise-sales-led, "
                "US-headquartered.",
                "<b>Piattaforme AI governance</b> (Credo AI, Holistic AI, Saidot) "
                "— coverage completo ma da €100K+/anno, vendite "
                "enterprise-led, con sede USA.",
            ),
            (
                "<b>Manual approach</b> — engineers + lawyers reverse-engineer "
                "Annex IV from application logs, weeks per system.",
                "<b>Approccio manuale</b> — ingegneri + avvocati che "
                "ricostruiscono l'Annex IV dai log applicativi, settimane "
                "per ogni sistema.",
            ),
        ],
    ),
    Para(
        en=(
            "AnnexKit fills the gap: developer-first, self-serve, "
            "EU-hosted, sub-€100/month starting tier, open-core. The "
            "integration is one Python decorator. The output is a PDF "
            "an auditor accepts."
        ),
        it=(
            "AnnexKit copre il gap: developer-first, self-serve, "
            "EU-hosted, tier iniziale sotto €100/mese, open-core. "
            "L'integrazione è un decoratore Python. L'output è un PDF "
            "che un auditor accetta."
        ),
    ),
    # ------------------------------------------------------------------------
    # 2. High-level architecture
    # ------------------------------------------------------------------------
    Heading(
        number=2,
        en="High-level architecture",
        it="Architettura ad alto livello",
    ),
    Code(
        text=(
            "+-------------------------------------------------------------+\n"
            "|  YOUR APPLICATION                                            |\n"
            "|    @annexkit.track(...) on each LLM call                     |\n"
            "+----------------------------+--------------------------------+\n"
            "                             | HTTPS · HMAC-SHA256 auth\n"
            "                             v\n"
            "+-------------------------------------------------------------+\n"
            "|  ANNEXKIT COLLECTOR  (FastAPI · Postgres 16 · EU-hosted)     |\n"
            "|                                                              |\n"
            "|   - Span ingest                  privacy-by-default (SHA-256)|\n"
            "|   - Annex III risk classifier    deterministic rules         |\n"
            "|   - Append-only audit log        Postgres trigger enforces   |\n"
            "|   - Annex IV generator           Markdown + PDF, bilingual   |\n"
            "|   - Public trust page            slug-addressable, redacted  |\n"
            "+----------------------+-----------------+--------------------+\n"
            "                       |                 |\n"
            "                       v                 v\n"
            "              +---------------+   +-----------------+\n"
            "              |  Postgres 16  |   |  Next.js 16     |\n"
            "              |  (audit data) |   |  trust frontend |\n"
            "              +---------------+   +-----------------+"
        ),
        caption_en="The whole product, in one box-and-arrows diagram.",
        caption_it="L'intero prodotto, in un diagramma boxes-and-arrows.",
    ),
    Subheading(
        en="The three architectural invariants",
        it="I tre invarianti architetturali",
    ),
    Bullets(
        items=[
            (
                "<b>The classifier is deterministic.</b> Annex III mapping is "
                "rule-driven (<font face='Courier'>backend/app/data/annex_iii.json</font>). "
                "LLM advisors (planned v0.2) can suggest categories on ambiguous "
                "inputs but the rules can never lower a tier the engine raised.",
                "<b>Il classifier è deterministico.</b> Il mapping Annex III è "
                "rule-driven (<font face='Courier'>backend/app/data/annex_iii.json</font>). "
                "Gli advisor LLM (previsti v0.2) possono suggerire categorie in "
                "casi ambigui, ma le regole non possono mai abbassare un tier "
                "che il classifier ha alzato.",
            ),
            (
                "<b>The audit log is append-only.</b> Three layers of enforcement: "
                "the service layer exposes only a single "
                "<font face='Courier'>record()</font> function; no repository or API "
                "ever calls UPDATE or DELETE; a Postgres trigger raises on any "
                "mutation attempt at the database level.",
                "<b>L'audit log è append-only.</b> Tre layer di enforcement: il "
                "service layer espone solo una funzione "
                "<font face='Courier'>record()</font>; nessun repository o API "
                "chiama mai UPDATE o DELETE; un trigger Postgres solleva un "
                "errore se viene tentata una mutation a livello DB.",
            ),
            (
                "<b>Privacy by default.</b> Inputs and outputs are SHA-256 hashed "
                "by the SDK before they leave the application host. Plaintext "
                "retention is opt-in per AI system, lands in v0.2 with "
                "encryption-at-rest on the collector.",
                "<b>Privacy by default.</b> Input e output vengono hashati "
                "SHA-256 dall'SDK prima di lasciare l'host applicativo. La "
                "retention in plaintext è opt-in per sistema AI, arriva in "
                "v0.2 con encryption-at-rest sul collector.",
            ),
        ],
    ),
    # ------------------------------------------------------------------------
    # 3. Three-package monorepo
    # ------------------------------------------------------------------------
    Heading(
        number=3,
        en="Three-package monorepo",
        it="Monorepo a tre pacchetti",
    ),
    Para(
        en=(
            "Three independently-versioned packages in one git repository, "
            "one deploy cadence. The monorepo enables atomic refactors "
            "across the stack (e.g. adding a span field touches SDK schema, "
            "backend model, frontend display in one PR). The license split "
            "follows the open-core playbook used by Sentry, PostHog, MinIO."
        ),
        it=(
            "Tre pacchetti versionati indipendentemente in un solo repo git, "
            "una cadenza di deploy. Il monorepo permette refactor atomici "
            "attraverso lo stack (es. aggiungere un campo span tocca lo "
            "schema SDK, il modello backend, il display frontend in un'unica "
            "PR). Lo split delle licenze segue il playbook open-core usato "
            "da Sentry, PostHog, MinIO."
        ),
    ),
    KV(
        header_en=("Package", "Stack · License · Role"),
        header_it=("Pacchetto", "Stack · Licenza · Ruolo"),
        rows=[
            (
                "sdk/",
                (
                    "Python 3.10+ · MIT · Published to PyPI as "
                    "<font face='Courier'>annexkit</font>. The <font face='Courier'>"
                    "@track</font> decorator + HTTP exporter + stdout fallback. "
                    "Pydantic 2 + httpx async.",
                    "Python 3.10+ · MIT · Pubblicato su PyPI come "
                    "<font face='Courier'>annexkit</font>. Il decoratore "
                    "<font face='Courier'>@track</font> + HTTP exporter + "
                    "fallback stdout. Pydantic 2 + httpx async.",
                ),
            ),
            (
                "backend/",
                (
                    "Python 3.13 · AGPL-3.0 · FastAPI collector + Annex IV "
                    "generator + trust API. SQLAlchemy 2.0 async, "
                    "Pydantic strict, Alembic migrations.",
                    "Python 3.13 · AGPL-3.0 · FastAPI collector + Annex IV "
                    "generator + trust API. SQLAlchemy 2.0 async, "
                    "Pydantic strict, migrazioni Alembic.",
                ),
            ),
            (
                "frontend/",
                (
                    "Next.js 16 · AGPL-3.0 · Public trust pages + marketing + "
                    "free tools. App Router + Turbopack + React 19 + "
                    "Tailwind 4.",
                    "Next.js 16 · AGPL-3.0 · Trust page pubbliche + marketing + "
                    "tools gratuiti. App Router + Turbopack + React 19 + "
                    "Tailwind 4.",
                ),
            ),
            (
                "examples/",
                (
                    "Python · MIT · End-to-end runnable demos (chatbot-openai, "
                    "test-walkthrough) that exercise SDK + collector + PDF in "
                    "one make-target.",
                    "Python · MIT · Demo end-to-end runnabili (chatbot-openai, "
                    "test-walkthrough) che esercitano SDK + collector + PDF in "
                    "un make-target.",
                ),
            ),
        ],
    ),
    Note(
        en=(
            "Why AGPL on the backend? Same arrangement Sentry / PostHog / "
            "MinIO use: self-host freely, but if you expose modifications "
            "as a network service you must publish your source. Aligns "
            "with the hosted/self-hosted business model."
        ),
        it=(
            "Perché AGPL sul backend? Stessa scelta di Sentry / PostHog / "
            "MinIO: self-host libero, ma se esponi modifiche come servizio "
            "di rete devi pubblicare il sorgente. Allineato col modello "
            "di business hosted/self-hosted."
        ),
    ),
    # ------------------------------------------------------------------------
    # 4. The SDK
    # ------------------------------------------------------------------------
    Heading(
        number=4,
        en="The SDK",
        it="L'SDK",
    ),
    Para(
        en=(
            "Python 3.10+ for broad compatibility (most ML codebases sit "
            "between 3.10 and 3.12). The integration surface is exactly "
            "one symbol — the <font face='Courier'>@track</font> decorator — "
            "with sync/async auto-detection so the same import works on "
            "FastAPI handlers, Celery tasks, and notebook code."
        ),
        it=(
            "Python 3.10+ per compatibilità ampia (la maggior parte delle "
            "codebase ML sta tra 3.10 e 3.12). La superficie di "
            "integrazione è esattamente un simbolo — il decoratore "
            "<font face='Courier'>@track</font> — con auto-detection "
            "sync/async così lo stesso import funziona su handler FastAPI, "
            "task Celery, e notebook."
        ),
    ),
    Code(
        text=(
            "from annexkit import track\n"
            "\n"
            "@track(\n"
            '    system_id="loan-screener",\n'
            '    risk_tier="auto",\n'
            '    purpose="pre-screen credit applications",\n'
            ")\n"
            "def screen(applicant):\n"
            "    return openai.chat.completions.create(\n"
            '        model="gpt-4o-mini",\n'
            '        messages=[{"role": "user", "content": prompt}],\n'
            "    ).choices[0].message.content"
        ),
        caption_en="The entire user-side integration. Span emission is automatic.",
        caption_it="L'intera integrazione lato utente. L'emissione di span è automatica.",
    ),
    Subheading(en="What the SDK does", it="Cosa fa l'SDK"),
    Bullets(
        items=[
            (
                "<b>SHA-256 hashes inputs and outputs</b> at the host before "
                "any network call. Plaintext never leaves the customer's "
                "process by default.",
                "<b>Hash SHA-256 di input e output</b> sull'host prima di "
                "qualunque chiamata di rete. Per default il plaintext non "
                "lascia mai il processo del cliente.",
            ),
            (
                "<b>HMAC-SHA256 authenticated transport</b> to the collector "
                "via httpx async. Bearer-style API key prefixed "
                "<font face='Courier'>ak_</font>, 120 bits of entropy.",
                "<b>Trasporto HMAC-SHA256 autenticato</b> verso il collector "
                "via httpx async. API key Bearer-style con prefisso "
                "<font face='Courier'>ak_</font>, 120 bit di entropia.",
            ),
            (
                "<b>Stdout fallback exporter</b> when no API key is set — "
                "spans print as JSON to stderr. Useful for local development "
                "without the collector running.",
                "<b>Exporter di fallback su stdout</b> quando non è settata "
                "l'API key — gli span vengono stampati come JSON su stderr. "
                "Utile per sviluppo locale senza collector attivo.",
            ),
            (
                "<b>Strict Pydantic 2 schemas</b> on every span. Twelve "
                "fields covering model id, prompt hash, output hash, "
                "latency, user role, retrieval sources, plus tenant "
                "context.",
                "<b>Schemi Pydantic 2 strict</b> su ogni span. Dodici campi "
                "che coprono model id, hash del prompt, hash dell'output, "
                "latenza, ruolo utente, source di retrieval, più il "
                "contesto tenant.",
            ),
            (
                "<b>Custom exporters</b> via a documented base class — drop "
                "in your own destination (OTLP, Kafka, S3) without forking.",
                "<b>Exporter custom</b> tramite una base class documentata "
                "— inserisci la tua destinazione (OTLP, Kafka, S3) senza "
                "forkare.",
            ),
        ],
    ),
    Note(
        en=(
            "48 unit tests using <font face='Courier'>httpx.MockTransport</font> "
            "— the wire format is pinned independently from the live "
            "collector, so SDK refactors can't silently break the "
            "ingest contract."
        ),
        it=(
            "48 test unitari con <font face='Courier'>httpx.MockTransport</font> "
            "— il wire format è fissato indipendentemente dal collector "
            "live, così i refactor dell'SDK non possono rompere "
            "silenziosamente il contratto di ingest."
        ),
    ),
    # ------------------------------------------------------------------------
    # 5. The Backend
    # ------------------------------------------------------------------------
    Heading(
        number=5,
        en="The Backend",
        it="Il Backend",
    ),
    Para(
        en=(
            "FastAPI on Python 3.13. Async-first end-to-end: SQLAlchemy 2.0 "
            "async, httpx async for any outbound call, no "
            "<font face='Courier'>time.sleep</font>, no blocking IO on the "
            "event loop. Strict Pydantic models with "
            "<font face='Courier'>extra=\"forbid\"</font> so the API rejects "
            "unknown keys instead of silently dropping them."
        ),
        it=(
            "FastAPI su Python 3.13. Async-first end-to-end: SQLAlchemy 2.0 "
            "async, httpx async per qualunque chiamata in uscita, niente "
            "<font face='Courier'>time.sleep</font>, nessun IO bloccante "
            "sull'event loop. Modelli Pydantic strict con "
            "<font face='Courier'>extra=\"forbid\"</font> così l'API "
            "rifiuta chiavi sconosciute invece di scartarle in silenzio."
        ),
    ),
    Subheading(
        en="Thin controllers, fat services",
        it="Controller sottili, service grassi",
    ),
    Para(
        en=(
            "Route handlers in <font face='Courier'>app/api/</font> are kept "
            "at ≤140 LOC each — they validate the request, call a service, "
            "return a Pydantic schema. All business logic lives in "
            "<font face='Courier'>app/services/</font>. ORM models never "
            "escape the service layer; they're converted to "
            "<font face='Courier'>Read</font> Pydantic schemas before the "
            "route returns. This makes the surface that talks to clients "
            "small and reviewable, and makes services testable without "
            "FastAPI's request machinery."
        ),
        it=(
            "Gli handler delle route in <font face='Courier'>app/api/</font> "
            "stanno sotto le 140 LOC ciascuno — validano la richiesta, "
            "chiamano un service, restituiscono uno schema Pydantic. Tutta "
            "la logica di business vive in <font face='Courier'>app/services/</font>. "
            "I modelli ORM non escono mai dal service layer; vengono "
            "convertiti in schemi <font face='Courier'>Read</font> Pydantic "
            "prima del return della route. Questo rende piccola e "
            "revisionabile la superficie che parla con i client, e rende "
            "i service testabili senza il machinery di richiesta di FastAPI."
        ),
    ),
    Subheading(en="Module map", it="Mappa dei moduli"),
    KV(
        header_en=("Module", "Responsibility"),
        header_it=("Modulo", "Responsabilità"),
        rows=[
            (
                "app/api/",
                (
                    "Route handlers (spans, systems, trust, annex-iv, "
                    "tools, auth). Validate + dispatch only.",
                    "Handler delle route (spans, systems, trust, annex-iv, "
                    "tools, auth). Solo validate + dispatch.",
                ),
            ),
            (
                "app/services/",
                (
                    "Business logic — span ingest with idempotency, "
                    "audit recording, Annex IV aggregation, risk "
                    "classifier, trust redaction, API-key issuance.",
                    "Logica di business — ingest span con idempotenza, "
                    "audit recording, aggregazione Annex IV, risk "
                    "classifier, redaction trust, emissione API key.",
                ),
            ),
            (
                "app/models/",
                (
                    "SQLAlchemy 2.0 ORM. <font face='Courier'>Mapped[T]</font> "
                    "annotations, <font face='Courier'>expire_on_commit=False</font> "
                    "to avoid MissingGreenlet on async returns.",
                    "ORM SQLAlchemy 2.0. Annotazioni "
                    "<font face='Courier'>Mapped[T]</font>, "
                    "<font face='Courier'>expire_on_commit=False</font> per "
                    "evitare MissingGreenlet sui return async.",
                ),
            ),
            (
                "app/schemas/",
                (
                    "Pydantic request/response models — separate "
                    "<font face='Courier'>Create</font>, "
                    "<font face='Courier'>Update</font>, "
                    "<font face='Courier'>Read</font> per resource.",
                    "Modelli Pydantic request/response — "
                    "<font face='Courier'>Create</font>, "
                    "<font face='Courier'>Update</font>, "
                    "<font face='Courier'>Read</font> separati per "
                    "risorsa.",
                ),
            ),
            (
                "app/data/",
                (
                    "Static rule data — <font face='Courier'>annex_iii.json</font> "
                    "(risk categories, bilingual labels), Article 5 "
                    "prohibited use cases.",
                    "Dati di regole statici — <font face='Courier'>annex_iii.json</font> "
                    "(categorie di rischio, label bilingue), use case "
                    "vietati dall'Articolo 5.",
                ),
            ),
            (
                "app/templates/",
                (
                    "Jinja templates for Annex IV (Markdown + PDF). "
                    "<font face='Courier'>StrictUndefined</font> so missing "
                    "fields hard-fail instead of producing empty PDF "
                    "sections.",
                    "Template Jinja per Annex IV (Markdown + PDF). "
                    "<font face='Courier'>StrictUndefined</font> così i "
                    "campi mancanti falliscono hard invece di produrre "
                    "sezioni PDF vuote.",
                ),
            ),
            (
                "alembic/",
                (
                    "DB migrations — one logical change per file, "
                    "rationale in the docstring, clean linear "
                    "<font face='Courier'>down_revision</font> chain.",
                    "Migrazioni DB — un cambio logico per file, "
                    "razionale nella docstring, chain "
                    "<font face='Courier'>down_revision</font> "
                    "lineare e pulita.",
                ),
            ),
        ],
    ),
    # ------------------------------------------------------------------------
    # 6. The Frontend
    # ------------------------------------------------------------------------
    Heading(
        number=6,
        en="The Frontend",
        it="Il Frontend",
    ),
    Para(
        en=(
            "Next.js 16 App Router with Turbopack, React 19, Tailwind 4 "
            "with OKLCH colour tokens. Server Components by default; "
            "client components only where strictly needed (theme provider, "
            "Cmd-K command palette, the Annex IV form). This keeps "
            "first-paint fast and the JS bundle small."
        ),
        it=(
            "Next.js 16 App Router con Turbopack, React 19, Tailwind 4 "
            "con token colore OKLCH. Server Component di default; "
            "client component solo dove strettamente necessario (theme "
            "provider, command palette Cmd-K, form Annex IV). Questo "
            "tiene veloce la first-paint e piccolo il bundle JS."
        ),
    ),
    Subheading(en="Routes shipping today", it="Route attualmente in vigore"),
    KV(
        header_en=("Route", "What it serves"),
        header_it=("Route", "Cosa serve"),
        rows=[
            (
                "/",
                (
                    "Home. Six narrative sections — Hero, Stakes (AI Act "
                    "countdown), HowItWorks + invariants, TrustPreview, "
                    "Comparison, FinalCTA.",
                    "Home. Sei sezioni narrative — Hero, Stakes (countdown "
                    "AI Act), HowItWorks + invarianti, TrustPreview, "
                    "Comparison, FinalCTA.",
                ),
            ),
            (
                "/pricing",
                (
                    "Four tiers (Self-host + Pro + Team + Enterprise) + "
                    "FAQ + Schema.org Product/FAQPage JSON-LD.",
                    "Quattro tier (Self-host + Pro + Team + Enterprise) + "
                    "FAQ + JSON-LD Schema.org Product/FAQPage.",
                ),
            ),
            (
                "/trust/[slug]",
                (
                    "Public, slug-addressable trust page. Server-rendered "
                    "from the backend trust API. Whitelist-redacted "
                    "provider_info.",
                    "Trust page pubblica, indirizzata da slug. Renderizzata "
                    "server-side dalla trust API backend. provider_info "
                    "redacted via whitelist.",
                ),
            ),
            (
                "/tools/annex-iv-generator",
                (
                    "Free anonymous Annex IV PDF generator. 5-min form "
                    "→ rule-classified PDF download. Rate-limited "
                    "10/hour/IP server-side.",
                    "Generatore Annex IV PDF gratuito e anonimo. Form 5 "
                    "minuti → PDF classificato da regole. Rate-limit "
                    "10/ora/IP server-side.",
                ),
            ),
            (
                "/tools/logging-schema",
                (
                    "JSON Schema for Article 12 logging — drop into "
                    "OTel, CI, or a custom adapter. Versioned URL.",
                    "JSON Schema per il logging Articolo 12 — da "
                    "inserire in OTel, CI, o un adapter custom. URL "
                    "versionata.",
                ),
            ),
            (
                "/demo/annex-iv",
                (
                    "Three pre-built Annex IV demos (loan-screener, "
                    "cv-screener, customer-support) — open the real "
                    "PDF in a new tab.",
                    "Tre demo Annex IV pre-costruite (loan-screener, "
                    "cv-screener, customer-support) — aprono il PDF "
                    "reale in una nuova tab.",
                ),
            ),
            (
                "/brand/avatar",
                (
                    "1024×1024 monogram PNG rendered at request time via "
                    "satori. Same colours as the website. Long-cached.",
                    "Monogramma PNG 1024×1024 renderizzato al volo via "
                    "satori. Stessi colori del sito. Long-cache.",
                ),
            ),
        ],
    ),
    Subheading(
        en="Build-time rasterised assets",
        it="Asset rasterizzati al build",
    ),
    Para(
        en=(
            "Icons (favicon, apple-icon), Open Graph cards, and Twitter "
            "cards are all rendered via <font face='Courier'>satori</font> — "
            "the same engine, the same font files (Inter Bold + EB Garamond "
            "Italic), the same brand colours read from one place. A brand "
            "refresh is therefore one diff that updates every rasterised "
            "surface coherently."
        ),
        it=(
            "Le icon (favicon, apple-icon), le card Open Graph e Twitter "
            "sono tutte renderizzate via <font face='Courier'>satori</font> — "
            "stesso motore, stessi file font (Inter Bold + EB Garamond "
            "Italic), stessi colori brand letti da un solo posto. Un "
            "brand refresh è quindi un singolo diff che aggiorna ogni "
            "superficie rasterizzata in modo coerente."
        ),
    ),
    # ------------------------------------------------------------------------
    # 7. Database
    # ------------------------------------------------------------------------
    Heading(
        number=7,
        en="The Database",
        it="Il Database",
    ),
    Para(
        en=(
            "Postgres 16 with the <font face='Courier'>pgvector</font> "
            "extension reserved for v0.2 (prompt-template semantic "
            "matching). Alembic for migrations: one logical change per "
            "file, rationale in the docstring, no autogenerate slop, "
            "no squashing of unrelated changes."
        ),
        it=(
            "Postgres 16 con l'estensione <font face='Courier'>pgvector</font> "
            "riservata per la v0.2 (matching semantico di template di "
            "prompt). Alembic per le migrazioni: un cambio logico per "
            "file, razionale nella docstring, niente slop da autogenerate, "
            "niente squash di cambi non correlati."
        ),
    ),
    Subheading(en="Core tables", it="Tabelle principali"),
    KV(
        header_en=("Table", "Purpose"),
        header_it=("Tabella", "Scopo"),
        rows=[
            (
                "tenants",
                (
                    "One row per organisation. Slug = public trust-page "
                    "URL. Status (created / suspended). No tier column in "
                    "v0.1 (billing lands Q3 2026).",
                    "Una row per organizzazione. Slug = URL della "
                    "trust page pubblica. Status (created / suspended). "
                    "Nessuna colonna tier in v0.1 (billing arriva Q3 2026).",
                ),
            ),
            (
                "api_keys",
                (
                    "HMAC-SHA256 hashed prefix + secret. Constant-time "
                    "compare on auth. Revocation by row delete. The plaintext "
                    "key is shown once at creation, never stored.",
                    "Prefisso + secret hashati HMAC-SHA256. Confronto a "
                    "tempo costante sull'auth. Revoca per delete della row. "
                    "La chiave in plaintext si vede una volta alla "
                    "creazione, non si memorizza mai.",
                ),
            ),
            (
                "ai_systems",
                (
                    "Declared AI systems per tenant. Carries the latest "
                    "risk-tier verdict, Annex III category, purpose, "
                    "provider_info JSONB.",
                    "Sistemi AI dichiarati per tenant. Porta il verdict di "
                    "risk-tier corrente, la categoria Annex III, lo scopo, "
                    "il provider_info JSONB.",
                ),
            ),
            (
                "spans",
                (
                    "Per-call telemetry — model id, prompt + output hashes, "
                    "latency, user role, retrieval sources, plus tenant + "
                    "system fk. Idempotent ingest by trace_id with TOCTOU "
                    "race protection.",
                    "Telemetria per chiamata — model id, hash di prompt + "
                    "output, latenza, ruolo utente, source di retrieval, "
                    "più fk tenant + system. Ingest idempotente per "
                    "trace_id con protezione race TOCTOU.",
                ),
            ),
            (
                "audit_logs",
                (
                    "Append-only journal of every state change. Postgres "
                    "trigger raises on UPDATE/DELETE. The only mutation "
                    "API in the service layer is <font face='Courier'>"
                    "record()</font>.",
                    "Journal append-only di ogni cambiamento di stato. "
                    "Trigger Postgres solleva su UPDATE/DELETE. L'unica "
                    "API di mutation nel service layer è "
                    "<font face='Courier'>record()</font>.",
                ),
            ),
        ],
    ),
    Subheading(
        en="Cross-tenant isolation",
        it="Isolamento cross-tenant",
    ),
    Para(
        en=(
            "Every queryable model carries a "
            "<font face='Courier'>tenant_id</font> column. Service-layer "
            "queries always filter by the authenticated tenant. Eight "
            "explicit tests in <font face='Courier'>"
            "test_cross_tenant_isolation.py</font> verify this — including "
            "byte-identical 404 responses (no timing oracle to enumerate "
            "slugs) and rejection of path-traversal attempts in "
            "<font face='Courier'>system_id</font>."
        ),
        it=(
            "Ogni modello queryabile porta una colonna "
            "<font face='Courier'>tenant_id</font>. Le query del service "
            "layer filtrano sempre per il tenant autenticato. Otto test "
            "espliciti in <font face='Courier'>"
            "test_cross_tenant_isolation.py</font> lo verificano — "
            "compresi response 404 byte-identici (nessun timing oracle "
            "per enumerare slug) e rifiuto di tentativi di path-traversal "
            "in <font face='Courier'>system_id</font>."
        ),
    ),
    # ------------------------------------------------------------------------
    # 8. Seven non-negotiables
    # ------------------------------------------------------------------------
    Heading(
        number=8,
        en="The seven non-negotiables",
        it="I sette punti non negoziabili",
    ),
    Para(
        en=(
            "These are the hard-won regulatory and audit invariants. "
            "Every PR is reviewed against them. Each is verified in "
            "code, not policy."
        ),
        it=(
            "Sono gli invarianti regolatori e di audit consolidati. "
            "Ogni PR viene revisionata contro di loro. Ognuno è "
            "verificato in codice, non in policy."
        ),
    ),
    KV(
        header_en=("#", "Invariant + enforcement"),
        header_it=("#", "Invariante + enforcement"),
        rows=[
            (
                "1",
                (
                    "<b>Deterministic risk classifier.</b> Pure-Python "
                    "rules. Strict precedence. Never declassifies.",
                    "<b>Risk classifier deterministico.</b> Regole "
                    "Python pure. Precedenza strict. Mai declassifica.",
                ),
            ),
            (
                "2",
                (
                    "<b>Append-only audit log.</b> 3 layers: service "
                    "exposes only record(); no mutation API; Postgres "
                    "trigger raises on UPDATE/DELETE.",
                    "<b>Audit log append-only.</b> 3 layer: il service "
                    "espone solo record(); nessuna API di mutation; "
                    "trigger Postgres solleva su UPDATE/DELETE.",
                ),
            ),
            (
                "3",
                (
                    "<b>EU data residency.</b> Hetzner Falkenstein "
                    "(collector + DB), Mistral La Plateforme Paris "
                    "(advisor). No US-only services touch PII.",
                    "<b>Residenza dati UE.</b> Hetzner Falkenstein "
                    "(collector + DB), Mistral La Plateforme Parigi "
                    "(advisor). Nessun servizio US-only tocca PII.",
                ),
            ),
            (
                "4",
                (
                    "<b>Thin controllers, fat services.</b> Routes "
                    "≤140 LOC, validate + dispatch only. All logic in "
                    "app/services/.",
                    "<b>Controller sottili, service grassi.</b> Route "
                    "≤140 LOC, solo validate + dispatch. Tutta la "
                    "logica in app/services/.",
                ),
            ),
            (
                "5",
                (
                    "<b>Types on everything.</b> from __future__ import "
                    "annotations everywhere. Mapped[T] on ORM. "
                    "Pydantic extra='forbid'.",
                    "<b>Tipi su tutto.</b> from __future__ import "
                    "annotations ovunque. Mapped[T] sull'ORM. "
                    "Pydantic extra='forbid'.",
                ),
            ),
            (
                "6",
                (
                    "<b>Permanent disclaimer.</b> Bilingual disclaimer "
                    "on every Annex IV PDF, trust-page surface, and "
                    "compliance output. AnnexKit is not a law firm.",
                    "<b>Disclaimer permanente.</b> Disclaimer bilingue "
                    "su ogni PDF Annex IV, trust-page, e output di "
                    "compliance. AnnexKit non è uno studio legale.",
                ),
            ),
            (
                "7",
                (
                    "<b>Privacy-by-default in spans.</b> SDK SHA-256 "
                    "hashes inputs/outputs at the host. Plaintext is "
                    "opt-in (v0.2 with encryption-at-rest).",
                    "<b>Privacy-by-default negli span.</b> L'SDK fa hash "
                    "SHA-256 di input/output sull'host. Il plaintext è "
                    "opt-in (v0.2 con encryption-at-rest).",
                ),
            ),
        ],
    ),
    # ------------------------------------------------------------------------
    # 9. Security
    # ------------------------------------------------------------------------
    Heading(
        number=9,
        en="Security architecture",
        it="Architettura di sicurezza",
    ),
    Bullets(
        items=[
            (
                "<b>API key design.</b> Prefix <font face='Courier'>ak_</font> "
                "+ 120-bit secret in a base32-ish alphabet that excludes "
                "ambiguous characters (0/O, 1/l/I). HMAC-SHA256 stored "
                "(not bcrypt — the rationale is in <font face='Courier'>"
                "api_key.py</font>).",
                "<b>Design delle API key.</b> Prefisso <font face='Courier'>ak_</font> "
                "+ secret a 120 bit in alfabeto base32-ish che esclude "
                "caratteri ambigui (0/O, 1/l/I). Memorizzato HMAC-SHA256 "
                "(non bcrypt — il razionale è in <font face='Courier'>"
                "api_key.py</font>).",
            ),
            (
                "<b>Constant-time comparison.</b> Auth path uses "
                "<font face='Courier'>hmac.compare_digest</font> to neutralise "
                "timing attacks against the key check.",
                "<b>Confronto a tempo costante.</b> Il percorso di auth usa "
                "<font face='Courier'>hmac.compare_digest</font> per "
                "neutralizzare timing attack contro la verifica della key.",
            ),
            (
                "<b>Rate limiting.</b> <font face='Courier'>slowapi</font> "
                "(FastAPI-friendly Flask-Limiter port) on every public "
                "trust endpoint. 60 req/min per IP. Cloudflare provides "
                "a coarse fallback above that.",
                "<b>Rate limiting.</b> <font face='Courier'>slowapi</font> "
                "(port di Flask-Limiter compatibile con FastAPI) su ogni "
                "endpoint trust pubblico. 60 req/min per IP. Cloudflare "
                "fornisce un fallback grossolano sopra a quello.",
            ),
            (
                "<b>Opaque 404s.</b> Slug-not-found and access-denied "
                "responses are byte-identical, so an attacker can't "
                "enumerate tenant slugs by timing or message diff.",
                "<b>404 opachi.</b> Le response slug-non-trovato e "
                "accesso-negato sono byte-identiche, così un attaccante "
                "non può enumerare gli slug tenant per timing o per diff "
                "del messaggio.",
            ),
            (
                "<b>Path-traversal rejection.</b> "
                "<font face='Courier'>system_id</font> is sanitised "
                "before any filesystem or routing use. Tested explicitly.",
                "<b>Rifiuto del path-traversal.</b> "
                "<font face='Courier'>system_id</font> viene sanitizzato "
                "prima di qualunque uso filesystem o di routing. Testato "
                "esplicitamente.",
            ),
            (
                "<b>Fail-fast hardening at startup.</b> The backend refuses "
                "to boot in production with an insecure SECRET_KEY or "
                "wildcard CORS — surfacing the misconfiguration on boot "
                "rather than at the first request that exploits it.",
                "<b>Hardening fail-fast all'avvio.</b> Il backend si "
                "rifiuta di partire in produzione con SECRET_KEY insicura "
                "o CORS wildcard — il misconfig viene fatto emergere al "
                "boot invece che alla prima richiesta che lo sfrutta.",
            ),
            (
                "<b>Idempotent span ingest with TOCTOU race protection.</b> "
                "Concurrent ingest of the same trace_id is handled by "
                "catching <font face='Courier'>IntegrityError</font>, "
                "rolling back, and re-fetching the row — so the API "
                "always returns the canonical persisted span.",
                "<b>Ingest span idempotente con protezione race TOCTOU.</b> "
                "L'ingest concorrente dello stesso trace_id viene gestito "
                "intercettando <font face='Courier'>IntegrityError</font>, "
                "facendo rollback e ri-fetchando la row — così l'API "
                "ritorna sempre lo span canonico persistito.",
            ),
        ],
    ),
    # ------------------------------------------------------------------------
    # 10. Deployment & infrastructure
    # ------------------------------------------------------------------------
    Heading(
        number=10,
        en="Deployment & infrastructure",
        it="Deploy e infrastruttura",
    ),
    Subheading(en="Local development", it="Sviluppo locale"),
    Para(
        en=(
            "<font face='Courier'>docker compose up</font> stands up the "
            "whole dev stack: Postgres 16 + the backend with "
            "<font face='Courier'>uvicorn --reload</font> + the Next.js "
            "frontend with Turbopack. Backend listens on :8033, frontend "
            "on :3001 (mapped to container :3000). A <font face='Courier'>"
            "make demo-seed</font> target creates a tenant and runs the "
            "loan-screener chatbot end-to-end."
        ),
        it=(
            "<font face='Courier'>docker compose up</font> avvia tutto lo "
            "stack di dev: Postgres 16 + il backend con "
            "<font face='Courier'>uvicorn --reload</font> + il frontend "
            "Next.js con Turbopack. Il backend ascolta su :8033, il "
            "frontend su :3001 (mappato sul container :3000). Un target "
            "<font face='Courier'>make demo-seed</font> crea un tenant ed "
            "esegue il chatbot loan-screener end-to-end."
        ),
    ),
    Subheading(en="Production", it="Produzione"),
    Para(
        en=(
            "Hetzner VPS in Falkenstein, Germany. Docker Compose with a "
            "<font face='Courier'>docker-compose.prod.yml</font> override "
            "that resets the dev reload volume + disables uvicorn "
            "<font face='Courier'>--reload</font> (the dev reloader keeps "
            "the parent process alive after worker crash — a silent "
            "failure mode in early prod). Caddy reverse proxy "
            "(co-hosted with sibling project Konformia) terminates TLS. "
            "Cloudflare DNS + CDN in front. Deploys are "
            "<font face='Courier'>git pull</font> + "
            "<font face='Courier'>docker compose up --build</font> driven "
            "by the <font face='Courier'>make prod-deploy</font> targets."
        ),
        it=(
            "VPS Hetzner a Falkenstein, Germania. Docker Compose con un "
            "override <font face='Courier'>docker-compose.prod.yml</font> "
            "che resetta il volume reload di dev + disabilita uvicorn "
            "<font face='Courier'>--reload</font> (il reloader di dev "
            "tiene il processo padre vivo anche dopo crash del worker — "
            "un fallimento silenzioso nei primi giorni di prod). Reverse "
            "proxy Caddy (co-hosted col progetto sibling Konformia) per "
            "il TLS. Cloudflare DNS + CDN davanti. I deploy sono "
            "<font face='Courier'>git pull</font> + "
            "<font face='Courier'>docker compose up --build</font> guidati "
            "dai target <font face='Courier'>make prod-deploy</font>."
        ),
    ),
    Subheading(en="External dependencies", it="Dipendenze esterne"),
    KV(
        header_en=("Service", "Role · Location"),
        header_it=("Servizio", "Ruolo · Localizzazione"),
        rows=[
            (
                "Hetzner Cloud",
                (
                    "VPS host · Falkenstein (DE). EU sovereign cloud "
                    "compatible.",
                    "Host del VPS · Falkenstein (DE). Compatibile con "
                    "EU sovereign cloud.",
                ),
            ),
            (
                "Cloudflare",
                (
                    "DNS, CDN, basic DDoS · global edge. Annexkit.dev + "
                    "subdomains.",
                    "DNS, CDN, DDoS di base · edge globale. Annexkit.dev "
                    "+ sottodomini.",
                ),
            ),
            (
                "Mistral La Plateforme",
                (
                    "LLM advisor (v0.2) · Paris (FR). EU-resident "
                    "alternative to OpenAI for ambiguous-declaration "
                    "hinting.",
                    "Advisor LLM (v0.2) · Parigi (FR). Alternativa "
                    "EU-resident a OpenAI per suggerimenti su "
                    "dichiarazioni ambigue.",
                ),
            ),
            (
                "PyPI",
                (
                    "SDK distribution · global. The "
                    "<font face='Courier'>annexkit</font> package.",
                    "Distribuzione SDK · globale. Il package "
                    "<font face='Courier'>annexkit</font>.",
                ),
            ),
            (
                "GitHub",
                (
                    "Source hosting + CI (Actions) + dependabot · global.",
                    "Hosting del sorgente + CI (Actions) + dependabot · "
                    "globale.",
                ),
            ),
        ],
    ),
    # ------------------------------------------------------------------------
    # 11. Testing
    # ------------------------------------------------------------------------
    Heading(
        number=11,
        en="Testing strategy",
        it="Strategia di test",
    ),
    Para(
        en=(
            "<b>~114 tests total: 66 backend + 48 SDK</b> against ~4,700 "
            "LOC of source. The split is deliberate: the SDK tests pin the "
            "wire format independently from the live backend, the backend "
            "tests pin the service-layer contracts and the cross-tenant "
            "isolation. CI runs both suites + a typecheck on every PR."
        ),
        it=(
            "<b>~114 test totali: 66 backend + 48 SDK</b> contro ~4.700 "
            "LOC di sorgente. Lo split è deliberato: i test SDK fissano "
            "il wire format indipendentemente dal backend live, i test "
            "backend fissano i contratti del service layer e l'isolamento "
            "cross-tenant. La CI esegue entrambe le suite + un typecheck "
            "su ogni PR."
        ),
    ),
    Bullets(
        items=[
            (
                "<b>pytest + pytest-asyncio</b> for async backend tests. "
                "SQLite in-memory database per test run — fast iteration, "
                "service-layer contracts pinned exactly.",
                "<b>pytest + pytest-asyncio</b> per i test async del "
                "backend. Database SQLite in-memory per ogni run di "
                "test — iterazione veloce, contratti del service layer "
                "fissati esattamente.",
            ),
            (
                "<b>Postgres trigger integration test</b> via "
                "<font face='Courier'>testcontainers-python</font>. "
                "Spins up a real Postgres, runs migrations, asserts "
                "that UPDATE/DELETE on audit_logs raises. ~10s CI "
                "overhead, catches the only DB-layer regression that "
                "SQLite can't.",
                "<b>Test di integrazione del trigger Postgres</b> via "
                "<font face='Courier'>testcontainers-python</font>. "
                "Avvia un Postgres reale, esegue le migrazioni, "
                "asserisce che UPDATE/DELETE su audit_logs solleva. "
                "~10s di overhead CI, intercetta l'unica regressione "
                "DB-layer che SQLite non può.",
            ),
            (
                "<b>httpx.MockTransport</b> on the SDK side. Replays the "
                "wire format the backend expects without booting the "
                "backend — fast iteration and the SDK doesn't drift from "
                "the contract.",
                "<b>httpx.MockTransport</b> lato SDK. Ripete il wire "
                "format che il backend si aspetta senza far partire il "
                "backend — iterazione veloce e l'SDK non drift-a dal "
                "contratto.",
            ),
            (
                "<b>Eight explicit cross-tenant isolation tests</b> in "
                "<font face='Courier'>test_cross_tenant_isolation.py</font>: "
                "opaque 404s, path-traversal rejection, tenant-A reads of "
                "tenant-B return 404 not 403.",
                "<b>Otto test espliciti di isolamento cross-tenant</b> in "
                "<font face='Courier'>test_cross_tenant_isolation.py</font>: "
                "404 opachi, rifiuto del path-traversal, letture del "
                "tenant-A su tenant-B restituiscono 404 non 403.",
            ),
            (
                "<b>Contract test on audit_service</b> introspects the "
                "module namespace and pins the public API — preventing "
                "a future PR from accidentally exposing an "
                "<font face='Courier'>update()</font> or "
                "<font face='Courier'>delete()</font> on the audit log.",
                "<b>Test di contratto su audit_service</b> introspetta il "
                "namespace del modulo e fissa l'API pubblica — impedisce "
                "che una PR futura esponga accidentalmente "
                "un <font face='Courier'>update()</font> o "
                "<font face='Courier'>delete()</font> sull'audit log.",
            ),
            (
                "<b>Frontend tests</b> are tracked under v0.2 (Vitest). "
                "Today the contract is exercised through Next.js's own "
                "build pass and the end-to-end Annex IV demo render.",
                "<b>I test frontend</b> sono tracciati sotto v0.2 "
                "(Vitest). Oggi il contratto è esercitato attraverso il "
                "build pass di Next.js e il render end-to-end della demo "
                "Annex IV.",
            ),
        ],
    ),
    # ------------------------------------------------------------------------
    # 12. Roadmap
    # ------------------------------------------------------------------------
    Heading(
        number=12,
        en="Roadmap (v0.2 and beyond)",
        it="Roadmap (v0.2 e oltre)",
    ),
    Subheading(en="Shipped in v0.1.x", it="Già rilasciato in v0.1.x"),
    Bullets(
        items=[
            (
                "Span ingest API with HMAC-authenticated tenants.",
                "API di ingest span con tenant autenticati HMAC.",
            ),
            (
                "Append-only audit log with Postgres trigger enforcement.",
                "Audit log append-only con enforcement via trigger Postgres.",
            ),
            (
                "Deterministic Annex III risk classifier (rules + "
                "bilingual labels).",
                "Risk classifier Annex III deterministico (regole + "
                "label bilingue).",
            ),
            (
                "Annex IV generator (Markdown + PDF, bilingual EN/IT).",
                "Generatore Annex IV (Markdown + PDF, bilingue EN/IT).",
            ),
            (
                "Public trust pages with whitelist-redacted provider_info.",
                "Trust page pubbliche con provider_info redatto via "
                "whitelist.",
            ),
            (
                "Cross-tenant isolation tests + Postgres trigger CI test.",
                "Test di isolamento cross-tenant + test CI del trigger "
                "Postgres.",
            ),
            (
                "Idempotent span ingest with TOCTOU race protection.",
                "Ingest span idempotente con protezione race TOCTOU.",
            ),
            (
                "Free anonymous tools: Annex IV generator + Article 12 "
                "JSON Schema.",
                "Tool gratuiti anonimi: generatore Annex IV + JSON Schema "
                "Articolo 12.",
            ),
            (
                "Rate limiting on public trust endpoints (slowapi, "
                "60/min/IP).",
                "Rate limiting sugli endpoint trust pubblici (slowapi, "
                "60/min/IP).",
            ),
        ],
    ),
    Subheading(en="Planned for v0.2", it="Pianificato per v0.2"),
    Bullets(
        items=[
            (
                "LangChain + LlamaIndex auto-instrumentation.",
                "Auto-instrumentation LangChain + LlamaIndex.",
            ),
            (
                "TypeScript / JavaScript SDK (parity with Python).",
                "SDK TypeScript / JavaScript (parità con Python).",
            ),
            (
                "LLM advisor for ambiguous declarations — Mistral La "
                "Plateforme, hard guardrail: never declassifies.",
                "Advisor LLM per dichiarazioni ambigue — Mistral La "
                "Plateforme, guardrail strict: mai declassifica.",
            ),
            (
                "Span batching + retry on transient failure.",
                "Batching span + retry su failure transient.",
            ),
            (
                "Trust badge embeddable in customer footers.",
                "Trust badge embeddabile nei footer dei clienti.",
            ),
            (
                "Customer dashboard + Stripe self-serve sign-up + "
                "automatic quota enforcement (Q3 2026).",
                "Dashboard cliente + sign-up self-serve via Stripe + "
                "enforcement automatico delle quote (Q3 2026).",
            ),
            (
                "Encryption-at-rest for opt-in plaintext spans.",
                "Encryption-at-rest per span plaintext opt-in.",
            ),
            (
                "OpenTelemetry GenAI semconv compatibility + OTLP exporter.",
                "Compatibilità con OpenTelemetry GenAI semconv + "
                "exporter OTLP.",
            ),
        ],
    ),
    # ------------------------------------------------------------------------
    # 13. Glossary
    # ------------------------------------------------------------------------
    Heading(
        number=13,
        en="Glossary",
        it="Glossario",
    ),
    KV(
        header_en=("Term", "Meaning"),
        header_it=("Termine", "Significato"),
        rows=[
            (
                "Annex III",
                (
                    "The list of high-risk AI use cases in the EU AI Act. "
                    "Eight categories (biometrics, critical infrastructure, "
                    "education, employment, public services, law "
                    "enforcement, migration, justice).",
                    "La lista di use case AI ad alto rischio nell'EU AI "
                    "Act. Otto categorie (biometria, infrastrutture "
                    "critiche, educazione, lavoro, servizi pubblici, "
                    "law enforcement, migrazione, giustizia).",
                ),
            ),
            (
                "Annex IV",
                (
                    "The mandated structure of the technical documentation "
                    "that providers of high-risk AI systems must produce. "
                    "What AnnexKit generates.",
                    "La struttura obbligata della documentazione tecnica "
                    "che i provider di sistemi AI ad alto rischio devono "
                    "produrre. Quello che AnnexKit genera.",
                ),
            ),
            (
                "Article 12",
                (
                    "AI Act requirement that high-risk systems "
                    "automatically log events throughout their lifetime. "
                    "AnnexKit's span ingest is the implementation.",
                    "Requisito dell'AI Act per cui i sistemi ad alto "
                    "rischio devono fare logging automatico degli eventi "
                    "per tutta la loro vita. L'ingest span di AnnexKit "
                    "è l'implementazione.",
                ),
            ),
            (
                "Article 50",
                (
                    "Transparency obligation toward natural persons "
                    "interacting with AI — chatbots must disclose they "
                    "are AI, deepfakes must be labelled.",
                    "Obbligo di trasparenza verso le persone fisiche che "
                    "interagiscono con un'AI — i chatbot devono "
                    "dichiarare di essere AI, i deepfake devono essere "
                    "etichettati.",
                ),
            ),
            (
                "Span",
                (
                    "A single record of one LLM call: model, timing, "
                    "prompt hash, output hash, retrieval sources, user "
                    "role, tenant + system reference.",
                    "Un singolo record di una chiamata LLM: modello, "
                    "timing, hash del prompt, hash dell'output, source "
                    "di retrieval, ruolo utente, riferimento a tenant "
                    "+ system.",
                ),
            ),
            (
                "Tenant",
                (
                    "An organisation using AnnexKit. One tenant maps to "
                    "one public trust page, one set of API keys, one "
                    "billing relationship (Q3 2026 onwards).",
                    "Un'organizzazione che usa AnnexKit. Un tenant "
                    "corrisponde a una trust page pubblica, un set di "
                    "API key, una relazione di billing (da Q3 2026).",
                ),
            ),
            (
                "Trust page",
                (
                    "The slug-addressable public page that lists a "
                    "tenant's declared AI systems and their risk tiers. "
                    "Provider info is whitelist-redacted.",
                    "La pagina pubblica indirizzata da slug che elenca "
                    "i sistemi AI dichiarati di un tenant e i loro "
                    "tier di rischio. Il provider info è redacted via "
                    "whitelist.",
                ),
            ),
        ],
    ),
    Note(
        en=(
            "Disclaimer: AnnexKit is not a law firm. The Annex IV "
            "documents and risk classifications it produces are "
            "technical artefacts; legal interpretation is the "
            "responsibility of your legal team or external counsel."
        ),
        it=(
            "Disclaimer: AnnexKit non è uno studio legale. I documenti "
            "Annex IV e le classificazioni di rischio prodotte sono "
            "artefatti tecnici; l'interpretazione legale è "
            "responsabilità del tuo team legale o di un consulente "
            "esterno."
        ),
    ),
]


# ============================================================================
# Render
# ============================================================================


def make_styles() -> dict[str, ParagraphStyle]:
    """Build all the paragraph styles we use in this document."""
    base = getSampleStyleSheet()["Normal"]

    return {
        "title": ParagraphStyle(
            "Title",
            parent=base,
            fontName="Helvetica-Bold",
            fontSize=32,
            leading=38,
            textColor=INK,
            spaceBefore=0,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base,
            fontName="Helvetica-Oblique",
            fontSize=14,
            leading=18,
            textColor=INK_MUTED,
            spaceAfter=24,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            parent=base,
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=INK_MUTED,
            spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base,
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=SAGE,
            spaceBefore=28,
            spaceAfter=10,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base,
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=INK,
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base,
            fontName="Helvetica",
            fontSize=10,
            leading=14.5,
            textColor=INK,
            spaceAfter=8,
            alignment=0,  # left
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base,
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=INK,
            leftIndent=18,
            bulletIndent=4,
            spaceAfter=6,
        ),
        "code_caption": ParagraphStyle(
            "CodeCaption",
            parent=base,
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            textColor=INK_MUTED,
            spaceBefore=4,
            spaceAfter=12,
        ),
        "note": ParagraphStyle(
            "Note",
            parent=base,
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            leading=13,
            textColor=INK_MUTED,
            leftIndent=14,
            spaceBefore=4,
            spaceAfter=12,
            borderColor=SAGE,
            borderWidth=0,
            borderPadding=0,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base,
            fontName="Courier",
            fontSize=8.5,
            leading=11,
            textColor=INK,
            backColor=CODE_BG,
            borderColor=RULE,
            borderWidth=0.5,
            borderPadding=10,
            spaceBefore=4,
            spaceAfter=4,
        ),
    }


def make_table_style(num_rows: int) -> TableStyle:
    """Generic table style — sage header row, hairline body rules."""
    return TableStyle(
        [
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), SAGE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
            ("TOPPADDING", (0, 0), (-1, 0), 7),
            # Body
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("TEXTCOLOR", (0, 1), (-1, -1), INK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            # Hairlines between body rows
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
            # Slight alternating row backgrounds for body
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [CANVAS, colors.white],
            ),
        ],
    )


class ArchitectureDoc(BaseDocTemplate):
    """BaseDocTemplate with a sage-tinted footer carrying the page number."""

    def __init__(self, *args, lang: Lang, **kwargs):
        self.lang = lang
        super().__init__(*args, **kwargs)
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        # Bind the language into closures so we don't rely on `self.lang`
        # lookup at render time — reportlab's onPage callback can be
        # invoked with a `doc` arg whose attribute namespace surprises us
        # if anyone subclasses BaseDocTemplate further.
        footer_text = (
            "AnnexKit — Architecture Overview · v0.1.x"
            if lang == "en"
            else "AnnexKit — Panoramica architettura · v0.1.x"
        )
        leftm = self.leftMargin
        bottomm = self.bottomMargin
        rightm = self.rightMargin
        page_w = self.pagesize[0]

        def _on_page(canvas: Canvas, doc: BaseDocTemplate) -> None:
            canvas.saveState()
            # Footer rule
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.5)
            canvas.line(
                leftm,
                bottomm - 0.3 * cm,
                page_w - rightm,
                bottomm - 0.3 * cm,
            )
            # Footer text
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(INK_MUTED)
            canvas.drawString(
                leftm,
                bottomm - 0.8 * cm,
                footer_text,
            )
            canvas.drawRightString(
                page_w - rightm,
                bottomm - 0.8 * cm,
                f"{doc.page}",
            )
            canvas.restoreState()

        self.addPageTemplates(
            [PageTemplate(id="default", frames=[frame], onPage=_on_page)],
        )


def build_cover(lang: Lang, styles: dict[str, ParagraphStyle]) -> list:
    """Cover page — title, subtitle, sage rule, meta."""
    title_en = "AnnexKit"
    title_it = "AnnexKit"
    subtitle_en = "Architecture Overview"
    subtitle_it = "Panoramica architetturale"
    blurb_en = (
        "Technical brief for engineering interviews and architecture "
        "diligence. Covers the system, the seven non-negotiables, the "
        "stack, the security model, the deployment shape, and the v0.2 "
        "roadmap."
    )
    blurb_it = (
        "Brief tecnico per colloqui di ingegneria e diligence "
        "architetturale. Copre il sistema, i sette punti non "
        "negoziabili, lo stack, il modello di sicurezza, la forma del "
        "deploy e la roadmap v0.2."
    )

    return [
        Spacer(1, 5 * cm),
        Paragraph(title_en if lang == "en" else title_it, styles["title"]),
        Paragraph(subtitle_en if lang == "en" else subtitle_it, styles["subtitle"]),
        # Sage rule
        Table(
            [[""]],
            colWidths=[5 * cm],
            rowHeights=[2.5 * mm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), SAGE)]),
        ),
        Spacer(1, 14 * mm),
        Paragraph(blurb_en if lang == "en" else blurb_it, styles["body"]),
        Spacer(1, 4 * cm),
        Paragraph(
            "Version v0.1.x · 2026-05-24" if lang == "en" else "Versione v0.1.x · 2026-05-24",
            styles["cover_meta"],
        ),
        Paragraph(
            "annexkit.dev · github.com/annexkit/annexkit"
            if lang == "en"
            else "annexkit.dev · github.com/annexkit/annexkit",
            styles["cover_meta"],
        ),
        PageBreak(),
    ]


def build_toc(lang: Lang, styles: dict[str, ParagraphStyle]) -> list:
    """Table of contents page — derived from the Heading blocks."""
    title_en = "Contents"
    title_it = "Indice"
    elements = [
        Paragraph(title_en if lang == "en" else title_it, styles["h1"]),
        Spacer(1, 6 * mm),
    ]

    for block in SECTIONS:
        if isinstance(block, Heading):
            text = block.en if lang == "en" else block.it
            elements.append(
                Paragraph(
                    f"<b>{block.number:>2}.</b> &nbsp;&nbsp;{text}",
                    styles["body"],
                )
            )

    elements.append(PageBreak())
    return elements


def build_content(lang: Lang, styles: dict[str, ParagraphStyle]) -> list:
    """Render the SECTIONS list to Platypus flowables."""
    elements: list = []

    for block in SECTIONS:
        if isinstance(block, Heading):
            text = block.en if lang == "en" else block.it
            elements.append(
                Paragraph(f"{block.number}. {text}", styles["h1"]),
            )
        elif isinstance(block, Subheading):
            text = block.en if lang == "en" else block.it
            elements.append(Paragraph(text, styles["h2"]))
        elif isinstance(block, Para):
            text = block.en if lang == "en" else block.it
            elements.append(Paragraph(text, styles["body"]))
        elif isinstance(block, Code):
            elements.append(Preformatted(block.text, styles["code"]))
            caption = block.caption_en if lang == "en" else block.caption_it
            if caption:
                elements.append(Paragraph(caption, styles["code_caption"]))
        elif isinstance(block, Bullets):
            items = [item[0] if lang == "en" else item[1] for item in block.items]
            for item in items:
                elements.append(
                    Paragraph(
                        f'<font color="{SAGE.hexval()}">›</font> &nbsp;{item}',
                        styles["bullet"],
                    )
                )
            elements.append(Spacer(1, 4))
        elif isinstance(block, KV):
            header = block.header_en if lang == "en" else block.header_it
            rows: list[list] = []
            if header is not None:
                rows.append([Paragraph(c, styles["body"]) for c in header])
            for key, value_pair in block.rows:
                value = value_pair[0] if lang == "en" else value_pair[1]
                rows.append(
                    [
                        Paragraph(f"<b>{key}</b>", styles["body"]),
                        Paragraph(value, styles["body"]),
                    ]
                )
            # Two-column: first narrow, second wide
            tbl = Table(
                rows,
                colWidths=[4 * cm, 12 * cm],
                style=make_table_style(len(rows)),
                hAlign="LEFT",
            )
            elements.append(tbl)
            elements.append(Spacer(1, 8))
        elif isinstance(block, Note):
            text = block.en if lang == "en" else block.it
            # Wrap in a sage-tinted left-border block
            note_para = Paragraph(f"<i>Note — {text}</i>" if lang == "en" else f"<i>Nota — {text}</i>", styles["note"])
            # Use a 1-cell table to give the note a sage left rule
            tbl = Table(
                [[note_para]],
                colWidths=[16 * cm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), SAGE_SOFT),
                        ("LINEBEFORE", (0, 0), (0, -1), 2, SAGE),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ],
                ),
                hAlign="LEFT",
            )
            elements.append(tbl)
            elements.append(Spacer(1, 12))

    return elements


def build_pdf(lang: Lang, output_path: Path) -> None:
    """Render the architecture brief in the requested language."""
    styles = make_styles()

    doc = ArchitectureDoc(
        str(output_path),
        lang=lang,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title="AnnexKit — Architecture Overview"
        if lang == "en"
        else "AnnexKit — Panoramica architettura",
        author="AnnexKit",
        subject="AnnexKit architecture brief (v0.1.x)"
        if lang == "en"
        else "Brief architetturale AnnexKit (v0.1.x)",
    )

    story: list = []
    story.extend(build_cover(lang, styles))
    story.extend(build_toc(lang, styles))
    story.extend(build_content(lang, styles))

    doc.build(story)


def main() -> None:
    desktop = Path(os.path.expanduser("~/Desktop"))
    out_en = desktop / "annexkit-architecture-en.pdf"
    out_it = desktop / "annexkit-architecture-it.pdf"

    print(f"-> Rendering EN to {out_en}")
    build_pdf("en", out_en)
    print(f"-> Rendering IT to {out_it}")
    build_pdf("it", out_it)
    print("Done.")


if __name__ == "__main__":
    main()
