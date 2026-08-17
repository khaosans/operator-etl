from __future__ import annotations

from operator_etl.config import Settings, set_settings
from operator_etl.load.duckdb import connect
from operator_etl.pipeline import ingest_source
from operator_etl.transform.gov_clean import transform_comments_bronze
from operator_etl.insights.gov_metrics import build_gov_marts, gov_quality_gate
from operator_etl_graph.graph import run_graph


def test_public_comments_ingest_and_transform(gov_settings: Settings) -> None:
    result = ingest_source("public_comments", gov_settings)
    assert result.rows_in == 12
    con = connect(gov_settings)
    stats = transform_comments_bronze(con)
    con.close()
    assert stats.rows_silver == 10
    assert stats.rows_quarantined == 2


def test_gov_gold_marts(gov_settings: Settings) -> None:
    ingest_source("public_comments", gov_settings)
    con = connect(gov_settings)
    transform_comments_bronze(con)
    build_gov_marts(con, gov_settings)
    kpis = con.execute("SELECT comment_count, pii_flagged_count FROM gold_comment_kpis").fetchone()
    gate = gov_quality_gate(con, gov_settings)
    con.close()
    assert kpis[0] == 10
    assert kpis[1] >= 4
    assert gate.passes


def test_graph_pipeline_completes(gov_settings: Settings) -> None:
    set_settings(gov_settings)
    result = run_graph(source="public_comments", settings=gov_settings)
    assert result["status"] == "complete"
    assert result["rows_silver"] == 10
    assert result["critic_passed"] is True
    assert "comment" in result["insight_draft"].lower()
