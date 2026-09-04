from __future__ import annotations

from pathlib import Path

from operator_etl.extract.csv import extract_csv
from operator_etl.load.duckdb import connect
from operator_etl.load.ops import already_ingested, load_bronze
from operator_etl.pipeline import ingest_source, run_pipeline
from operator_etl.transform.clean import transform_bronze


def test_ingest_is_idempotent_on_file_hash(settings) -> None:
    first = ingest_source("demo", settings)
    assert first.rows_in == 21
    assert first.files_skipped == 0

    second = ingest_source("demo", settings)
    assert second.rows_in == 0
    assert second.files_skipped == 1

    con = connect(settings)
    bronze = con.execute("SELECT COUNT(*) FROM bronze_raw").fetchone()[0]
    files = con.execute("SELECT COUNT(*) FROM ingest_files").fetchone()[0]
    con.close()
    assert bronze == 21
    assert files == 1


def test_load_bronze_skips_when_hash_recorded(settings) -> None:
    path = Path(settings.root) / "samples" / "orders.csv"
    extracted = extract_csv(path)
    con = connect(settings)
    assert already_ingested(con, extracted.content_hash) is False
    load_bronze(con, source="demo", extracted=extracted)
    assert already_ingested(con, extracted.content_hash) is True
    con.close()


def test_quarantine_invalid_rows(settings) -> None:
    ingest_source("demo", settings)
    con = connect(settings)
    stats = transform_bronze(con)
    quarantined = con.execute("SELECT error FROM quarantine_orders ORDER BY _row_num").fetchall()
    silver = con.execute("SELECT COUNT(*) FROM silver_orders").fetchone()[0]
    con.close()

    assert stats.rows_silver == 17
    assert stats.rows_quarantined == 4
    assert silver == 17
    errors = " | ".join(row[0] for row in quarantined)
    assert "empty" in errors or "missing" in errors or "required" in errors
    assert (
        "not-a-date" in errors
        or "datetime" in errors.lower()
        or "Input should be a valid datetime" in errors
    )
    assert "greater than 0" in errors or "-5" in errors
    assert "amount" in errors.lower() or "free" in errors or "valid number" in errors.lower()


def test_run_builds_gold_and_passes_gate(settings) -> None:
    result = run_pipeline("demo", settings)
    assert result.status == "ok"
    assert result.rows_silver == 17
    assert result.rows_quarantined == 4
    assert result.insights is not None
    assert "Quality: PASS" in result.insights
    assert "orders          17" in result.insights
    assert "SKU-PRO" in result.insights

    con = connect(settings)
    kpis = con.execute("SELECT order_count, customer_count FROM gold_kpis").fetchone()
    con.close()
    assert kpis == (17, 10)
