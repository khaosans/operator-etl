# How Operator ETL works

End-to-end usage model for FOIA / public comment intake — local MVP and scaled GCP deployment.

**When to read:** You need the runtime flow, three planes, lifecycle, or MCP policy. If you do not know what medallion means: [PATTERNS.md](PATTERNS.md).

**See it work:** [TOUR.md](TOUR.md) · [WALKTHROUGH.md](WALKTHROUGH.md) · **Scale out:** [SCALING.md](SCALING.md) · **Start here:** [README.md](../README.md)

---

## Who uses it

Named composites: [PERSONAS.md](PERSONAS.md).

| Role | What they do | Entry point |
|---|---|---|
| **FOIA officer (Priya)** | Review PII flags, quarantine, critic-checked insight | Dashboard Gov tab |
| **Data engineer (Riley)** | Add sources, run pipelines, optional local Ollama | [GETTING-STARTED.md](GETTING-STARTED.md), [LLM.md](LLM.md), [MODELS.md](MODELS.md) |
| **New engineer (Sam)** | Prove the clone | `./scripts/verify.sh` |
| **Reviewer (Jordan)** | Honest scope | [FINAL-REVIEW.md](FINAL-REVIEW.md) |
| **AI agent (MCP)** | Query gold KPIs, allowlisted SQL | `operator-etl-mcp` |

---

## Three planes

Agents orchestrate. Python and SQL execute. PII never reaches unconstrained tools.

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
    Silver[silver_comments]
    Gold[gold marts]
    Quarantine[quarantine_comments]
  end

  Graph -->|"MCP allowlist"| Gold
  Bronze --> PII
  PII --> Silver
  PII --> Quarantine
  Silver --> Gold
  Graph --> Critic
  Critic --> persist[persist insight]
```

Details: [okf/models/three-planes.md](../okf/models/three-planes.md)

---

## FOIA comment lifecycle

```mermaid
flowchart TB
  subgraph intake [Intake]
    CSV[samples/public_comments.csv]
    GCS[GCS inbox at scale]
  end

  subgraph dataPlane [Data plane]
    Bronze[bronze_raw]
    Silver[silver_comments]
    Quarantine[quarantine_comments]
    Gold[gold SQL marts]
  end

  subgraph policyPlane [Policy plane]
    PIIGate[PII scan + vault]
  end

  subgraph controlPlane [Control plane]
    Quality[quality agent]
    Insight[insight draft]
    Critic[critic]
  end

  subgraph human [Human review]
    Officer[FOIA officer]
  end

  CSV --> ingest[ingest]
  GCS --> ingest
  ingest --> Bronze
  Bronze --> PIIGate
  PIIGate --> Silver
  PIIGate --> Quarantine
  Silver --> Gold
  Gold --> Quality
  Quality --> Insight
  Insight --> Critic
  Critic --> persist[persist]
  persist --> Officer
