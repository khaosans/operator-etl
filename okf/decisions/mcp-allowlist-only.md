---
type: Decision
title: MCP allowlist only
description: Agents call typed tools — no raw SQL, no vault decrypt
tags: [mcp, security]
timestamp: 2026-08-17T00:00:00Z
---

# MCP allowlist only

**Decision:** All agent data access goes through MCP tools defined in [`sql/allowlist.yaml`](/sql/allowlist.yaml).

**Allowed tools:** `get_gold_metrics`, `run_quality_sql`, `get_run_status`.

**Denied patterns:** `vault_decrypt`, arbitrary SQL, bronze row reads via MCP.

**Errors:** Structured `TOOL_DENIED` JSON — never silent fallback.

**Local:** `uv run operator-etl-mcp` (stdio).

**GCP:** HTTP wrapper at `operator_etl_gcp/http/mcp_app.py`.
