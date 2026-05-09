"""``app.services.api_key`` contract tests.

The hashing functions are simple by design — these tests pin the format,
constant-time verify, and the looks_like_api_key fast-fail.
"""

from __future__ import annotations

from app.services import api_key as api_key_service


def test_generate_returns_plaintext_prefix_hash() -> None:
    g = api_key_service.generate()
    assert g.plaintext.startswith("ak_")
    assert len(g.plaintext) == len(api_key_service.PREFIX) + api_key_service.SUFFIX_LEN
    assert g.prefix == g.plaintext[: api_key_service.PREFIX_VISIBLE_LEN]
    # Hex digest of HMAC-SHA256 → 64 chars.
    assert len(g.key_hash) == 64
    assert all(c in "0123456789abcdef" for c in g.key_hash)


def test_generate_keys_are_unique() -> None:
    keys = {api_key_service.generate().plaintext for _ in range(100)}
    assert len(keys) == 100  # tiny chance of collision; not in practice


def test_hash_key_is_deterministic() -> None:
    g = api_key_service.generate()
    again = api_key_service.hash_key(g.plaintext)
    assert g.key_hash == again


def test_verify_accepts_correct_key() -> None:
    g = api_key_service.generate()
    assert api_key_service.verify(g.plaintext, g.key_hash) is True


def test_verify_rejects_wrong_key() -> None:
    g = api_key_service.generate()
    assert api_key_service.verify("ak_xxxxxxxxxxxxxxxxxxxxxxxx", g.key_hash) is False


def test_looks_like_api_key_accepts_real() -> None:
    g = api_key_service.generate()
    assert api_key_service.looks_like_api_key(g.plaintext) is True


def test_looks_like_api_key_rejects_garbage() -> None:
    assert api_key_service.looks_like_api_key("") is False
    assert api_key_service.looks_like_api_key("ak_") is False
    assert api_key_service.looks_like_api_key("ak_short") is False
    # Wrong prefix
    assert api_key_service.looks_like_api_key("xy_" + "a" * 24) is False
    # Disallowed char (uppercase / 0 / 1 / l / o)
    assert api_key_service.looks_like_api_key("ak_" + "A" * 24) is False
    assert api_key_service.looks_like_api_key("ak_" + "1" * 24) is False
