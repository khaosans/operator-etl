from __future__ import annotations

import pytest

from operator_etl.config import Settings
from operator_etl.load.duckdb import connect
from operator_etl.load.ops import start_run
from operator_etl_mcp.tools import (
    ToolDenied,
    get_gold_metrics,
    get_run_status,
    load_allowlist,
    run_allowlisted_sql,
)


def test_run_quality_sql_denies_unknown_query_id(gov_settings: Settings) -> None:
    """run_quality_sql: allowlisted IDs only; unknown query_id returns TOOL_DENIED."""
    con = connect(gov_settings)
    with pytest.raises(ToolDenied):
        run_allowlisted_sql(con, "drop_all_tables", settings=gov_settings)
    con.close()


def test_run_quality_sql_permits_comment_quality(gov_settings: Settings) -> None:
    """run_quality_sql: comment_quality allowlist query returns quarantine_rate."""
    from operator_etl.insights.gov_metrics import build_gov_marts
    from operator_etl.pipeline import ingest_source
    from operator_etl.transform.gov_clean import transform_comments_bronze

    ingest_source("public_comments", gov_settings)
    con = connect(gov_settings)
    transform_comments_bronze(con)
    build_gov_marts(con, gov_settings)
    result = run_allowlisted_sql(con, "comment_quality", settings=gov_settings)
    con.close()
    assert "quarantine_rate" in result["columns"]


def test_allowlist_has_no_vault_tools(gov_settings: Settings) -> None:
    spec = load_allowlist(gov_settings)
    for entry in spec.get("queries", []):
        query_id = entry["id"].lower()
        assert "vault" not in query_id
        assert "decrypt" not in query_id


def test_get_gold_metrics_returns_expected_kpis(gov_settings: Settings) -> None:
    """get_gold_metrics: aggregate KPIs from gold_comment_kpis (no row-level data)."""
    from operator_etl.insights.gov_metrics import build_gov_marts
    from operator_etl.pipeline import ingest_source
    from operator_etl.transform.gov_clean import transform_comments_bronze

    ingest_source("public_comments", gov_settings)
    con = connect(gov_settings)
    transform_comments_bronze(con)
    build_gov_marts(con, gov_settings)
    metrics = get_gold_metrics(con, domain="gov")
    con.close()
    assert metrics["comment_count"] == 10
    assert metrics["pii_flagged_count"] >= 4
    assert 0 <= metrics["pii_rate"] <= 1


def test_get_run_status_returns_audit_row(gov_settings: Settings) -> None:
    """get_run_status: returns pipeline_runs audit row for a known run_id."""
    con = connect(gov_settings)
    start_run(con, "run-mcp-test-001", "public_comments")
    result = get_run_status(con, "run-mcp-test-001")
    con.close()
    assert result["run_id"] == "run-mcp-test-001"
    assert result["source"] == "public_comments"
    assert result["status"] == "running"


def test_get_run_status_not_found(gov_settings: Settings) -> None:
    """get_run_status: unknown run_id returns NOT_FOUND error shape."""
    con = connect(gov_settings)
    result = get_run_status(con, "run-does-not-exist")
    con.close()
    assert result == {"error": "NOT_FOUND"}
