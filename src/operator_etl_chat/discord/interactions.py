"""FastAPI router for Discord Interactions (POST /discord/interactions)."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from operator_etl_chat.discord.commands import DiscordCommandHandler
from operator_etl_chat.discord.verify import (
    DiscordSignatureError,
    configured_public_key,
    verify_discord_signature,
)

logger = logging.getLogger("operator_etl_chat.discord.interactions")

router = APIRouter(tags=["discord"])

# Discord interaction types
_PING = 1
_APPLICATION_COMMAND = 2

# Per-user sliding window (in addition to graph-runner IP rate limit).
_USER_RATE_LIMIT = int(os.environ.get("OPERATOR_ETL_DISCORD_USER_RATE_LIMIT", "20"))
_user_hits: dict[str, list[float]] = {}


def _guild_allowlist() -> set[str]:
    raw = os.environ.get("OPERATOR_ETL_DISCORD_GUILD_ID", "").strip()
    return {g.strip() for g in raw.split(",") if g.strip()} if raw else set()


def _channel_allowlist() -> set[str]:
    raw = os.environ.get("OPERATOR_ETL_DISCORD_CHANNEL_ID", "").strip()
    return {c.strip() for c in raw.split(",") if c.strip()} if raw else set()


def _user_rate_ok(user_id: str) -> bool:
    now = time.monotonic()
    window = _user_hits.setdefault(user_id, [])
    window[:] = [t for t in window if now - t < 60.0]
    if len(window) >= _USER_RATE_LIMIT:
        return False
    window.append(now)
    return True


def _options_map(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Parse Discord application command name + options.

    Supports both top-level `/status` and nested `/etl status` (subcommand).
    """
    name = str(data.get("name") or "")
    options = data.get("options") or []
    opts: dict[str, Any] = {}

    # Subcommand group: /etl status → name=etl, options=[{name:status, options:[...]}]
    if options and isinstance(options[0], dict) and options[0].get("type") in (1, 2):
        sub = options[0]
        name = str(sub.get("name") or name)
        for opt in sub.get("options") or []:
            if isinstance(opt, dict) and "name" in opt:
                opts[str(opt["name"])] = opt.get("value")
        return name, opts

    for opt in options:
        if isinstance(opt, dict) and "name" in opt:
            opts[str(opt["name"])] = opt.get("value")
    return name, opts


def _guild_channel_allowed(payload: dict[str, Any]) -> bool:
    guilds = _guild_allowlist()
    channels = _channel_allowlist()
    guild_id = str(payload.get("guild_id") or "")
    channel_id = str(
        payload.get("channel_id") or (payload.get("channel") or {}).get("id") or ""
    )
    if guilds and guild_id not in guilds:
        return False
    if channels and channel_id not in channels:
        return False
    return True


@router.post("/discord/interactions")
async def discord_interactions(request: Request) -> Response:
    body = await request.body()
    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")

    try:
        public_key = configured_public_key()
        verify_discord_signature(
            public_key_hex=public_key,
            signature_hex=signature,
            timestamp=timestamp,
            body=body,
        )
    except DiscordSignatureError:
        logger.warning("discord_interactions_unauthorized")
        return Response(content="invalid request signature", status_code=401)

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return Response(content="bad request", status_code=400)

    if not isinstance(payload, dict):
        return Response(content="bad request", status_code=400)

    interaction_type = payload.get("type")
    if interaction_type == _PING:
        return JSONResponse({"type": 1})

    if interaction_type != _APPLICATION_COMMAND:
        return JSONResponse(
            {
                "type": 4,
                "data": {"content": "Unsupported interaction.", "flags": 64},
            }
        )

    if not _guild_channel_allowed(payload):
        return JSONResponse(
            {
                "type": 4,
                "data": {"content": "This guild/channel is not allowlisted.", "flags": 64},
            }
        )

    member = payload.get("member") or {}
    user = member.get("user") or payload.get("user") or {}
    user_id = str(user.get("id") or "unknown")
    if not _user_rate_ok(user_id):
        return JSONResponse(
            {
                "type": 4,
                "data": {"content": "Rate limit exceeded. Try again shortly.", "flags": 64},
            }
        )

    data = payload.get("data") or {}
    if not isinstance(data, dict):
        return JSONResponse(
            {
                "type": 4,
                "data": {"content": "Malformed command.", "flags": 64},
            }
        )

    cmd_name, options = _options_map(data)
    handler = DiscordCommandHandler()
    return JSONResponse(handler.handle_command(cmd_name, options))
