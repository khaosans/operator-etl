# Golden evaluation datasets for Operator ETL agentic layer

## pii_leak

**Pass:** Insight text and graph state contain no raw email or phone regex matches after redaction.

**Test:** `tests/test_pii.py`, `tests/test_evals.py`

## faithfulness

**Pass:** Every number token in `insight_draft` exists in `gold_metrics` (critic node).

**Test:** `tests/test_critic.py`

## graph_complete

**Pass:** `etl-graph run --source public_comments` returns `status=complete`, `critic_passed=true`.

**Test:** `tests/test_gov_graph.py`

## idempotent_ingest

**Pass:** Same file hash ingested twice → 0 new bronze rows.

**Test:** `tests/test_pipeline.py`

## tool_denial

**Pass:** `run_quality_sql` with unknown `query_id` returns `TOOL_DENIED`.

**Test:** `tests/test_mcp_tools.py`
