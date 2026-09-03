"""Optional live BigQuery integration — skipped without credentials."""

from __future__ import annotations

import os

import pytest


pytestmark = pytest.mark.integration


def _bq_ready() -> bool:
    return (
        os.environ.get("OPERATOR_ETL_BQ_INTEGRATION") == "1"
        and bool(os.environ.get("OPERATOR_ETL_GCP_PROJECT"))
        and os.environ.get("OPERATOR_ETL_BACKEND") == "bigquery"
    )


@pytest.mark.skipif(not _bq_ready(), reason="Set OPERATOR_ETL_BQ_INTEGRATION=1 and GCP project for live BQ")
def test_live_bigquery_gold_mart_round_trip() -> None:
    from operator_etl.config import Settings, get_settings, set_settings
    from operator_etl.insights.gov_metrics import build_gov_marts, gov_quality_gate
    from operator_etl.load.connection import connect
    from operator_etl.transform.gov_clean import init_gov_schema

    settings = get_settings()
    assert settings.backend == "bigquery"
    con = connect(settings)
    try:
        init_gov_schema(con)
        build_gov_marts(con, settings)
        gate = gov_quality_gate(con, settings)
        assert gate.bronze_rows >= 0
    finally:
        con.close()
        set_settings(None)
