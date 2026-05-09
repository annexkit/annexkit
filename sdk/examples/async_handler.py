"""Async handler example — a FastAPI-style coroutine traced by AnnexKit.

Run me directly to see span JSON on stderr:

    cd sdk
    uv run python examples/async_handler.py

No real LLM call — the function ``await``s a sleep to mimic an
async API client.
"""

from __future__ import annotations

import asyncio

from annexkit import track


@track(
    system_id="async-classifier",
    risk_tier="auto",
    purpose="classify incoming support tickets by urgency",
)
async def classify_ticket(ticket_id: str, body: str) -> str:
    await asyncio.sleep(0.02)
    return "urgent" if "outage" in body.lower() else "normal"


async def main() -> None:
    results = await asyncio.gather(
        classify_ticket("T-1", "Site outage in production"),
        classify_ticket("T-2", "How do I reset my password?"),
    )
    print("Classifications:", results)


if __name__ == "__main__":
    asyncio.run(main())
