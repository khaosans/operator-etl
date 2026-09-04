---
type: Decision
title: Chat adapter boundary
description: Discord/Slack chat is a Control-plane client — gold-read and bounded-run only; never publish or vault
tags: [security, chat, discord]
timestamp: 2026-09-04T00:00:00Z
---

# Chat adapter boundary

**Decision:** Chat platforms (Discord first; Slack later) are **thin Control-plane clients**. They may call allowlisted MCP tools and bounded graph runs. They must **never** become warehouse chatbots, vault clients, or auto-publish channels.

**Allowed:**

- HITL escalation alerts with sanitized metrics (`run_id`, status, row counts)
- Slash commands that map to `get_gold_metrics`, `get_run_status`, or fixed `public_comments` runs
- Ephemeral Discord replies

**Denied:**

- Raw SQL, bronze/silver rows, vault decrypt, insight/FOIA body text in chat
- Free-form natural-language warehouse exploration
- Auto-publishing redacted FOIA bundles or insights to channels ([agents-never-publish-prod](agents-never-publish-prod.md))
- Accepting `raw_records` or arbitrary pipeline params from chat users

**Security:**

- Discord Interactions: Ed25519 signature + timestamp skew check
- Guild/channel allowlists via env
- Secrets only in env / Secret Manager (`OPERATOR_ETL_DISCORD_*`)
- Fail-soft outbound webhooks (never fail the FOIA graph)

**Code:** `src/operator_etl_chat/` · Docs: [DISCORD.md](../../docs/DISCORD.md)
