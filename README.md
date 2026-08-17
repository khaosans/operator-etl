# Operator ETL

**Agentic data intake for FOIA and public comments** — deterministic medallion warehouse, LangGraph orchestration, MCP tool surface, PII policy plane.

Built for government agencies and regulated bodies that must intake public comments, detect PII before release, quarantine bad rows, and produce **defensible insights** (every number verified against the warehouse).

## Quick start

```bash
uv sync --extra dev
uv run etl-graph --source public_comments --pipeline public_comments
uv run pytest
```

## Architecture

| Plane | Package | Status |
|---|---|---|
| **Data** | `operator_etl/` | IMPLEMENTED — bronze/silver/gold, quarantine, CLI |
| **Control** | `operator_etl_graph/` | IMPLEMENTED — LangGraph, critic, checkpoints |
| **Policy** | `operator_etl_policy/` | IMPLEMENTED — PII scan, vault, budgets |
| **MCP** | `operator_etl_mcp/` | IMPLEMENTED — allowlisted tools for agents |

```
CSV / portal export  →  bronze  →  PII gate  →  silver / quarantine
                                              →  gold SQL  →  insight  →  critic  →  persist
```

## Use cases

- **Public comment periods** — EPA/FCC-style docket comments with PII redaction queue
- **FOIA request logs** — structured intake with audit trail
- **Commerce orders** — original demo domain (`etl run --source demo`)

## Documentation

| Doc | Description |
|---|---|
| [`docs/FOIA-Public-Comments-Guide.md`](docs/FOIA-Public-Comments-Guide.md) | Agency workflow, data model, how to run |
| [`docs/Operator-ETL-White-Paper.md`](docs/Operator-ETL-White-Paper.md) | Full engineering spec, GCP, ADRs, NFRs |
| [`docs/Operator-ETL-White-Paper.pdf`](docs/Operator-ETL-White-Paper.pdf) | PDF version |

## Commands

| Command | Action |
|---|---|
| `uv run etl-graph` | Full agentic FOIA/public comments pipeline |
| `uv run etl run --source demo` | Orders demo (deterministic only) |
| `uv run operator-etl-mcp` | MCP server for Cursor agents |
| `uv run pytest` | 17 tests — PII, critic, graph, idempotency |

## Project layout

```
src/
  operator_etl/           # Data plane
  operator_etl_graph/     # LangGraph control plane
  operator_etl_policy/    # PII + budgets
  operator_etl_mcp/       # MCP tools
pipelines/
  public_comments.yaml    # FOIA / gov domain
  demo.yaml               # Orders demo
samples/
  public_comments.csv     # 12-row gov sample (10 silver, 2 quarantine)
sql/marts/gov/            # Gold marts for comments
sql/allowlist.yaml        # MCP SQL whitelist
evals/                    # Golden eval definitions
docs/                     # White paper + FOIA guide
```

## Agentic AI best practices implemented

- **Agents orchestrate; ETL executes** — no unconstrained SQL
- **MCP allowlist** — typed tools, structured `TOOL_DENIED` errors
- **PII fail-closed** — scan before insight; vault never exposed via MCP
- **Critic node** — faithfulness check on every numeric claim
- **LangGraph checkpoints** — resumable runs (`warehouse/checkpoints.db`)
- **Quality gate** — KPIs withheld when quarantine rate exceeds threshold
- **Eval suite** — PII leak, critic, graph E2E, idempotency

## License

Private — government / operator use. See repository settings.
