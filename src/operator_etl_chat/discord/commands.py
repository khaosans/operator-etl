"""Slash-command → MCP / bounded graph-run mapping."""

from __future__ import annotations

import logging
from typing import Any

from operator_etl.config import Settings, get_settings
from operator_etl.load.connection import connect
from operator_etl_chat.sanitize import (
    format_dict_discord_content,
    sanitize_hitl_payload,
    sanitize_kpis,
    sanitize_run_status,
)
from operator_etl_graph.graph import run_graph
from operator_etl_mcp.tools import get_gold_metrics, get_run_status

logger = logging.getLogger("operator_etl_chat.discord.commands")

# Fixed demo/public_comments params only — no free-form records from Discord.
_ALLOWED_RUN_SOURCES = frozenset({"public_comments"})
_ALLOWED_DOMAINS = frozenset({"gov", "orders"})


class DiscordCommandHandler:
    """ChatCommandHandler for /etl status|kpis|run."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings

    def handle_command(self, name: str, options: dict[str, Any]) -> dict[str, Any]:
        """Return Discord interaction callback payload (type 4 channel message)."""
        try:
            if name == "status":
                text = self._cmd_status(options)
            elif name == "kpis":
                text = self._cmd_kpis(options)
            elif name == "run":
                text = self._cmd_run(options)
            else:
                text = "Unknown command. Use `/etl status`, `/etl kpis`, or `/etl run`."
        except Exception as exc:
            logger.warning("discord_command_failed: %s: %s", type(exc).__name__, exc)
            text = "Command failed. Check Operator ETL logs / dashboard."
        return {
            "type": 4,  # CHANNEL_MESSAGE_WITH_SOURCE
            "data": {
                "content": text[:1900],
                "flags": 64,  # EPHEMERAL
            },
        }

    def _settings_or_default(self) -> Settings:
        return self._settings or get_settings()

    def _cmd_status(self, options: dict[str, Any]) -> str:
        run_id = str(options.get("run_id", "")).strip()
        if not run_id or len(run_id) > 128:
            return "Provide a valid `run_id` (max 128 chars)."
        settings = self._settings_or_default()
        con = connect(settings)
        try:
            raw = get_run_status(con, run_id)
        finally:
            con.close()
        if raw.get("error") == "NOT_FOUND":
            return f"Run `{run_id}` not found."
        clean = sanitize_run_status(raw)
        return format_dict_discord_content("Run status", clean)

    def _cmd_kpis(self, options: dict[str, Any]) -> str:
        domain = str(options.get("domain", "gov")).strip().lower() or "gov"
        if domain not in _ALLOWED_DOMAINS:
            return "Domain must be `gov` or `orders`."
        settings = self._settings_or_default()
        con = connect(settings)
        try:
            raw = get_gold_metrics(con, domain=domain)
        finally:
            con.close()
        clean = sanitize_kpis(raw)
        return format_dict_discord_content(f"Gold KPIs ({domain})", clean)

    def _cmd_run(self, options: dict[str, Any]) -> str:
        source = str(options.get("source", "public_comments")).strip() or "public_comments"
        if source not in _ALLOWED_RUN_SOURCES:
            return "Only `source=public_comments` is allowed from Discord."
        # Ignore any unexpected keys that could smuggle raw_records.
        settings = self._settings_or_default()
        result = run_graph(source=source, settings=settings)
        summary = {
            "run_id": result.get("run_id"),
            "status": result.get("status"),
            "rows_silver": result.get("rows_silver"),
            "rows_quarantined": result.get("rows_quarantined"),
            "critic_passed": result.get("critic_passed"),
        }
        # Never echo insight_draft / artifacts to Discord.
        clean = sanitize_hitl_payload(
            {
                **summary,
                "pipeline": settings.pipeline_name,
                "message": "Bounded run accepted from Discord. Review dashboard before publish.",
            }
        )
        return format_dict_discord_content("Run result", clean)
