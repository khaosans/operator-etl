from __future__ import annotations

from operator_etl.config import Settings
from operator_etl.insights.metrics import build_marts, quality_gate
from operator_etl.load.duckdb import connect
from operator_etl.pipeline import run_pipeline


def test_quality_gate_blocks_high_quarantine(settings) -> None:
    run_pipeline("demo", settings)
    strict = Settings(
        root=settings.root,
        warehouse=settings.warehouse_path,
        max_quarantine_rate=0.05,
        max_freshness_hours=settings.max_freshness_hours,
    )
    con = connect(settings)
    build_marts(con, settings)
    report = quality_gate(con, strict)
    con.close()
    assert report.passes is False
    assert any("quarantine rate" in reason for reason in report.reasons)
