"""Thin Mistral La Plateforme client — single integration point for embeddings + chat.

Why wrap the Mistral SDK?

1. **EU residency invariant.** The whole point of choosing Mistral over
   OpenAI/Anthropic for hot-path LLM traffic is GDPR + Italian SME
   expectations around data sovereignty. Routing everything through one
   module makes the boundary auditable — one `grep` for `MistralClient`
   shows every place we actually leave the process.

2. **Testability.** Embedding and chat calls are what we stub in tests.
   A narrow Protocol + dataclass return shapes means a `StubMistralClient`
   with deterministic responses is trivial to write.

3. **Config enforcement.** We want a predictable `MistralNotConfiguredError`
   when the API key is blank (dev without billing) rather than a surprise
   `AuthenticationException` deep in a request flow.

Keep this file tiny. No business logic, no prompt assembly — that lives
in `copilot_service`. Only SDK wiring, error normalisation, test stubs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

# Note on the import path: `mistralai` v2.x re-arranged the namespace and
# the `Mistral` class now lives under `mistralai.client`, not the top-level
# package. Importing from `.client` works across 2.x and is robust to the
# top-level `__init__` being empty in some packaging configurations.
from mistralai.client import Mistral

from app.config import Settings


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------
class MistralNotConfiguredError(RuntimeError):
    """Raised when we try to call Mistral without a configured API key.

    Route handlers should turn this into a 503 — it's a server-side misconfig,
    not a user error. The copilot API explicitly maps it so Business
    customers don't see a cryptic 500 during a Mistral outage / missing
    key.
    """


# ---------------------------------------------------------------------------
# Return shape — kept minimal so callers don't depend on Mistral's types.
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class ChatMessage:
    """Single message in a chat completion call. Only roles we use."""

    role: str  # "system" | "user" | "assistant"
    content: str


# ---------------------------------------------------------------------------
# Protocol — lets tests inject a stub without subclassing concrete code.
# ---------------------------------------------------------------------------
class MistralClient(Protocol):
    """Just the surface the copilot actually touches. Narrow on purpose."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text, in order.

        Raises `MistralNotConfiguredError` if the key is missing. Must
        return `EMBEDDING_DIM`-length vectors — callers rely on this.
        """
        ...

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = 1024,
    ) -> str:
        """Return the assistant message content for the given conversation.

        We default to a very low temperature because the copilot is a
        grounded-QA system — creativity is a bug, not a feature. The
        model should quote the retrieved chunks, not invent.
        """
        ...


# ---------------------------------------------------------------------------
# Real implementation — hits the network, EU region.
# ---------------------------------------------------------------------------
class RealMistralClient:
    """Production client — one instance per process.

    The Mistral SDK is async-friendly; we expose only the two methods we
    actually need, so the rest of the codebase never imports `mistralai`
    directly (keeping the dependency boundary narrow for future swaps).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # `api_key=None` is allowed — the SDK will reject calls at runtime.
        # We check for ourselves in `ensure_configured()` so the error
        # message is ours.
        self._client: Mistral | None = None
        if settings.mistral_api_key:
            self._client = Mistral(api_key=settings.mistral_api_key)

    # ---- helpers ----------------------------------------------------------
    def ensure_configured(self) -> None:
        """Fail fast if the API key is missing. Copilot routes call this
        before any network work so the 503 lands before audit writes."""
        if self._client is None:
            raise MistralNotConfiguredError(
                "MISTRAL_API_KEY is not set. Copilot is disabled."
            )

    # ---- API --------------------------------------------------------------
    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.ensure_configured()
        assert self._client is not None  # for the type checker
        # The SDK batches under the hood; still pass the whole list so we
        # round-trip once per batch rather than per text.
        resp = await self._client.embeddings.create_async(
            model=self._settings.mistral_embed_model,
            inputs=texts,
        )
        # `resp.data` is a list of `EmbeddingObject` — `.embedding` is the
        # raw vector. Order is guaranteed to match `texts`.
        return [list(d.embedding) for d in resp.data]

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = 1024,
    ) -> str:
        self.ensure_configured()
        assert self._client is not None
        # Translate our tiny dataclass into the SDK's dict shape. Doing
        # it here keeps `ChatMessage` SDK-free so tests can build them
        # without importing `mistralai`.
        payload: list[dict[str, Any]] = [
            {"role": m.role, "content": m.content} for m in messages
        ]
        resp = await self._client.chat.complete_async(
            model=self._settings.mistral_chat_model,
            messages=payload,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # `choices[0].message.content` — mirrors the OpenAI shape. The SDK
        # wraps it in a pydantic model so coerce to str for safety.
        choice = resp.choices[0]
        return str(choice.message.content or "")


# ---------------------------------------------------------------------------
# Dependency factory — cached per-process.
# ---------------------------------------------------------------------------
_real_client: RealMistralClient | None = None


def get_mistral(settings: Settings) -> MistralClient:
    """Return the process-wide `RealMistralClient`.

    Tests override this FastAPI dependency with a stub — see
    `tests/conftest.py` / per-test fixtures.
    """
    global _real_client
    if _real_client is None:
        _real_client = RealMistralClient(settings)
    return _real_client
