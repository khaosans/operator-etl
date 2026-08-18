# CLI and Make targets

**When to read:** After [QUICKSTART](QUICKSTART.md) — you want to run pipelines by hand. Env vars: [GETTING-STARTED](GETTING-STARTED.md#environment-variables).

All commands assume the repo root and `uv sync --extra dev` (or a green `./scripts/verify.sh`).

---

## Make (preferred shortcuts)

| Target | What it runs |
|---|---|
| `make verify` | `scripts/verify.sh` — uv bootstrap + full proof gate |
| `make e2e` | `harness/e2e.sh` — OKF + pytest + FOIA demo |
| `make demo` | FOIA demo only (`scripts/demo_mvp.sh`) |
| `make test` | `uv run pytest -q` (41 tests) |
| `make walkthrough` | Demo + warehouse inspection |
| `make okf` | Strict OKF validate |
| `make share` | e2e then regenerate PDFs |
| `make docker-build` | Local image `operator-etl:local` |
| `make help` | Print this list |

---

## `etl` — data plane (orders / generic)

Entry: `uv run etl` · source: [`src/operator_etl/cli.py`](https://github.com/khaosans/operator-etl/blob/master/src/operator_etl/cli.py)

Default source is **`demo`** (orders CSV). Pipeline YAML: [`pipelines/demo.yaml`](https://github.com/khaosans/operator-etl/blob/master/pipelines/demo.yaml).

| Command | Purpose |
|---|---|
| `uv run etl sources` | List registered source names |
| `uv run etl ingest -s demo` | Bronze only; same file hash skipped |
| `uv run etl run -s demo` | Ingest → silver/quarantine → gold → print insights |
| `uv run etl run -s http` | HTTP/file JSON source (`samples/http_orders.json`) |
| `uv run etl insight` | Print gold KPIs if quality gate passes |
| `uv run etl dashboard` | Streamlit on the current warehouse |

Expected orders demo: 21 rows in → 17 silver, 4 quarantined.

---

## `etl-graph` — FOIA control plane

Entry: `uv run etl-graph` · source: [`src/operator_etl_graph/cli.py`](https://github.com/khaosans/operator-etl/blob/master/src/operator_etl_graph/cli.py)

Forces **gov** domain. Use a **fresh warehouse** to avoid stale counts:

```bash
OPERATOR_ETL_WAREHOUSE=.tmp/mvp-demo/operator.duckdb \
OPERATOR_ETL_PIPELINE_NAME=public_comments \
OPERATOR_ETL_DOMAIN=gov \
uv run etl-graph --source public_comments --pipeline public_comments
```

| Flag | Default | Meaning |
|---|---|---|
| `-s` / `--source` | `public_comments` | Source key in the pipeline YAML |
| `-p` / `--pipeline` | `public_comments` | YAML name under `pipelines/` |

Prints `status=`, `silver=`, `quarantined=`, optional `pii_findings=`, then the insight draft.

---

## `operator-etl-mcp`

```bash
uv run operator-etl-mcp
```

stdio MCP server for Cursor. Tools and policy: [MCP.md](MCP.md).

---

## Environment cheat sheet

Prefix **`OPERATOR_ETL_`**. Copy [`.env.example`](https://github.com/khaosans/operator-etl/blob/master/.env.example) for local DuckDB.

| Variable | Typical local value |
|---|---|
| `OPERATOR_ETL_WAREHOUSE` | `warehouse/operator.duckdb` or `.tmp/mvp-demo/operator.duckdb` |
| `OPERATOR_ETL_PIPELINE_NAME` | `demo` or `public_comments` |
| `OPERATOR_ETL_DOMAIN` | `orders` or `gov` |
| `OPERATOR_ETL_BACKEND` | `duckdb` (default) |
| `OPERATOR_ETL_INSIGHT_BACKEND` | `template` (default) or `llm` — [LLM.md](LLM.md) |
| `OPERATOR_ETL_ORDERS_WAREHOUSE` | Orders tab path (default `warehouse/operator.duckdb`) |

Gov env vars leak into pytest if you export them in the same shell — use `make e2e` or a clean terminal. [TROUBLESHOOTING](TROUBLESHOOTING.md).

---

## See also

- [DASHBOARD.md](DASHBOARD.md)
- [ADD-A-SOURCE.md](ADD-A-SOURCE.md)
- [WALKTHROUGH.md](WALKTHROUGH.md)
