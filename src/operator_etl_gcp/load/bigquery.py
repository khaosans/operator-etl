"""BigQuery warehouse backend — production path on GCP."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any

from operator_etl.config import Settings, get_settings

TABLE_MAP = {
    "bronze_raw": ("bronze", "raw_events"),
    "silver_comments": ("silver", "comments"),
    "quarantine_comments": ("quarantine", "comments_rejected"),
    "ingest_files": ("gold", "ingest_files"),
    "pipeline_runs": ("gold", "pipeline_runs"),
    "insights": ("gold", "insights"),
    "gold_comment_kpis": ("gold", "gold_comment_kpis"),
    "gold_comments_by_agency": ("gold", "gold_comments_by_agency"),
    "gold_comments_by_docket": ("gold", "gold_comments_by_docket"),
    "gold_comment_quality": ("gold", "gold_comment_quality"),
}


class BigQueryConnection:
    backend = "bigquery"

    def __init__(self, client: Any, settings: Settings):
        self.client = client
        self.settings = settings
        self._rows: list[tuple] = []
        self._columns: list[str] = []
        self.description: list[tuple[str]] | None = None

    def fqn(self, logical: str) -> str:
        if logical in TABLE_MAP:
            layer, table = TABLE_MAP[logical]
            return self.settings.table_ref(layer, table)
        return logical

    def _rewrite_sql(self, sql: str) -> str:
        out = sql
        for logical in sorted(TABLE_MAP, key=len, reverse=True):
            out = re.sub(rf"\b{logical}\b", f"`{self.fqn(logical)}`", out)
        return out

    def execute(self, sql: str, params: list | None = None) -> BigQueryConnection:
        sql = self._rewrite_sql(sql)
        if params:
            from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter

            rewritten = sql
            query_parameters = []
            for i, value in enumerate(params):
                name = f"p{i}"
                rewritten = rewritten.replace("?", f"@{name}", 1)
                query_parameters.append(ScalarQueryParameter(name, _scalar_type(value), value))
            job = self.client.query(rewritten, job_config=QueryJobConfig(query_parameters=query_parameters))
        else:
            job = self.client.query(sql)
        result = job.result()
        self._columns = [field.name for field in result.schema]
        self._rows = [tuple(row.values()) for row in result]
        self.description = [(c,) for c in self._columns]
        return self

    def fetchone(self) -> tuple | None:
        return self._rows[0] if self._rows else None

    def fetchall(self) -> list[tuple]:
        return list(self._rows)

    def insert_rows(self, logical_table: str, rows: list[dict]) -> None:
        table_id = self.fqn(logical_table)
        errors = self.client.insert_rows_json(table_id, rows)
        if errors:
            raise RuntimeError(f"BigQuery insert errors: {errors}")

    def register(self, name: str, frame: Any) -> None:
        self._registered = (name, frame)

    def unregister(self, name: str) -> None:
        self._registered = None

    def close(self) -> None:
        pass


def _scalar_type(value: Any) -> str:
    if isinstance(value, bool):
        return "BOOL"
    if isinstance(value, int):
        return "INT64"
    if isinstance(value, float):
        return "FLOAT64"
    if isinstance(value, datetime):
        return "TIMESTAMP"
    return "STRING"


def connect_bigquery(settings: Settings | None = None) -> BigQueryConnection:
    settings = settings or get_settings()
    if not settings.gcp_project:
        raise ValueError("OPERATOR_ETL_GCP_PROJECT required when backend=bigquery")
    from google.cloud import bigquery

    client = bigquery.Client(project=settings.gcp_project, location=settings.gcp_region)
    return BigQueryConnection(client, settings)


def already_ingested(con: BigQueryConnection, content_hash: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM ingest_files WHERE content_hash = ? LIMIT 1",
        [content_hash],
    ).fetchone()
    return row is not None


def load_bronze(
    con: BigQueryConnection,
    *,
    source: str,
    extracted: Any,
    ingested_at: datetime | None = None,
) -> int:
    from operator_etl.extract.csv import ExtractResult

    extracted: ExtractResult = extracted
    stamp = ingested_at or datetime.now(UTC).replace(tzinfo=None)
    if not extracted.rows:
        con.insert_rows(
            "ingest_files",
            [{
                "content_hash": extracted.content_hash,
                "file_name": extracted.file_name,
                "source": source,
                "ingested_at": stamp.isoformat(),
                "row_count": 0,
            }],
        )
        return 0

    bronze_rows = [
        {
            "_content_hash": extracted.content_hash,
            "_file_name": extracted.file_name,
            "_source": source,
            "_ingested_at": stamp.isoformat(),
            "_row_num": i,
            "payload": json.loads(json.dumps(row, ensure_ascii=False)),
        }
        for i, row in enumerate(extracted.rows, start=1)
    ]
    con.insert_rows("bronze_raw", bronze_rows)
    con.insert_rows(
        "ingest_files",
        [{
            "content_hash": extracted.content_hash,
            "file_name": extracted.file_name,
            "source": source,
            "ingested_at": stamp.isoformat(),
            "row_count": len(extracted.rows),
        }],
    )
    return len(extracted.rows)


def start_run(con: BigQueryConnection, run_id: str, source: str) -> None:
    con.insert_rows(
        "pipeline_runs",
        [{
            "run_id": run_id,
            "started_at": datetime.now(UTC).replace(tzinfo=None).isoformat(),
            "source": source,
            "status": "running",
            "rows_in": 0,
            "rows_silver": 0,
            "rows_quarantined": 0,
            "files_skipped": 0,
        }],
    )


def finish_run(
    con: BigQueryConnection,
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
