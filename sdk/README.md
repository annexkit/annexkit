# annexkit — EU AI Act compliance pipeline for developers

> One decorator. Audit-ready evidence. EU-hosted.

`pip install annexkit` and the SDK turns every LLM invocation in your
codebase into Article 12 audit log entries plus an Annex IV
technical-documentation feed for the EU AI Act
(Reg. 2024/1689).

```python
from annexkit import track

@track(
    system_id="customer-support-bot",
    risk_tier="auto",
    purpose="answer customer questions on shipping and returns",
)
def chat(user_msg: str, user_role: str = "customer") -> str:
    return openai.chat.completions.create(...).choices[0].message.content
```

## What gets recorded

Every call captures, by default:

| Field | What it holds |
|---|---|
| `system_id` / `deployment` | Stable identifiers you choose |
| `risk_tier` / `purpose` | AI Act metadata for Annex IV §1 + §4 |
| `started_at` / `ended_at` / `latency_ms` | Timing in UTC |
| `input_hash` / `output_hash` | SHA-256 hex (privacy-preserving) |
| `input_chars` / `output_chars` | Char count of serialised payloads |
| `model_provider` / `model_name` / `model_version` | When set explicitly |
| `sources[]` | Retrieval provenance for RAG |
| `user_role` | Article 13/14 oversight context |
| `error` | `<module>.<class>: <message>` on exception |
| `metadata` | Free-form `dict` |
| `sdk_version` / `sdk_lang` | Provenance |

**Plaintext content is never logged by default.** Hashes only — that's
the privacy-by-default invariant
(see [`../CLAUDE.md`](../CLAUDE.md) non-negotiable #7).

## Install

> **Pre-PyPI**: AnnexKit is in active MVP development. The PyPI listing
> goes live at v1.0 (Day 7 of the MVP roadmap). For now install from
> source:

```bash
git clone https://github.com/annexkit/annexkit
cd annexkit/sdk
uv sync          # or: pip install -e .
```

When the package lands on PyPI:

```bash
pip install annexkit            # coming at v1.0
# or
uv add annexkit
```

Python ≥ 3.10. Only two runtime deps: `httpx` and `pydantic`.

## Quickstart

### 1. Decorate sync functions

```python
from annexkit import track

@track(system_id="loan-screener", purpose="pre-screen credit applications")
def screen(applicant: dict) -> str:
    return llm.classify(applicant)
```

### 2. Decorate async functions

```python
@track(system_id="async-classifier")
async def classify(ticket_id: str, body: str) -> str:
    return await llm.acomplete(body)
```

The decorator auto-detects sync vs async — same API, no flag needed.

### 3. Multi-step blocks via the context manager

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
single function (notebook cells, agent loops, orchestration scripts).

### 4. Configure via env or code

```bash
export ANNEXKIT_API_KEY=ak_xxxxx
export ANNEXKIT_COLLECTOR_URL=https://collector.annexkit.dev
export ANNEXKIT_DEPLOYMENT=prod
```

Or programmatically:

```python
import annexkit
annexkit.configure(api_key="ak_xxxxx", deployment="staging")
```

| Env var | Default | Purpose |
|---|---|---|
| `ANNEXKIT_API_KEY` | unset | When set, switches to HTTP exporter |
| `ANNEXKIT_COLLECTOR_URL` | `https://collector.annexkit.dev` | Collector endpoint |
| `ANNEXKIT_EXPORTER` | `auto` | `auto`/`stdout`/`http`/`noop` |
| `ANNEXKIT_DISABLED` | `0` | Set `1` to disable tracking globally |
| `ANNEXKIT_DEPLOYMENT` | `prod` | Default deployment label for spans |

### 5. Stdout in dev, HTTP in prod

With no API key, AnnexKit prints one JSON span per line to **stderr** —
perfect for testing, log shipping, or `jq` exploration:

```text
{"system_id":"customer-support-bot","trace_id":"...","input_hash":"2cf24dba...",...}
```

Set `ANNEXKIT_API_KEY` and the same span is POSTed to the collector
instead.

## Examples

Runnable examples in [`examples/`](examples/):

```bash
cd sdk
uv sync
uv run python examples/basic_chatbot.py
uv run python examples/async_handler.py
uv run python examples/with_session.py
```

Each prints span JSON on stderr — no API keys required.

## Custom exporters

Subclass `annexkit.exporters.Exporter` and pass an instance:

```python
from annexkit.exporters import Exporter
from annexkit.schema import Span

class MyExporter(Exporter):
    def export(self, span: Span) -> None:
        my_observability_platform.publish(span.model_dump())

import annexkit
annexkit.configure(exporter=MyExporter())
```

The base class never raises from `export()` — your subclass shouldn't
either. Catching and logging exporter failures is the contract.

## Public API

```python
from annexkit import (
    track,             # decorator
    session,           # context manager
    configure,         # runtime override
    flush, shutdown,   # lifecycle
    Span, Source,      # data types
    SpanHandle,        # session yield type
    __version__,
)
from annexkit.exporters import Exporter, StdoutExporter, HttpExporter
```

## Testing your code with AnnexKit

The SDK ships a `CollectingExporter` pattern in
[`tests/conftest.py`](tests/conftest.py) you can copy into your own test
suite to assert on emitted spans without hitting the network:

```python
from annexkit.exporters.base import Exporter

class CollectingExporter(Exporter):
    def __init__(self) -> None:
        self.spans = []
    def export(self, span):
        self.spans.append(span)
```

Then:

```python
def test_my_handler():
    exporter = CollectingExporter()
    annexkit.configure(exporter=exporter)
    my_handler("input")
    assert exporter.spans[0].system_id == "my-handler"
```

## Status

**v0.1.0 (Day 2 of MVP)** — sync + async decorator, session manager,
stdout + HTTP exporters, config via env or code, 40+ unit tests.
The collector ingest endpoint (`POST /api/v1/spans`) lands in Day 3 of
the MVP — until then the HTTP exporter has nothing real to talk to.
Track progress in [`../README.md`](../README.md).

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT — see [`LICENSE`](LICENSE).

## Disclaimer

AnnexKit is not a law firm. The Annex IV documents and risk
classifications it produces are technical evidence; interpretation is
the responsibility of your legal team or external counsel.
