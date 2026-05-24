# annexkit

> EU AI Act compliance pipeline — Python SDK.

[![PyPI version](https://img.shields.io/pypi/v/annexkit.svg?style=flat-square&color=3d7aff)](https://pypi.org/project/annexkit/)
[![Python versions](https://img.shields.io/pypi/pyversions/annexkit.svg?style=flat-square)](https://pypi.org/project/annexkit/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/annexkit/annexkit/blob/main/sdk/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/annexkit/annexkit?style=flat-square&color=3d7aff)](https://github.com/annexkit/annexkit)

One decorator on your LLM call. Audit-ready **Annex IV** technical
documentation under
[Reg. (EU) 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
out the other end.

```python
from annexkit import track

@track(
    system_id="customer-support-bot",
    risk_tier="auto",
    purpose="answer customer questions on shipping and returns",
)
def chat(user_msg: str, user_role: str = "customer") -> str:
    return openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_msg}],
    ).choices[0].message.content
```

That decorator:

- emits a **span** on every call (Article 12 logging),
- ships it to the collector — or your own exporter,
- feeds the system's **Annex IV** technical documentation, generated
  on demand at the collector.

Inputs and outputs are SHA-256 hashed before they leave your host.
Plaintext logging is opt-in.

---

## Install

```bash
pip install annexkit
```

Python ≥ 3.10. Two runtime deps: `httpx` and `pydantic`.

## Quickstart

### 1. Decorate

```python
from annexkit import track

@track(system_id="loan-screener", purpose="pre-screen credit applications")
def screen(applicant: dict) -> str:
    return llm.classify(applicant)
```

Sync or async — the decorator auto-detects. Same API, no flag.

### 2. Two modes — stdout in dev, HTTP in prod

**Without an API key**, AnnexKit prints one JSON span per call to
**stderr**. Perfect for local dev, log shipping, or `jq` exploration:

```text
{"system_id":"loan-screener","trace_id":"...","input_hash":"2cf24dba...","latency_ms":523,...}
```

**With `ANNEXKIT_API_KEY` set**, the same span is POSTed to the
collector:

```bash
export ANNEXKIT_API_KEY=ak_xxxxx
export ANNEXKIT_COLLECTOR_URL=https://annexkit.dev
```

Or programmatically:

```python
import annexkit
annexkit.configure(api_key="ak_xxxxx", deployment="staging")
```

### 3. Async — same API

```python
@track(system_id="async-classifier")
async def classify(ticket_id: str, body: str) -> str:
    return await llm.acomplete(body)
```

### 4. Multi-step via context manager

```python
import annexkit

with annexkit.session(
    system_id="policy-rag",
    purpose="answer customer questions from policy KB",
) as span:
    span.set_input(user_query)
    docs = retriever.search(user_query)
    for d in docs:
        span.attach_source(uri=d.uri, hash=d.hash, version=d.version)
    answer = llm.generate(user_query, docs)
    span.set_output(answer)
    span.set_model(provider="mistral", name="mistral-small-latest")
```

`annexkit.session(...)` is the right shape when you can't decorate a
single function — notebook cells, agent loops, orchestration scripts.

## What gets recorded

| Field | What it holds |
|---|---|
| `system_id` / `deployment` | Stable identifiers you choose |
| `risk_tier` / `purpose` | AI Act metadata for Annex IV |
| `started_at` / `ended_at` / `latency_ms` | Timing in UTC |
| `input_hash` / `output_hash` | SHA-256 hex (privacy-preserving) |
| `input_chars` / `output_chars` | Char counts of payloads |
| `model_provider` / `model_name` / `model_version` | When set explicitly |
| `sources[]` | Retrieval provenance for RAG |
| `user_role` | Article 13 / 14 oversight context |
| `error` | `<module>.<class>: <message>` on exception |
| `metadata` | Free-form `dict` for adapter authors |
| `sdk_version` / `sdk_lang` | Provenance |

Plaintext payloads are never logged by default — privacy-by-default
is wired into the SDK, not a config flag.

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `ANNEXKIT_API_KEY` | unset | When set, switches to HTTP exporter |
| `ANNEXKIT_COLLECTOR_URL` | `https://annexkit.dev` | Collector endpoint |
| `ANNEXKIT_EXPORTER` | `auto` | `auto` / `stdout` / `http` / `noop` |
| `ANNEXKIT_DISABLED` | `0` | Set to `1` to disable tracking globally |
| `ANNEXKIT_DEPLOYMENT` | `prod` | Default deployment label for spans |

## Custom exporters

```python
from annexkit.exporters import Exporter
from annexkit.schema import Span

class MyExporter(Exporter):
    def export(self, span: Span) -> None:
        my_observability_platform.publish(span.model_dump())

import annexkit
annexkit.configure(exporter=MyExporter())
```

Subclasses must never raise from `export()` — catch and log inside.
That's the contract; the base class will never raise either.

## Public API

```python
from annexkit import (
    track,             # decorator (sync + async)
    session,           # context manager
    configure,         # runtime override
    flush, shutdown,   # lifecycle helpers
    Span, Source,      # data types
    SpanHandle,        # session yield type
    __version__,
)
from annexkit.exporters import Exporter, StdoutExporter, HttpExporter
```

## Testing your code with AnnexKit

A common pattern: a `CollectingExporter` that captures spans into a
list, so your tests can assert on what was emitted without hitting the
network.

```python
from annexkit.exporters import Exporter

class CollectingExporter(Exporter):
    def __init__(self) -> None:
        self.spans = []
    def export(self, span):
        self.spans.append(span)
```

```python
def test_my_handler():
    exporter = CollectingExporter()
    annexkit.configure(exporter=exporter)
    my_handler("input")
    assert exporter.spans[0].system_id == "my-handler"
```

## Status

`v0.1.x` — sync + async decorator, session manager, stdout + HTTP
exporters, config via env or code. 48 unit tests with
`httpx.MockTransport` for hermetic HTTP coverage (zero real network
in CI).

The hosted collector at
[annexkit.dev](https://annexkit.dev) is in **early access**. The
self-host path (`docker compose up` against the
[repo](https://github.com/annexkit/annexkit)) is available today
under AGPL-3.0.

## Roadmap (v0.2)

- Mistral advisor for ambiguous declarations (hard guardrail: never
  declassifies a system the rules engine flagged)
- LangChain + LlamaIndex auto-instrumentation
  (`annexkit.auto_instrument(["langchain"])`)
- TypeScript / JavaScript SDK (`@annexkit/node`) — same wire format,
  same env-var conventions
- Async HTTP exporter (`httpx.AsyncClient`)
- Span batching + retry on transient failure
- OpenTelemetry GenAI semconv compliance — emit OTel-native spans
  alongside the AnnexKit-specific extensions

Full
[CHANGELOG](https://github.com/annexkit/annexkit/blob/main/sdk/CHANGELOG.md).

## Links

- 🌐 Website: <https://annexkit.dev>
- 📦 PyPI: <https://pypi.org/project/annexkit/>
- 💻 Source: <https://github.com/annexkit/annexkit>
- 🐛 Issues: <https://github.com/annexkit/annexkit/issues>
- 📜 EU AI Act (Reg. 2024/1689): [eur-lex.europa.eu](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
- 📨 Contact: <founder@annexkit.dev>

## License

MIT — see
[LICENSE](https://github.com/annexkit/annexkit/blob/main/sdk/LICENSE).

The hosted collector and trust-center frontend are AGPL-3.0; the SDK
is MIT so you can drop it into any codebase without copyleft concerns.
Same dual-licence arrangement Sentry, PostHog, and MinIO use.

## Disclaimer

AnnexKit is not a law firm; AnnexKit non è uno studio legale. The
Annex IV documents and risk classifications it produces are technical
artefacts; legal interpretation is the responsibility of your legal
team or external counsel.
