---
type: Decision
title: PII fail-closed
description: Scan before insight; tokenize to vault; HITL on ambiguous matches
tags: [pii, foia, policy]
timestamp: 2026-08-17T00:00:00Z
---

# PII fail-closed

**Decision:** No raw PII in insight drafts, MCP responses, or LLM context.

**Flow:**

1. Scan `body` and `subject` for email, phone, SSN patterns
2. Tokenize matches into encrypted vault (`warehouse/pii_vault.json` — gitignored)
3. Flag `pii_detected=true` on silver rows for FOIA redaction queue
4. Ambiguous confidence → graph `needs_human` interrupt

**MCP:** Vault never exposed via tools.

**Optional upgrade:** Presidio analyzer (`uv sync --extra presidio`) — SPECIFIED as enhancement.
