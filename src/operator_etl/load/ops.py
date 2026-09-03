"""Neutral load operations — dispatch by connection backend."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from operator_etl.extract.csv import ExtractResult


def _backend(con: Any) -> str:
    return getattr(con, "backend", "duckdb")


def already_ingested(con: Any, content_hash: str) -> bool:
    if _backend(con) == "bigquery":
        from operator_etl_gcp.load.bigquery import already_ingested as bq_already_ingested

        return bq_already_ingested(con, content_hash)
    from operator_etl.load import duckdb as duck

    return duck.already_ingested(con, content_hash)


def load_bronze(
    con: Any,
    *,
    source: str,
    extracted: ExtractResult,
    ingested_at: datetime | None = None,
) -> int:
    """Insert bronze rows. Caller must skip when already_ingested is true."""
    if _backend(con) == "bigquery":
        from operator_etl_gcp.load.bigquery import load_bronze as bq_load_bronze

        return bq_load_bronze(con, source=source, extracted=extracted, ingested_at=ingested_at)
    from operator_etl.load import duckdb as duck

    return duck.load_bronze(con, source=source, extracted=extracted, ingested_at=ingested_at)


def start_run(con: Any, run_id: str, source: str) -> None:
    if _backend(con) == "bigquery":
        from operator_etl_gcp.load.bigquery import start_run as bq_start_run

        return bq_start_run(con, run_id, source)
    from operator_etl.load import duckdb as duck

    return duck.start_run(con, run_id, source)


def finish_run(
    con: Any,
    run_id: str,
    *,
    status: str,
    rows_in: int = 0,
    rows_silver: int = 0,
    rows_quarantined: int = 0,
    files_skipped: int = 0,
    error: str | None = None,
) -> None:
    if _backend(con) == "bigquery":
        from operator_etl_gcp.load.bigquery import finish_run as bq_finish_run

        return bq_finish_run(
            con,
            run_id,
            status=status,
            rows_in=rows_in,
            rows_silver=rows_silver,
            rows_quarantined=rows_quarantined,
            files_skipped=files_skipped,
            error=error,
        )
    from operator_etl.load import duckdb as duck

    return duck.finish_run(
        con,
        run_id,
        status=status,
        rows_in=rows_in,
        rows_silver=rows_silver,
        rows_quarantined=rows_quarantined,
        files_skipped=files_skipped,
        error=error,
    )
