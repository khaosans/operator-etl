"""Discord Interactions Ed25519 signature verification."""

from __future__ import annotations

import os
import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# Discord recommends rejecting timestamps outside a short window (replay protection).
_MAX_TIMESTAMP_SKEW_SECONDS = 300


class DiscordSignatureError(Exception):
    """Raised when an Interactions request fails signature or timestamp checks."""


def _public_key_from_hex(hex_key: str) -> Ed25519PublicKey:
    try:
        raw = bytes.fromhex(hex_key.strip())
    except ValueError as exc:
        raise DiscordSignatureError("invalid public key encoding") from exc
    if len(raw) != 32:
        raise DiscordSignatureError("invalid public key length")
    return Ed25519PublicKey.from_public_bytes(raw)


def configured_public_key() -> str:
    key = os.environ.get("OPERATOR_ETL_DISCORD_PUBLIC_KEY", "").strip()
    if not key:
        raise DiscordSignatureError("OPERATOR_ETL_DISCORD_PUBLIC_KEY not configured")
    return key


def verify_discord_signature(
    *,
    public_key_hex: str,
    signature_hex: str,
    timestamp: str,
    body: bytes,
    now: float | None = None,
    max_skew_seconds: int = _MAX_TIMESTAMP_SKEW_SECONDS,
) -> None:
    """Verify Discord Interactions signature (Ed25519 over timestamp + body).

    Raises DiscordSignatureError on any failure. Does not leak key material in messages.
    """
    if not signature_hex or not timestamp:
        raise DiscordSignatureError("missing signature headers")

    try:
        ts = int(timestamp)
    except (TypeError, ValueError) as exc:
        raise DiscordSignatureError("invalid timestamp") from exc

    current = time.time() if now is None else now
    if abs(current - ts) > max_skew_seconds:
        raise DiscordSignatureError("timestamp skew exceeded")

    try:
        signature = bytes.fromhex(signature_hex)
    except ValueError as exc:
        raise DiscordSignatureError("invalid signature encoding") from exc

    message = timestamp.encode("utf-8") + body
    public_key = _public_key_from_hex(public_key_hex)
    try:
        public_key.verify(signature, message)
    except InvalidSignature as exc:
        raise DiscordSignatureError("signature verification failed") from exc
