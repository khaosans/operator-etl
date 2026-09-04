# Discord chat adapter

**When to read:** You want HITL escalation alerts or ops slash commands in Discord without widening MCP/A2A privileges.

Policy: [chat-adapter-boundary](https://github.com/khaosans/operator-etl/blob/master/okf/decisions/chat-adapter-boundary.md) · Security: [SECURITY-HARDENING.md](SECURITY-HARDENING.md)

Discord is a **Control-plane client** — same boundary as Cursor MCP + A2A. It is **not** chat-with-the-warehouse.

---

## What it does

| Mode | Behavior |
|---|---|
| **HITL alerts** | When a FOIA graph run reaches `needs_human`, post a sanitized metric summary to an Incoming Webhook |
| **Ops commands** | `/etl status`, `/etl kpis`, `/etl run` via Interactions endpoint on the graph-runner |

Replies never include vault contents, comment bodies, insight drafts, or bronze/silver rows.

---

## Environment variables

Never commit these. Put them in `.env` or Secret Manager.

| Variable | Required for | Purpose |
|---|---|---|
| `OPERATOR_ETL_DISCORD_WEBHOOK_URL` | Alerts | Incoming Webhook URL (`https://discord.com/api/webhooks/...`) |
| `OPERATOR_ETL_DISCORD_PUBLIC_KEY` | Commands | Application **Public Key** (hex) for Ed25519 verify |
| `OPERATOR_ETL_DISCORD_GUILD_ID` | Commands (recommended) | Allowlisted guild id(s), comma-separated |
| `OPERATOR_ETL_DISCORD_CHANNEL_ID` | Commands (optional) | Allowlisted channel id(s) |
| `OPERATOR_ETL_DISCORD_BOT_TOKEN` | Register commands only | Bot token for `scripts/discord_register_commands.py` |
| `OPERATOR_ETL_DISCORD_APPLICATION_ID` | Register commands only | Application id |
| `OPERATOR_ETL_DISCORD_USER_RATE_LIMIT` | Commands | Per-user commands / minute (default `20`) |

If the webhook URL is unset, HITL alerts are a no-op (safe for local CI).

---

## Setup

1. Create a Discord **Application** → Bot → copy **Public Key**.
2. Create an **Incoming Webhook** on the officer channel → set `OPERATOR_ETL_DISCORD_WEBHOOK_URL`.
3. Run the graph-runner (`uv run operator-etl-gcp` or Docker on `:8080`).
4. Set Interactions Endpoint URL to `https://<your-host>/discord/interactions`.
5. Register slash commands:

```bash
export OPERATOR_ETL_DISCORD_BOT_TOKEN=...
export OPERATOR_ETL_DISCORD_APPLICATION_ID=...
export OPERATOR_ETL_DISCORD_GUILD_ID=...   # optional; faster guild scope
uv run python scripts/discord_register_commands.py
```

6. Invite the bot to the allowlisted guild with `applications.commands` scope.

---

## Slash commands

| Command | Backend | Notes |
|---|---|---|
| `/etl status run_id:<uuid>` | MCP `get_run_status` | Ephemeral; errors redacted to `see_dashboard` |
| `/etl kpis [domain]` | MCP `get_gold_metrics` | `gov` (default) or `orders` |
| `/etl run [source]` | Bounded `run_graph` | Only `public_comments`; no free-form records |

---

## Security checklist

- [ ] Public key verify rejects unsigned / skewed requests (`401`)
- [ ] Guild/channel allowlist configured in production
- [ ] Webhook URL host is `discord.com` / `discordapp.com` only
- [ ] No FOIA publish from Discord (officer still uses dashboard)
- [ ] Secrets not in git, Terraform placeholders, or docs examples

Agent checklist: [skills/operator-security](https://github.com/khaosans/operator-etl/blob/master/skills/operator-security/SKILL.md) · [skills/operator-chat](https://github.com/khaosans/operator-etl/blob/master/skills/operator-chat/SKILL.md)
