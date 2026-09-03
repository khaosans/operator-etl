from __future__ import annotations

import uuid
from dataclasses import dataclass

from operator_etl.config import Settings, get_settings
from operator_etl.extract.csv import ExtractResult, extract_csv, extract_csv_dir
from operator_etl.extract.http import extract_http
from operator_etl.insights.metrics import build_marts, render_insights
from operator_etl.load.connection import connect
from operator_etl.load.duckdb import (
    already_ingested,
    finish_run,
    load_bronze,
    start_run,
)
from operator_etl.sources import Source, get_source
from operator_etl.transform.clean import TransformStats, transform_bronze


@dataclass
class RunResult:
    run_id: str
    source: str
    rows_in: int
    rows_silver: int
    rows_quarantined: int
    files_skipped: int
    status: str
    insights: str | None = None
    error: str | None = None


def collect_extracts(source: Source, settings: Settings) -> list[ExtractResult]:
    if source.kind == "csv":
        if source.path is None:
            raise ValueError(f"Source {source.name} is csv but has no path")
        return [extract_csv(source.path)]
    if source.kind == "csv_dir":
        if source.path is None:
            raise ValueError(f"Source {source.name} is csv_dir but has no path")
        return extract_csv_dir(source.path)
    if source.kind == "http":
        if not source.url:
            raise ValueError(f"Source {source.name} is http but has no url")
        return [extract_http(source.url, root=settings.root)]
    if source.kind == "gcs":
        from operator_etl_gcp.extract.gcs import extract_gcs_inbox

        bucket = settings.gcs_inbox_bucket
        if not bucket:
            raise ValueError("OPERATOR_ETL_GCS_INBOX_BUCKET required for gcs source")
        prefix = str(source.path) if source.path else ""
        return extract_gcs_inbox(bucket, prefix, settings)
    if source.kind == "regulations_gov":
        from operator_etl.extract.regulations_gov import (
            fetch_comments_for_docket,
            load_sample_fallback,
            rows_to_extract,
        )

        docket_id = source.docket_id or (source.options or {}).get("docket_id")
        sample = source.path
        try:
            if not docket_id:
                raise ValueError("regulations_gov source requires docket_id")
            rows = fetch_comments_for_docket(str(docket_id))
            return [rows_to_extract(rows, file_name=f"regulations_gov_{docket_id}.csv")]
        except Exception:
            if sample and sample.exists():
                return [load_sample_fallback(sample)]
            raise
    raise ValueError(f"Unsupported source kind {source.kind}")


def ingest_source(source_name: str, settings: Settings | None = None) -> RunResult:
    settings = settings or get_settings()
    source = get_source(source_name, settings)
    run_id = str(uuid.uuid4())
    con = connect(settings)
    start_run(con, run_id, source.name)
    rows_in = 0
    skipped = 0
    try:
        extracts = collect_extracts(source, settings)
        if not extracts:
            finish_run(con, run_id, status="ok", rows_in=0, files_skipped=0)
            return RunResult(run_id, source.name, 0, 0, 0, 0, "ok")
        for extracted in extracts:
            if already_ingested(con, extracted.content_hash):
                skipped += 1
                continue
            rows_in += load_bronze(con, source=source.name, extracted=extracted)
        finish_run(con, run_id, status="ok", rows_in=rows_in, files_skipped=skipped)
        return RunResult(run_id, source.name, rows_in, 0, 0, skipped, "ok")
    except Exception as exc:
        finish_run(con, run_id, status="error", rows_in=rows_in, files_skipped=skipped, error=str(exc))
        raise
    finally:
        con.close()


def run_pipeline(source_name: str, settings: Settings | None = None) -> RunResult:
    settings = settings or get_settings()
    source = get_source(source_name, settings)
    run_id = str(uuid.uuid4())
    con = connect(settings)
    start_run(con, run_id, source.name)
    rows_in = 0
    skipped = 0
    transform = TransformStats(0, 0, 0)
    try:
        extracts = collect_extracts(source, settings)
        for extracted in extracts:
            if already_ingested(con, extracted.content_hash):
                skipped += 1
                continue
            rows_in += load_bronze(con, source=source.name, extracted=extracted)
        transform = transform_bronze(con)
        build_marts(con, settings)
        insights = render_insights(con, settings)
        finish_run(
            con,
            run_id,
            status="ok",
            rows_in=rows_in,
            rows_silver=transform.rows_silver,
            rows_quarantined=transform.rows_quarantined,
            files_skipped=skipped,
        )
        return RunResult(
            run_id=run_id,
            source=source.name,
            rows_in=rows_in,
            rows_silver=transform.rows_silver,
            rows_quarantined=transform.rows_quarantined,
            files_skipped=skipped,
            status="ok",
            insights=insights,
        )
    except Exception as exc:
        finish_run(
            con,
            run_id,
            status="error",
            rows_in=rows_in,
            rows_silver=transform.rows_silver,
            rows_quarantined=transform.rows_quarantined,
            files_skipped=skipped,
            error=str(exc),
        )
        raise
    finally:
        con.close()
