---
type: OperatingModel
title: Three planes architecture
description: Data, Policy, and Control — agents orchestrate; ETL executes
tags: [architecture, langgraph, mcp]
timestamp: 2026-08-17T00:00:00Z
---

# Three planes

**Rule:** LLMs decide *whether* to phrase an insight. Python and SQL decide *what data exists*.

```mermaid
flowchart TB
  subgraph control [Control plane]
    Graph[LangGraph pipeline]
    Critic[critic node]
    Checkpoints[checkpoints]
  end

  subgraph policy [Policy plane]
    PII[PII scan]
    Vault[encrypted vault]
    Budgets[run budgets]
  end

  subgraph data [Data plane]
    Bronze[bronze_raw]
    Silver[silver validated]
    Gold[gold marts]
    Quarantine[quarantine]
  end

  Graph -->|"MCP allowlist"| Gold
  Bronze --> PII
  PII --> Silver
  PII --> Quarantine
  Silver --> Gold
  Graph --> Critic
```

Usage narrative: [docs/HOW-IT-WORKS.md](../../docs/HOW-IT-WORKS.md)

| Plane | Package | MCP access |
|---|---|---|
| Control | `operator_etl_graph/` | Orchestrates nodes |
| Policy | `operator_etl_policy/` | Never exposed via MCP |
| Data | `operator_etl/` | Via allowlisted tools only |

See [implementation status](/models/implementation-status.md) for what is coded vs specified.
