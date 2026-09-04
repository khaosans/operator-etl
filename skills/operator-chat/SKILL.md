---
name: operator-chat
description: >-
  Discord (and future Slack) chat adapter for Operator ETL — HITL alerts and
  allowlisted ops commands. Use when wiring Discord webhooks, Interactions, or
  reviewing chat security boundaries.
---

# Chat adapter — Operator ETL

**Load:** [chat-adapter-boundary.md](../../okf/decisions/chat-adapter-boundary.md) · [DISCORD.md](../../docs/DISCORD.md) · [operator-security](../operator-security/SKILL.md)

## Rules

1. Chat is a **Control-plane client** — call MCP tools or bounded `/run` only.
2. Never put vault, PII, bronze/silver, or insight text in Discord payloads.
3. Never auto-publish FOIA releases to channels.
4. Discord Interactions must verify Ed25519 signatures before handling commands.
5. HITL notifier is env-gated and fail-soft.

## Verify after changes

```bash
uv run pytest -q tests/test_discord_verify.py tests/test_discord_notify.py tests/test_discord_commands.py
./scripts/verify.sh
```
