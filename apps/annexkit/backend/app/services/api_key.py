"""API key generation, hashing, and constant-time verification.

Design:
    * **Format**: ``ak_`` + 24 random base32 chars from a high-entropy
      alphabet → 27 chars total. Friendly to copy/paste, easy to grep.
    * **Hash**: HMAC-SHA256(SECRET_KEY, full_key), hex-encoded. Stored
      in ``api_keys.key_hash``. The plaintext key is shown to the user
      exactly once at generation time — never stored, never logged.
    * **Prefix**: first 11 chars of the plaintext (``ak_xxxxxxxx``).
      Visible in dashboards so a user can identify their keys without
      seeing the secret.
    * **Verify**: constant-time ``hmac.compare_digest`` to avoid timing
      attacks revealing the hash byte-by-byte.

Not bcrypt because:
    * Bcrypt is for low-entropy human passwords. API keys are 24 random
      chars from a 32-symbol alphabet → 120 bits of entropy — already
      uncrackable. HMAC is the right primitive for high-entropy secrets.
    * HMAC verification is microseconds; bcrypt is ~250ms per attempt.
      The latter would dominate every authenticated request.
    * HMAC is keyed: a leaked DB without ``SECRET_KEY`` is useless to an
      attacker. Bcrypt would be crackable offline given enough GPU time.

Rotation:
    * To rotate ``SECRET_KEY``: regenerate every API key. (No transparent
      re-hash because the hashes are not reversible.) An admin endpoint
      to bulk-revoke + reissue lands in M4.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

from app.config import Settings
from app.config import settings as _module_settings

#: Base32-ish alphabet (excludes ambiguous chars: 0/O, 1/l/I).
#: 32 symbols → 5 bits per char. 24 chars → 120 bits of entropy.
_KEY_ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"
_KEY_SUFFIX_LEN = 24
_KEY_PREFIX = "ak_"
_PREFIX_VISIBLE_LEN = 11  # "ak_" + 8 of the suffix


@dataclass(frozen=True)
class GeneratedKey:
    """Result of :func:`generate`. The plaintext is shown to the user
    once; the rest persists in the DB."""

    plaintext: str
    prefix: str
    key_hash: str


def generate(*, settings_override: Settings | None = None) -> GeneratedKey:
    """Mint a fresh API key. Returns plaintext + persistence material."""
    settings = settings_override or _module_settings
    suffix = "".join(secrets.choice(_KEY_ALPHABET) for _ in range(_KEY_SUFFIX_LEN))
    plaintext = f"{_KEY_PREFIX}{suffix}"
    return GeneratedKey(
        plaintext=plaintext,
        prefix=plaintext[:_PREFIX_VISIBLE_LEN],
        key_hash=_hmac(plaintext, settings.secret_key),
    )


def hash_key(plaintext: str, *, settings_override: Settings | None = None) -> str:
    """HMAC-SHA256 of ``plaintext`` keyed by ``SECRET_KEY``, hex.

    Use during auth to look up the matching ``api_keys`` row. The lookup
    is O(1) thanks to the unique index on ``key_hash``.
    """
    settings = settings_override or _module_settings
    return _hmac(plaintext, settings.secret_key)


def verify(plaintext: str, stored_hash: str, *, settings_override: Settings | None = None) -> bool:
    """Constant-time check that ``plaintext`` hashes to ``stored_hash``."""
    return hmac.compare_digest(
        hash_key(plaintext, settings_override=settings_override),
        stored_hash,
    )


def looks_like_api_key(value: str) -> bool:
    """Cheap pre-validation before hitting the DB.

    Catches truncation / typos before we waste a DB lookup. Not a
    security boundary — just an early-fail for obvious garbage.
    """
    if not value.startswith(_KEY_PREFIX):
        return False
    suffix = value[len(_KEY_PREFIX) :]
    if len(suffix) != _KEY_SUFFIX_LEN:
        return False
    return all(c in _KEY_ALPHABET for c in suffix)


def _hmac(plaintext: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        plaintext.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# Re-export the constants so tests + admin tooling don't have to dig.
ALPHABET = _KEY_ALPHABET
SUFFIX_LEN = _KEY_SUFFIX_LEN
PREFIX = _KEY_PREFIX
PREFIX_VISIBLE_LEN = _PREFIX_VISIBLE_LEN
