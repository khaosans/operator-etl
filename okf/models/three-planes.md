---
type: OperatingModel
title: Three planes architecture
description: Data, Policy, and Control — agents orchestrate; ETL executes
tags: [architecture, langgraph, mcp]
timestamp: 2026-08-17T00:00:00Z
---

# Three planes

```
CONTROL  — LangGraph graph, checkpoints, critic, HITL interrupts
POLICY   — PII scan, token vault, run budgets, trace redaction
DATA     — Deterministic bronze → silver → gold ETL
```

**Rule:** LLMs decide *whether* to phrase an insight. Python and SQL decide *what data exists*.

| Plane | Package | MCP access |
|---|---|---|
| Control | `operator_etl_graph/` | Orchestrates nodes |
| Policy | `operator_etl_policy/` | Never exposed via MCP |
| Data | `operator_etl/` | Via allowlisted tools only |

See [implementation status](/models/implementation-status.md) for what is coded vs specified.
