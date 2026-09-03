"""BigQuery gold mart dialect + rewrite coverage (no live GCP)."""

from __future__ import annotations

from pathlib import Path

from operator_etl.config import Settings
from operator_etl.insights.gov_metrics import build_gov_marts
from operator_etl_gcp.load.bigquery import BigQueryConnection, TABLE_MAP


def test_bq_gov_mart_sql_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    bq_dir = root / "sql" / "marts" / "gov" / "bq"
    files = sorted(p.name for p in bq_dir.glob("*.sql"))
    assert files == [
        "01_gold_comment_kpis.sql",
        "02_gold_comments_by_agency.sql",
        "03_gold_comments_by_docket.sql",
        "04_gold_comment_quality.sql",
    ]
    kpi = (bq_dir / "01_gold_comment_kpis.sql").read_text()
    assert "COUNTIF(pii_detected)" in kpi
    assert "SAFE_DIVIDE" in kpi


def test_build_gov_marts_selects_bq_dialect(tmp_path: Path) -> None:
    settings = Settings(
        root=Path(__file__).resolve().parents[1],
        domain="gov",
        backend="bigquery",
        gcp_project="proj",
        bq_dataset_silver="etl_silver_staging",
        bq_dataset_gold="etl_gold_staging",
        bq_dataset_bronze="etl_bronze_staging",
        bq_dataset_quarantine="etl_quarantine_staging",
    )

    class FakeResult:
        schema = []

        def __iter__(self):
            return iter([])

    class FakeClient:
        def __init__(self):
            self.sqls: list[str] = []

        def query(self, sql, job_config=None):
            self.sqls.append(sql)
            return self

        def result(self):
            return FakeResult()

    client = FakeClient()
    con = BigQueryConnection(client, settings)
    build_gov_marts(con, settings)
    assert len(client.sqls) == 4
    joined = "\n".join(client.sqls)
    assert "`proj.etl_silver_staging.comments`" in joined
    assert "`proj.etl_gold_staging.gold_comment_kpis`" in joined
    assert "COUNTIF" in joined
    for logical in (
        "gold_comment_kpis",
        "gold_comments_by_agency",
        "gold_comments_by_docket",
        "gold_comment_quality",
        "silver_comments",
        "bronze_raw",
        "quarantine_comments",
    ):
        assert logical in TABLE_MAP
