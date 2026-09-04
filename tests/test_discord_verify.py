"""Discord Ed25519 Interactions signature verification."""

from __future__ import annotations

import time

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from operator_etl_chat.discord.verify import DiscordSignatureError, verify_discord_signature


def _sign(body: bytes, timestamp: str) -> tuple[str, str]:
    private = Ed25519PrivateKey.generate()
    public_hex = private.public_key().public_bytes_raw().hex()
    message = timestamp.encode("utf-8") + body
    signature_hex = private.sign(message).hex()
    return public_hex, signature_hex


def test_verify_accepts_valid_signature() -> None:
    body = b'{"type":1}'
    timestamp = str(int(time.time()))
    public_hex, signature_hex = _sign(body, timestamp)
    verify_discord_signature(
        public_key_hex=public_hex,
        signature_hex=signature_hex,
        timestamp=timestamp,
        body=body,
    )


def test_verify_rejects_bad_signature() -> None:
    body = b'{"type":1}'
    timestamp = str(int(time.time()))
    public_hex, _ = _sign(body, timestamp)
    with pytest.raises(DiscordSignatureError, match="signature"):
        verify_discord_signature(
            public_key_hex=public_hex,
            signature_hex="00" * 64,
            timestamp=timestamp,
            body=body,
        )


def test_verify_rejects_timestamp_skew() -> None:
    body = b'{"type":1}'
    old_ts = str(int(time.time()) - 10_000)
    public_hex, signature_hex = _sign(body, old_ts)
    with pytest.raises(DiscordSignatureError, match="skew"):
        verify_discord_signature(
            public_key_hex=public_hex,
            signature_hex=signature_hex,
            timestamp=old_ts,
            body=body,
            now=time.time(),
        )


def test_verify_rejects_missing_headers() -> None:
    with pytest.raises(DiscordSignatureError, match="missing"):
        verify_discord_signature(
            public_key_hex="ab" * 32,
            signature_hex="",
            timestamp="",
            body=b"{}",
        )
