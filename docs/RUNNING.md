# Run the services locally

Every runnable entry point in Operator ETL, the command that starts it, and how to prove it works. Run [`./scripts/verify.sh`](QUICKSTART.md) once first so dependencies are synced and the proof gate is green.

FastAPI, uvicorn, and the OpenTelemetry SDK are core dependencies as of `0.5.1`, so the HTTP graph-runner, A2A task surface, and MCP HTTP wrapper all run with the default `dev` sync — no extra needed.

---

## Entry points

Console scripts are declared in [`pyproject.toml`](../pyproject.toml) (`[project.scripts]`).

| Entry point | Command | What it is | Needs |
|---|---|---|---|
| CLI (orders) | `uv run etl` | Ingest → silver/quarantine → gold → insights | dev |
| CLI (FOIA graph) | `uv run etl-graph` | Agentic FOIA / public-comments LangGraph pipeline | dev |
| Dashboard | `uv run streamlit run dashboard/app.py` | Streamlit Gov / FOIA, Orders, and Observability tabs | dev |
| HTTP graph-runner (**main**) | `uv run operator-etl-gcp` | FastAPI service on `:8080` — `/health`, `/run`, `/pubsub/push`, A2A, and Discord Interactions | dev |
| MCP over HTTP | `uv run uvicorn operator_etl_gcp.http.mcp_app:app` | FastAPI wrapper over the gold-KPI tools | dev |
| MCP over stdio | `uv run operator-etl-mcp` | Allowlisted stdio MCP tools for local agents | dev — see caveat |

---

## FOIA graph pipeline (CLI)

```bash
OPERATOR_ETL_WAREHOUSE=.tmp/mvp-demo/operator.duckdb \
OPERATOR_ETL_PIPELINE_NAME=public_comments \
OPERATOR_ETL_DOMAIN=gov \
uv run etl-graph --source public_comments --pipeline public_comments
```

Expect `status=complete`, `rows_in=12`, `silver=10`, `quarantined=2`, `critic_passed=True` on a fresh warehouse. This is the same run the proof gate asserts ([scripts/demo_mvp.sh](../scripts/demo_mvp.sh)). Re-running against the same warehouse ingests `0` rows (same-hash idempotency) and still reports `complete`.

## Dashboard

```bash
./scripts/demo_mvp.sh   # seeds .tmp/mvp-demo/operator.duckdb
OPERATOR_ETL_WAREHOUSE=.tmp/mvp-demo/operator.duckdb \
OPERATOR_ETL_PIPELINE_NAME=public_comments \
OPERATOR_ETL_DOMAIN=gov \
uv run streamlit run dashboard/app.py
```

Open the **Gov / FOIA** tab (Gate=PASS, silver=10, quarantined=2, PII rate 40%) and the **Observability & Spans** tab ([OBSERVABILITY.md](OBSERVABILITY.md)). In a Cursor Cloud Agent the dashboard is already served on `:8501` — see [CLOUD-AGENT.md](CLOUD-AGENT.md). Tab reference: [DASHBOARD.md](DASHBOARD.md).

## HTTP graph-runner (main)

The Cloud Run entry point ([src/operator_etl_gcp/http/app.py](../src/operator_etl_gcp/http/app.py)) also runs locally:

```bash
OPERATOR_ETL_WAREHOUSE=.tmp/main-demo/operator.duckdb \
OPERATOR_ETL_PIPELINE_NAME=public_comments \
OPERATOR_ETL_DOMAIN=gov \
uv run operator-etl-gcp        # uvicorn on 0.0.0.0:8080
```

Exercise it:

```bash
curl -s localhost:8080/health
# {"status":"ok","service":"graph-runner"}

curl -s -X POST localhost:8080/run \
  -H 'Content-Type: application/json' \
  -d '{"source":"public_comments","pipeline":"public_comments"}'
# {"run_id":"...","status":"complete","rows_in":12,"rows_silver":10,
#  "rows_quarantined":2,"critic_passed":true,"insight_draft":"...","errors":[]}
```

`/pubsub/push` decodes a Pub/Sub push envelope (GCS `OBJECT_FINALIZE`) and runs the graph on the staged object. Production blueprint: [HOW-IT-WORKS.md](HOW-IT-WORKS.md).

### Rate limit and body size

