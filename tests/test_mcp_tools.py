from __future__ import annotations

import pytest

from operator_etl.config import Settings
from operator_etl.load.duckdb import connect
from operator_etl_mcp.tools import ToolDenied, get_gold_metrics, load_allowlist, run_allowlisted_sql


def test_allowlist_denies_unknown_query(gov_settings: Settings) -> None:
    con = connect(gov_settings)
    with pytest.raises(ToolDenied):
        run_allowlisted_sql(con, "drop_all_tables", settings=gov_settings)
    con.close()


def test_allowlist_permits_comment_quality(gov_settings: Settings) -> None:
    from operator_etl.pipeline import ingest_source
    from operator_etl.transform.gov_clean import transform_comments_bronze
    from operator_etl.insights.gov_metrics import build_gov_marts

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
    from operator_etl.pipeline import ingest_source
    from operator_etl.transform.gov_clean import transform_comments_bronze
    from operator_etl.insights.gov_metrics import build_gov_marts

    ingest_source("public_comments", gov_settings)
    con = connect(gov_settings)
    transform_comments_bronze(con)
    build_gov_marts(con, gov_settings)
    metrics = get_gold_metrics(con, domain="gov")
    con.close()
    assert metrics["comment_count"] == 10
    assert metrics["pii_flagged_count"] >= 4
    assert 0 <= metrics["pii_rate"] <= 1
