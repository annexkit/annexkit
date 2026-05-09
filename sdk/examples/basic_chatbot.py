"""Basic synchronous chatbot example.

Run me directly to see span JSON on stderr:

    cd sdk
    uv run python examples/basic_chatbot.py

The example doesn't actually call OpenAI — it simulates an LLM response
so you don't need API keys to see AnnexKit spans flowing.
"""

from __future__ import annotations

import time

from annexkit import track


@track(
    system_id="customer-support-bot",
    risk_tier="auto",
    purpose="answer customer questions on shipping and returns",
)
def chat(user_msg: str, user_role: str = "customer") -> str:
    """Pretend to call an LLM and return an answer."""
    # Simulate latency so the recorded span has a non-zero duration.
    time.sleep(0.05)
    return f"(simulated answer to {user_msg!r} for role={user_role})"


def main() -> None:
    print(chat("how long does shipping take?"))
    print(chat("can I return after 30 days?", user_role="employee"))


if __name__ == "__main__":
    main()
