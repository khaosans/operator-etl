from __future__ import annotations

from operator_etl.config import Settings, set_settings
from operator_etl.load.duckdb import connect
from operator_etl.pipeline import ingest_source
from operator_etl.transform.gov_clean import transform_comments_bronze
from operator_etl.insights.gov_metrics import build_gov_marts, gov_quality_gate
from operator_etl_graph.graph import run_graph
from helpers import assert_insight_grounded_in_metrics, assert_no_pii_leak


def test_public_comments_ingest_and_transform(gov_settings: Settings) -> None:
    result = ingest_source("public_comments", gov_settings)
    assert result.rows_in == 12
    con = connect(gov_settings)
    stats = transform_comments_bronze(con)
    con.close()
    assert stats.rows_silver == 10
    assert stats.rows_quarantined == 2


def test_gov_ingest_is_idempotent(gov_settings: Settings) -> None:
    first = ingest_source("public_comments", gov_settings)
    assert first.rows_in == 12
    assert first.files_skipped == 0

    second = ingest_source("public_comments", gov_settings)
    assert second.rows_in == 0
    assert second.files_skipped == 1

    con = connect(gov_settings)
    bronze = con.execute("SELECT COUNT(*) FROM bronze_raw").fetchone()[0]
    files = con.execute("SELECT COUNT(*) FROM ingest_files").fetchone()[0]
    con.close()
    assert bronze == 12
    assert files == 1


def test_quarantine_preserves_bad_rows_with_errors(gov_settings: Settings) -> None:
    ingest_source("public_comments", gov_settings)
    con = connect(gov_settings)
    transform_comments_bronze(con)
    rows = con.execute("SELECT _row_num, error FROM quarantine_comments ORDER BY _row_num").fetchall()
    con.close()
    assert len(rows) == 2
    errors = " | ".join(r[1] for r in rows)
    assert "body" in errors.lower()
    assert "datetime" in errors.lower() or "date" in errors.lower()


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


def test_graph_insight_contains_no_pii(gov_settings: Settings) -> None:
    set_settings(gov_settings)
    result = run_graph(source="public_comments", settings=gov_settings)
    assert_no_pii_leak(result["insight_draft"])


def test_graph_insight_numbers_match_gold_metrics(gov_settings: Settings) -> None:
    set_settings(gov_settings)
    result = run_graph(source="public_comments", settings=gov_settings)
    assert result["status"] == "complete"
    metrics = result.get("gold_metrics") or {}
    assert metrics.get("comment_count") == 10
    assert_insight_grounded_in_metrics(result["insight_draft"], metrics)


def test_graph_persists_insight_row(gov_settings: Settings) -> None:
    set_settings(gov_settings)
    result = run_graph(source="public_comments", settings=gov_settings)
    assert result["status"] == "complete"
    assert result.get("insight_id")

    con = connect(gov_settings)
    row = con.execute(
        "SELECT text, critic_passed FROM insights WHERE insight_id = ?",
        [result["insight_id"]],
    ).fetchone()
    con.close()
    assert row is not None
    assert row[1] is True
    assert_no_pii_leak(row[0])
    assert_insight_grounded_in_metrics(row[0], result["gold_metrics"] or {})


def test_graph_needs_human_when_quality_fails(gov_settings: Settings, tmp_path) -> None:
    strict = Settings(
        root=gov_settings.root,
        warehouse=tmp_path / "strict.duckdb",
        pipeline_name="public_comments",
        domain="gov",
        max_quarantine_rate=0.01,
    )
    set_settings(strict)
    result = run_graph(source="public_comments", settings=strict)
    assert result["quality_passes"] is False
    assert result["status"] == "needs_human"
