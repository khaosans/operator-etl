"""Outbound Discord HITL alerts via Incoming Webhook (env-gated, fail-soft)."""

from __future__ import annotations

import logging
import os
from typing import Any
from urllib.parse import urlparse

import httpx

from operator_etl_chat.sanitize import format_hitl_discord_content, sanitize_hitl_payload

logger = logging.getLogger("operator_etl_chat.discord")

_ALLOWED_WEBHOOK_HOSTS = frozenset({"discord.com", "discordapp.com"})


def _webhook_url() -> str | None:
    url = os.environ.get("OPERATOR_ETL_DISCORD_WEBHOOK_URL", "").strip()
    return url or None


def _is_safe_webhook_url(url: str) -> bool:
    """Reject non-HTTPS or non-Discord hosts (SSRF hygiene)."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme != "https":
        return False
    host = (parsed.hostname or "").lower()
    if host not in _ALLOWED_WEBHOOK_HOSTS and not host.endswith(".discord.com"):
        return False
    if not parsed.path.startswith("/api/webhooks/"):
        return False
    return True


class DiscordWebhookNotifier:
    """ChatNotifier implementation using a Discord Incoming Webhook URL."""

    def __init__(self, webhook_url: str | None = None, *, timeout: float = 5.0) -> None:
        self._webhook_url = webhook_url if webhook_url is not None else _webhook_url()
        self._timeout = timeout

    def notify_hitl(self, payload: dict[str, Any]) -> bool:
        if not self._webhook_url:
            return False
        if not _is_safe_webhook_url(self._webhook_url):
            logger.warning("discord_hitl_skipped: unsafe webhook url")
            return False
        clean = sanitize_hitl_payload(payload)
        content = format_hitl_discord_content(clean)
        body = {"content": content[:1900]}
        try:
            response = httpx.post(self._webhook_url, json=body, timeout=self._timeout)
            if response.status_code >= 400:
                logger.warning(
                    "discord_hitl_failed: status=%s type=%s",
                    response.status_code,
                    type(response).__name__,
                )
                return False
            return True
        except Exception as exc:
            # Fail-soft: never break the FOIA pipeline because Discord is down.
            logger.warning("discord_hitl_failed: %s: %s", type(exc).__name__, exc)
            return False


def notify_hitl_discord(payload: dict[str, Any]) -> bool:
    """Module-level helper used by the graph needs_human node."""
    return DiscordWebhookNotifier().notify_hitl(payload)
