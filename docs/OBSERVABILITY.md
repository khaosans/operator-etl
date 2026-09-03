# Observability

Operator ETL ships opt-in OpenTelemetry tracing and metrics for the LangGraph pipeline, MCP tools, and the A2A task surface. Telemetry is **off by default** and **sanitized by design**: spans and metrics carry run IDs, counts, durations, and outcomes — never raw records, payloads, or PII.

Added in `0.5.1`. Code: [`src/telemetry/`](../src/telemetry/). Streamlit view: the **Observability & Spans** tab ([DASHBOARD.md](DASHBOARD.md)).

---

## Enable it

Telemetry initializes lazily and stays inert until an OTLP endpoint is configured:

```bash
# Export to any OTLP/HTTP collector (Jaeger, Grafana Tempo, Honeycomb, ...)
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
export OTEL_SERVICE_NAME=operator-etl        # optional, this is the default
```

Traces post to `<endpoint>/v1/traces` and metrics to `<endpoint>/v1/metrics` ([src/telemetry/config.py](../src/telemetry/config.py)). With no endpoint set, providers run locally with no exporter — `telemetry_enabled()` is `False` and nothing leaves the box. See the commented block in [`.env.example`](../.env.example).

### Optional LLM tracing (OpenInference)

```bash
export LANGCHAIN_TRACING_V2=true
```

Instruments LangChain via OpenInference with `hide_inputs=True` / `hide_outputs=True`, so prompt and completion contents are never captured — only call structure and timing.

---

## What gets recorded

### Spans ([src/telemetry/tracer.py](../src/telemetry/tracer.py))

| Span | Emitted for |
|---|---|
| `operator_etl.node.<name>` | Each LangGraph node (ingest, validate_load, build_gold, pii_gate, critic, …) |
| `operator_etl.route.<name>` | Conditional branch decisions (e.g. HITL routing) |
| `operator_etl.graph.error` | Graph exceptions (records exception type only) |
| `operator_etl.a2a.task` / `operator_etl.a2a.jsonrpc` | A2A task execution and JSON-RPC dispatch |

Span attributes are restricted to a safe allowlist (`run_id`, `source`, `domain`, `status`, `rows_in`, `rows_silver`, `rows_quarantined`, `quality_passes`, `critic_passed`, retry/LLM-call counters). Any non-scalar or unlisted value is dropped or stringified by `safe_attributes` / `state_attributes`.

### Metrics (counters)

| Counter | Unit | Dimensions |
|---|---|---|
| `etl.rows.processed` | rows | `stage` = bronze / silver / gold |
| `etl.rows.quarantined` | rows | `reason` (normalized) |
| `etl.pii.detections` | detections | `entity_type` — **counts only, no values** |
| `etl.critic.evaluations` | evaluations | `outcome` = passed / failed |

---

## Safety boundary

- Off unless `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
- No raw records, comment bodies, SQL, or PII values in spans, metrics, or the dashboard — only metadata (IDs, counts, durations, outcomes).
- PII is counted by entity type, never emitted by value.
- LLM inputs/outputs are hidden when OpenInference instrumentation is on.

This mirrors the same fail-closed, no-raw-PII rule enforced across the pipeline, MCP, and A2A surfaces ([A2A.md](A2A.md), [NIST.md](NIST.md)).

---

## See also

- [RUNNING.md](RUNNING.md) — start the services that emit telemetry
- [DASHBOARD.md](DASHBOARD.md) — the Observability & Spans tab
- [A2A.md](A2A.md) — task surface that reuses the same tracing
- [TESTING.md](TESTING.md) — `tests/test_telemetry.py` coverage
