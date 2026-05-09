"""Context-manager example — tracing a multi-step RAG pipeline.

Run me directly:

    cd sdk
    uv run python examples/with_session.py

The retrieval and LLM calls are simulated. The ``annexkit.session(...)``
form is the right shape when you can't decorate a single function — for
example when each retrieval and each model call happens in a notebook
cell or deep inside an agent loop.
"""

from __future__ import annotations

import annexkit


def main() -> None:
    with annexkit.session(
        system_id="policy-rag",
        risk_tier="auto",
        purpose="answer customer questions from internal policy KB",
    ) as span:
        user_query = "what's the refund policy after 14 days?"
        span.set_input(user_query)
        span.set_user_role("customer")

        # Pretend retrieval.
        for src in [
            ("kb://policies/refund-v3", "abc123", "v3"),
            ("kb://policies/general-tos", "def456", "v1.4"),
        ]:
            span.attach_source(uri=src[0], hash=src[1], version=src[2])

        # Pretend LLM call.
        span.set_model(provider="mistral", name="mistral-small-latest")
        answer = "After 14 days refunds are case-by-case; please contact support."
        span.set_output(answer)

        span.add_metadata(retrieval_k=2, channel="web")

        print("Answer:", answer)


if __name__ == "__main__":
    main()
