"""Privacy-preserving hashing utilities.

Per the project's non-negotiable #7 (see ../CLAUDE.md), the SDK never logs
plaintext input/output by default — every payload is SHA-256 hashed
before it leaves the host. Hex digests are easy to grep and easy to
compare across audit logs without leaking the underlying text.

Usage:
    >>> hash_text("hello")
    '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
    >>> hash_value({"a": 1, "b": 2}) == hash_value({"b": 2, "a": 1})
    True
"""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any


def hash_text(text: str | None) -> str | None:
    """SHA-256 hex of a UTF-8 string. ``None`` passes through unchanged.

    Idempotent: ``hash_text(x)`` always returns the same digest for the
    same ``x``.
    """
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def serialize(value: Any) -> str:
    """Stable string representation for hashing arbitrary Python values.

    Strategy:
      1. ``None`` → empty string.
      2. ``str`` → as-is.
      3. ``bytes`` → base64-encoded.
      4. JSON-serialisable → ``json.dumps(..., sort_keys=True)`` so dict
         key order doesn't change the hash.
      5. Anything else → ``repr(...)`` as last resort.

    Determinism is the contract: the same logical input must produce the
    same string on retry. Tests assert this directly.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    try:
        return json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    except Exception:
        # Broad except is intentional: a custom __str__ that raises
        # shouldn't crash a tracing call. repr() is the last-resort
        # deterministic-ish fallback.
        try:
            return repr(value)
        except Exception:
            return f"<unrepresentable {type(value).__name__}>"


def hash_value(value: Any) -> str | None:
    """Convenience: ``serialize(value)`` then ``hash_text(...)``.

    Returns ``None`` only when the serialised form is the empty string
    (i.e. the input was ``None``). Empty strings, empty dicts, etc. all
    produce a real digest because they are observable user inputs that
    deserve audit trails.
    """
    serialised = serialize(value)
    if serialised == "" and value is None:
        return None
    return hash_text(serialised)


def measure_chars(value: Any) -> int | None:
    """Char count of the serialised form, for span metadata.

    Auditors care about "how much text did the model see?" — hash alone
    doesn't answer that.
    """
    if value is None:
        return None
    return len(serialize(value))
