"""DuckDB warehouse backend — local MVP path."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import duckdb
import pandas as pd

from operator_etl.config import Settings, get_settings
from operator_etl.extract.csv import ExtractResult

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ingest_files (
    content_hash VARCHAR PRIMARY KEY,
    file_name VARCHAR,
    source VARCHAR,
    ingested_at TIMESTAMP,
    row_count INTEGER
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id VARCHAR PRIMARY KEY,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    source VARCHAR,
    status VARCHAR,
    rows_in INTEGER DEFAULT 0,
    rows_silver INTEGER DEFAULT 0,
    rows_quarantined INTEGER DEFAULT 0,
    files_skipped INTEGER DEFAULT 0,
    error VARCHAR
);

CREATE TABLE IF NOT EXISTS bronze_raw (
    _content_hash VARCHAR,
    _file_name VARCHAR,
    _source VARCHAR,
    _ingested_at TIMESTAMP,
    _row_num INTEGER,
    payload JSON,
    PRIMARY KEY (_content_hash, _row_num)
);

CREATE TABLE IF NOT EXISTS silver_orders (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR,
    ordered_at TIMESTAMP,
    amount DOUBLE,
    sku VARCHAR,
    status VARCHAR,
    _content_hash VARCHAR,
    _row_num INTEGER,
    _source VARCHAR,
    _ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quarantine_orders (
    _content_hash VARCHAR,
    _row_num INTEGER,
    _source VARCHAR,
    _ingested_at TIMESTAMP,
    payload JSON,
    error VARCHAR,
    PRIMARY KEY (_content_hash, _row_num)
);
"""


def connect(settings: Settings | None = None) -> duckdb.DuckDBPyConnection:
    settings = settings or get_settings()
    path = settings.warehouse_path
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    # Annotate for WarehouseConnection / load.ops dispatch (C extension may reject setattr).
    try:
        con.backend = "duckdb"  # type: ignore[attr-defined]
    except (AttributeError, TypeError):
        pass
    init_schema(con)
    return con


def init_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(SCHEMA_SQL)


def already_ingested(con: duckdb.DuckDBPyConnection, content_hash: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM ingest_files WHERE content_hash = ?",
        [content_hash],
    ).fetchone()
    return row is not None


def load_bronze(
    con: duckdb.DuckDBPyConnection,
    *,
    source: str,
    extracted: ExtractResult,
    ingested_at: datetime | None = None,
) -> int:
    """Insert bronze rows. Caller must skip when already_ingested is true."""
    if not extracted.rows:
        con.execute(
            """
            INSERT INTO ingest_files (content_hash, file_name, source, ingested_at, row_count)
            VALUES (?, ?, ?, ?, 0)
            """,
            [
                extracted.content_hash,
                extracted.file_name,
                source,
                ingested_at or datetime.now(UTC).replace(tzinfo=None),
            ],
        )
        return 0

    stamp = ingested_at or datetime.now(UTC).replace(tzinfo=None)
    frame = pd.DataFrame(
        {
            "_content_hash": extracted.content_hash,
            "_file_name": extracted.file_name,
            "_source": source,
            "_ingested_at": stamp,
            "_row_num": list(range(1, len(extracted.rows) + 1)),
            "payload": [json.dumps(row, ensure_ascii=False) for row in extracted.rows],
        }
    )
    con.register("bronze_batch", frame)
    con.execute("INSERT INTO bronze_raw SELECT * FROM bronze_batch")
    con.unregister("bronze_batch")
    con.execute(
        """
        INSERT INTO ingest_files (content_hash, file_name, source, ingested_at, row_count)
        VALUES (?, ?, ?, ?, ?)
        """,
        [extracted.content_hash, extracted.file_name, source, stamp, len(extracted.rows)],
    )
    return len(extracted.rows)


def start_run(con: duckdb.DuckDBPyConnection, run_id: str, source: str) -> None:
    con.execute(
        """
        INSERT INTO pipeline_runs (run_id, started_at, source, status)
        VALUES (?, ?, ?, 'running')
        """,
        [run_id, datetime.now(UTC).replace(tzinfo=None), source],
    )


def finish_run(
    con: duckdb.DuckDBPyConnection,
    run_id: str,
    *,
    status: str,
    rows_in: int = 0,
    rows_silver: int = 0,
    rows_quarantined: int = 0,
    files_skipped: int = 0,
    error: str | None = None,
) -> None:
    con.execute(
        """
        UPDATE pipeline_runs
        SET finished_at = ?,
            status = ?,
            rows_in = ?,
            rows_silver = ?,
            rows_quarantined = ?,
            files_skipped = ?,
            error = ?
        WHERE run_id = ?
        """,
        [
            datetime.now(UTC).replace(tzinfo=None),
            status,
            rows_in,
            rows_silver,
            rows_quarantined,
            files_skipped,
            error,
            run_id,
        ],
    )