All routes except `/health` share an in-process per-client sliding window (default **60** requests per minute). Tune with `RATE_LIMIT_PER_MINUTE`. Excess requests return **429**. POST bodies over **10 MB** return **413**. A2A `raw_records` is also capped at 10,000 items.

```bash
# After ~60 POSTs in a minute from the same client:
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8080/run \
  -H 'Content-Type: application/json' \
  -d '{"source":"public_comments","pipeline":"public_comments"}'
# 429
```

This limiter is **one process**. Multi-instance Cloud Run needs Cloud Armor or an API gateway. Full control list: [SECURITY-HARDENING.md](SECURITY-HARDENING.md).

## A2A task surface

The same `operator-etl-gcp` service exposes the bounded agent-to-agent surface ([A2A.md](A2A.md)). Every A2A route requires a bearer token. Set one on the server and reuse it from the client via an env var (never hard-code a token):

```bash
export A2A_TOKEN="$(openssl rand -hex 16)"   # any non-empty value
OPERATOR_ETL_A2A_BEARER_TOKEN="$A2A_TOKEN" \
OPERATOR_ETL_WAREHOUSE=.tmp/main-demo/operator.duckdb \
uv run operator-etl-gcp
```

```bash
# No token -> 401
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8080/a2a/v1/tasks \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":"1","method":"tasks.create","params":{"source_type":"public_comments","docket_id":"EPA-HQ-OAR-2026-001","raw_records":[]}}'

# Create a task (token supplied from the env var above)
curl -s -X POST localhost:8080/a2a/v1/tasks \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $A2A_TOKEN" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tasks.create","params":{"source_type":"public_comments","docket_id":"EPA-HQ-OAR-2026-001","raw_records":[{"comment_id":"CMT-9001","docket_id":"EPA-HQ-OAR-2026-001","agency":"EPA","submitted_at":"2026-09-01T12:00:00","commenter_type":"individual","subject":"Support","body":"Please redact my email.","pii_detected":true}]}}'
# {"jsonrpc":"2.0","id":"1","result":{"task_id":"...","run_id":"...","state":"accepted"}}
```

`tasks.get_status` returns sanitized artifacts only (gold metrics, public brief, critic outcome, row counts) — no raw records or PII. Stream lifecycle events over SSE at `GET /a2a/v1/tasks/{task_id}/events`. Full contract and security boundary: [A2A.md](A2A.md).

## Discord Interactions

Same graph-runner hosts `POST /discord/interactions` (Ed25519-verified). HITL alerts use an Incoming Webhook when `OPERATOR_ETL_DISCORD_WEBHOOK_URL` is set. Setup and command list: [DISCORD.md](DISCORD.md).

## MCP tools

- **HTTP** — `uv run uvicorn operator_etl_gcp.http.mcp_app:app --port 8090`, then `GET /tools/gold_metrics?domain=gov`.
- **stdio** — `uv run operator-etl-mcp` speaks MCP over stdio for local agents. Configure with [.cursor/mcp.json.example](../.cursor/mcp.json.example). Tool reference: [MCP.md](MCP.md).

!!! warning "stdio MCP requires the mcp 1.x API"
    [src/operator_etl_mcp/server.py](../src/operator_etl_mcp/server.py) uses the `@server.list_tools()` / `@server.call_tool()` decorator API. If the resolved `mcp` package is 2.x, importing the stdio server fails with `'Server' object has no attribute 'list_tools'`. The tool functions in `operator_etl_mcp.tools` (and the HTTP MCP wrapper) are unaffected and stay covered by `tests/test_mcp_tools.py`. Pin `mcp` to a 1.x release to run the stdio server.

---

## See also

- [QUICKSTART.md](QUICKSTART.md) — one-command verify
- [CLI.md](CLI.md) · [DASHBOARD.md](DASHBOARD.md) · [MCP.md](MCP.md) · [A2A.md](A2A.md) · [DISCORD.md](DISCORD.md) · [OBSERVABILITY.md](OBSERVABILITY.md)
- [CLOUD-AGENT.md](CLOUD-AGENT.md) — the same services, auto-started in Cursor Cloud
- [HOW-IT-WORKS.md](HOW-IT-WORKS.md) — GCP / Cloud Run production path
- [SECURITY-HARDENING.md](SECURITY-HARDENING.md) — rate limit, body cap, path traversal, CI gates