```

Agency mapping: [FOIA-Public-Comments-Guide.md](FOIA-Public-Comments-Guide.md)

---

## What runs where

| Component | Local MVP | GCP (scaled) | Enterprise Invariant |
|---|---|---|---|
| **Trigger** | `make e2e` / `etl-graph` CLI | GCS upload → Pub/Sub → Cloud Run | At-least-once event delivery |
| **Warehouse** | DuckDB (`warehouse/operator.duckdb`) | BigQuery (`etl_*` datasets) | Bit-identical SQL aggregation |
| **Graph runner** | `operator_etl_graph` on laptop | Cloud Run `graph-runner` | Deterministic LangGraph state machine |
| **Checkpoints** | SQLite | Cloud SQL PostgreSQL | Resumable HITL interruption |
| **MCP** | stdio (`operator-etl-mcp`) | HTTP/SSE on Cloud Run | Strict query allowlist enforcement |
| **PII vault** | Local encrypted file | Secret Manager + Cloud KMS | Zero raw PII in model context |

Same graph nodes, PII policy, critic, and MCP allowlist in both environments.

---

## Real-world Production Deployment Blueprint

When graduating from local development to production agency infrastructure:

```mermaid
flowchart TD
    subgraph Intake [1. Event Ingestion]
        GCS["Inbound GCS Bucket<br/>gs://agency-intake-drop/"] -->|"Object Finalize"| PS["Pub/Sub Topic"]
    end

    subgraph Compute [2. Containerized Orchestration]
        PS -->|"Push Subscription"| CR["Cloud Run: Graph Runner<br/>(operator-etl container)"]
        SM["Cloud Secret Manager<br/>(PII AES Key + API Tokens)"] -.->|Injected| CR
        SQL["Cloud SQL Postgres<br/>(LangGraph Checkpointer)"] <--> CR
    end

    subgraph Storage [3. Medallion Lakehouse]
        CR --> BQ_B["BigQuery: etl_bronze<br/>(Raw Immutable Payloads)"]
        CR --> BQ_S["BigQuery: etl_silver<br/>(Validated Entities)"]
        CR --> BQ_Q["BigQuery: etl_quarantine<br/>(Audit Dead-Letter)"]
        CR --> BQ_G["BigQuery: etl_gold<br/>(Audited KPI Marts)"]
    end

    subgraph Governance [4. Output & HITL Sign-off]
        BQ_G --> MCP["Cloud Run MCP Server<br/>(SSE Transport)"]
        MCP --> Agent["Analytical Agent<br/>(Briefing Generator)"]
        Agent --> Critic["Critic Node"]
        Critic --> Persist["Persist Verified Memo"]
        Critic -->|"Violation"| Officer["FOIA Officer Review Dashboard"]
    end
```

---

## What agents may and may not do

**Allowed (MCP tools):**

- `get_gold_metrics` — aggregate KPIs only
- `run_quality_sql` — allowlisted query IDs only
- `get_run_status` — audit row for a run

**Denied:**

- Raw SQL on bronze/silver
- `vault_decrypt` or row-level PII export
- Auto-publish to external systems

Policy: [okf/decisions/mcp-allowlist-only.md](../okf/decisions/mcp-allowlist-only.md)

```mermaid
flowchart LR
  Agent[AI agent] --> MCP[operator-etl-mcp]
  MCP --> Allow[get_gold_metrics<br/>run_quality_sql<br/>get_run_status]
  MCP -.->|blocked| Deny[vault_decrypt<br/>raw SQL<br/>auto-publish]
```

---

## Why this design

Operator ETL separates **deterministic ETL** (medallion warehouse, SQL marts) from **bounded agents** (LangGraph orchestration, MCP allowlist). PII never reaches unconstrained tools; the critic rejects insight numbers that do not exist in gold.

```mermaid
flowchart LR
  Draft[insight draft] --> Critic{critic}
  Gold[(gold marts)] --> Critic
  Critic -->|numbers match| OK[persist]
  Critic -->|999 not in gold| HITL[retry or needs_human]
```

Each invariant maps to an authoritative source and a pytest — see [FOUNDATIONS.md](FOUNDATIONS.md).

---

## Proof before trust

Before claiming the system works or scaling to staging:

```bash
make e2e
```

This runs OKF validation, 51 pytest tests, and a fresh-warehouse FOIA demo with output assertions.

**CI:** Every push to `master` runs the same gate on GitHub Actions — see the CI badge in [README.md](../README.md).

Step-by-step: [WALKTHROUGH.md](WALKTHROUGH.md)

## See also

- [CONCEPTS.md](CONCEPTS.md) — what we built
- [APPLY.md](APPLY.md) — other data sources
- [RISKS.md](RISKS.md) — residual risks
- [FOUNDATIONS.md](FOUNDATIONS.md) — why this design; proof matrix
- [GETTING-STARTED.md](GETTING-STARTED.md) — install and env vars
- [FINAL-REVIEW.md](FINAL-REVIEW.md) — proven vs specified audit
