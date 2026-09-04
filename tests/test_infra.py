"""Infrastructure and GCP adapter tests (no live GCP required)."""

from __future__ import annotations

import base64
import json

import pytest

from operator_etl.config import Settings
from operator_etl_gcp.pubsub import decode_pubsub_push


def test_table_ref() -> None:
    s = Settings(
        gcp_project="proj",
        bq_dataset_bronze="etl_bronze_staging",
        bq_dataset_gold="etl_gold_staging",
    )
    assert s.table_ref("bronze", "raw_events") == "proj.etl_bronze_staging.raw_events"
    assert s.table_ref("gold", "pipeline_runs") == "proj.etl_gold_staging.pipeline_runs"


def test_is_gcp_flag() -> None:
    assert Settings(backend="duckdb").is_gcp is False
    assert Settings(backend="duckdb").uses_bigquery is False
    assert Settings(backend="bigquery", gcp_project="x").is_gcp is True
    assert Settings(backend="bigquery", gcp_project="x").uses_bigquery is True


def test_pubsub_gcs_decode() -> None:
    payload = {
        "bucket": "operator-etl-inbox",
        "name": "incoming/comments.csv",
        "contentType": "text/csv",
    }
    envelope = {
        "message": {
            "data": base64.b64encode(json.dumps(payload).encode()).decode(),
        }
    }
    event = decode_pubsub_push(envelope)
    assert event.bucket == "operator-etl-inbox"
    assert event.object_name == "incoming/comments.csv"
    assert event.is_csv is True


def test_pubsub_missing_data_raises() -> None:
    with pytest.raises(ValueError, match="missing data"):
        decode_pubsub_push({"message": {}})


def test_bigquery_sql_rewrite() -> None:
    from operator_etl_gcp.load.bigquery import BigQueryConnection

    settings = Settings(
        gcp_project="proj",
        bq_dataset_silver="etl_silver_staging",
        bq_dataset_gold="etl_gold_staging",
    )

    class FakeResult:
        schema = []

        def __iter__(self):
            return iter([])

        def values(self):
            return []

    class FakeClient:
        last_sql = ""

        def query(self, sql, job_config=None):
            self.last_sql = sql
            return self

        def result(self):
            return FakeResult()

    con = BigQueryConnection(FakeClient(), settings)
    con.execute("SELECT * FROM silver_comments LIMIT 1")
    assert "`proj.etl_silver_staging.comments`" in con.client.last_sql
