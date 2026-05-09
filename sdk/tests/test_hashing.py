"""Hash function contract tests.

The hashing helpers underpin the SDK's privacy guarantee. If their
behaviour drifts, audit logs become unstable. Every test here pins a
specific contract; don't loosen them lightly.
"""

from __future__ import annotations

from annexkit._hashing import (
    hash_text,
    hash_value,
    measure_chars,
    serialize,
)


def test_hash_text_none_passes_through() -> None:
    assert hash_text(None) is None


def test_hash_text_empty_string_hashes() -> None:
    digest = hash_text("")
    assert digest is not None
    assert len(digest) == 64


def test_hash_text_idempotent() -> None:
    assert hash_text("hello") == hash_text("hello")


def test_hash_text_known_vector() -> None:
    # SHA-256 of "hello" UTF-8.
    assert (
        hash_text("hello")
        == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )


def test_serialize_dict_order_independent() -> None:
    a = serialize({"x": 1, "y": 2})
    b = serialize({"y": 2, "x": 1})
    assert a == b


def test_hash_value_dict_order_independent() -> None:
    assert hash_value({"x": 1, "y": 2}) == hash_value({"y": 2, "x": 1})


def test_hash_value_str_equals_hash_text() -> None:
    assert hash_value("hello") == hash_text("hello")


def test_hash_value_none_returns_none() -> None:
    assert hash_value(None) is None


def test_hash_value_empty_string_hashes() -> None:
    digest = hash_value("")
    assert digest is not None and len(digest) == 64


def test_serialize_unjsonable_uses_default_str() -> None:
    """default=str makes json.dumps wrap str(obj) in JSON quotes."""

    class Opaque:
        def __repr__(self) -> str:
            return "<Opaque>"

    # str(Opaque()) defaults to __repr__, json wraps in quotes → '"<Opaque>"'.
    # Determinism is the contract; the exact form is implementation detail.
    assert serialize(Opaque()) == '"<Opaque>"'


def test_serialize_unjsonable_repr_fallback_when_default_fails() -> None:
    """If even ``default=str`` fails, repr() is the last resort."""

    class Mean:
        def __str__(self) -> str:
            raise RuntimeError("nope")

    out = serialize(Mean())
    assert "Mean" in out


def test_measure_chars_none() -> None:
    assert measure_chars(None) is None


def test_measure_chars_string() -> None:
    assert measure_chars("hello") == 5


def test_measure_chars_dict_uses_json() -> None:
    # json.dumps default separators include a space after ',' and ':'.
    # Form: '{"a": 1, "b": 2}' → 16 chars.
    assert measure_chars({"a": 1, "b": 2}) == 16
