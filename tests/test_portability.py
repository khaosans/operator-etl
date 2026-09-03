"""Portability scaffolding — warehouse protocol, object store, checkpoints, settings."""

from __future__ import annotations

from operator_etl.checkpoints import build_checkpointer
from operator_etl.config import Settings
from operator_etl.extract.object_store import MemoryObjectStore, extract_inbox
from operator_etl.load.ops import already_ingested, finish_run, load_bronze, start_run
from operator_etl.load.protocol import WarehouseConnection
from operator_etl.sources import get_source


def test_uses_bigquery_and_is_gcp_alias() -> None:
    local = Settings(backend="duckdb")
    assert local.uses_bigquery is False
    assert local.is_gcp is False
    cloud = Settings(backend="bigquery", gcp_project="x")
    assert cloud.uses_bigquery is True
    assert cloud.is_gcp is True


def test_inbox_uri_resolves_bucket_and_prefix() -> None:
    s = Settings(inbox_uri="gs://my-bucket/incoming/path")
    assert s.resolved_inbox_bucket == "my-bucket"
    assert s.resolved_inbox_prefix == "incoming/path"
    legacy = Settings(gcs_inbox_bucket="legacy-bucket")
    assert legacy.resolved_inbox_bucket == "legacy-bucket"


def test_memory_object_store_extract_inbox() -> None:
    csv_body = b"comment_id,agency\n1,EPA\n"
    store = MemoryObjectStore(
        {
            "incoming/a.csv": csv_body,
            "incoming/skip.txt": b"nope",
            "other/b.csv": csv_body,
        }
    )
    results = extract_inbox(store, "incoming/")
    assert len(results) == 1
    assert results[0].file_name == "a.csv"
    assert results[0].rows == [{"comment_id": "1", "agency": "EPA"}]


def test_gcs_source_kind_keeps_prefix_path(gov_settings) -> None:
    source = get_source("gcs_inbox", gov_settings)
    assert source.kind == "gcs"
    assert source.path is not None
    assert str(source.path).rstrip("/") == "incoming"


def test_checkpoints_import_from_core(settings) -> None:
    saver = build_checkpointer(settings)
    assert saver is not None
    # GCP shim still re-exports
    from operator_etl_gcp.checkpoints import build_checkpointer as gcp_build

    assert gcp_build is build_checkpointer or callable(gcp_build)


def test_duckdb_load_ops_roundtrip(settings) -> None:
    from operator_etl.extract.csv import ExtractResult
    from operator_etl.load.duckdb import connect

    con = connect(settings)
    assert getattr(con, "backend", "duckdb") in ("duckdb",)
    start_run(con, "run-port-1", "demo")
    extracted = ExtractResult(file_name="t.csv", content_hash="abc123hash", rows=[{"a": "1"}])
    assert already_ingested(con, extracted.content_hash) is False
    assert load_bronze(con, source="demo", extracted=extracted) == 1
    assert already_ingested(con, extracted.content_hash) is True
    finish_run(con, "run-port-1", status="ok", rows_in=1)
    con.close()


def test_bigquery_connection_satisfies_protocol() -> None:
    from operator_etl_gcp.load.bigquery import BigQueryConnection

    settings = Settings(gcp_project="proj")
    con = BigQueryConnection(client=object(), settings=settings)
    assert isinstance(con, WarehouseConnection)
    assert con.backend == "bigquery"
