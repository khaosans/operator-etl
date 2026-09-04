#!/usr/bin/env python3
"""Register Discord application slash commands for Operator ETL.

Requires env:
  OPERATOR_ETL_DISCORD_BOT_TOKEN
  OPERATOR_ETL_DISCORD_APPLICATION_ID
Optional:
  OPERATOR_ETL_DISCORD_GUILD_ID  — register guild-scoped (faster) vs global

Usage (docs only; never commit tokens):
  uv run python scripts/discord_register_commands.py
"""

from __future__ import annotations

import json
import os
import sys

import httpx

COMMANDS = [
    {
        "name": "etl",
        "description": "Operator ETL ops (gold KPIs / status / bounded run)",
        "options": [
            {
                "type": 1,
                "name": "status",
                "description": "Get pipeline run status by run_id",
                "options": [
                    {
                        "type": 3,
                        "name": "run_id",
                        "description": "Pipeline run UUID",
                        "required": True,
                    }
                ],
            },
            {
                "type": 1,
                "name": "kpis",
                "description": "Get gold KPI aggregates",
                "options": [
                    {
                        "type": 3,
                        "name": "domain",
                        "description": "gov or orders",
                        "required": False,
                    }
                ],
            },
            {
                "type": 1,
                "name": "run",
                "description": "Trigger a bounded public_comments graph run",
                "options": [
                    {
                        "type": 3,
                        "name": "source",
                        "description": "Only public_comments is allowed",
                        "required": False,
                    }
                ],
            },
        ],
    }
]


def main() -> int:
    token = os.environ.get("OPERATOR_ETL_DISCORD_BOT_TOKEN", "").strip()
    app_id = os.environ.get("OPERATOR_ETL_DISCORD_APPLICATION_ID", "").strip()
    guild_id = os.environ.get("OPERATOR_ETL_DISCORD_GUILD_ID", "").strip()
    if not token or not app_id:
        print(
            "Set OPERATOR_ETL_DISCORD_BOT_TOKEN and OPERATOR_ETL_DISCORD_APPLICATION_ID",
            file=sys.stderr,
        )
        return 1
    if guild_id:
        url = f"https://discord.com/api/v10/applications/{app_id}/guilds/{guild_id}/commands"
    else:
        url = f"https://discord.com/api/v10/applications/{app_id}/commands"
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    with httpx.Client(timeout=30.0) as client:
        response = client.put(url, headers=headers, content=json.dumps(COMMANDS))
    print(f"status={response.status_code}")
    print(response.text[:2000])
    return 0 if response.status_code < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
