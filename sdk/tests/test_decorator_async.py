"""``@track`` async function tests."""

from __future__ import annotations

import asyncio

import pytest

from annexkit import track
from annexkit._hashing import hash_value


async def test_async_basic(collector) -> None:
    @track(system_id="async-bot", purpose="echo")
    async def echo(msg: str) -> str:
        await asyncio.sleep(0)
        return msg.upper()

    assert await echo("hi") == "HI"
    assert len(collector.spans) == 1
    span = collector.spans[0]
    assert span.system_id == "async-bot"
    assert span.input_hash == hash_value({"msg": "hi"})
    assert span.output_hash == hash_value("HI")
    assert span.error is None


async def test_async_exception(collector) -> None:
    @track(system_id="async-bot")
    async def boom() -> None:
        raise RuntimeError("kaboom")

    with pytest.raises(RuntimeError, match="kaboom"):
        await boom()
    assert "RuntimeError" in collector.spans[0].error


async def test_async_concurrent(collector) -> None:
    @track(system_id="async-bot")
    async def f(n: int) -> int:
        await asyncio.sleep(0)
        return n * 2

    results = await asyncio.gather(*(f(i) for i in range(20)))
    assert results == [i * 2 for i in range(20)]
    # All 20 spans recorded — concurrent calls don't drop spans.
    assert len(collector.spans) == 20
    # All distinct trace_ids.
    assert len({s.trace_id for s in collector.spans}) == 20
