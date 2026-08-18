---
name: operator-run
description: >-
  Run Operator ETL locally — MVP demo, pytest, FOIA graph pipeline, Streamlit dashboard.
  Use when proving the system works or demoing to reviewers.
---

# Run Operator ETL locally

**Load:** [okf/index.md](../../okf/index.md) → [run-local-mvp.md](../../okf/playbooks/run-local-mvp.md)

## MVP proof (required before share claims)

```bash
./harness/e2e.sh
```

## Quick demo

```bash
./scripts/demo_mvp.sh
```

## Commands

| Command | Purpose |
|---|---|
| `uv run etl-graph --source public_comments` | Full FOIA agentic pipeline |
| `uv run etl run --source demo` | Orders ETL (interviews) |
| `uv run pytest -q` | 51 tests |
| `uv run etl dashboard` | Streamlit — Gov + Orders tabs |

## Fresh warehouse for demos

```bash
OPERATOR_ETL_WAREHOUSE=.tmp/mvp-demo/operator.duckdb \
OPERATOR_ETL_PIPELINE_NAME=public_comments \
OPERATOR_ETL_DOMAIN=gov \
uv run etl-graph
```

## Expected FOIA numbers

See [mvp-demo.md](../../okf/models/mvp-demo.md): 12 → 10 silver, 2 quarantine, critic pass.
