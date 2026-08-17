from __future__ import annotations

import pytest

from operator_etl.config import Settings
from operator_etl.load.duckdb import connect
from operator_etl_mcp.tools import ToolDenied, run_allowlisted_sql


def test_allowlist_denies_unknown_query(gov_settings: Settings) -> None:
    con = connect(gov_settings)
    with pytest.raises(ToolDenied):
        run_allowlisted_sql(con, "drop_all_tables", settings=gov_settings)
    con.close()


def test_allowlist_permits_comment_quality(gov_settings: Settings) -> None:
    from operator_etl.pipeline import ingest_source
    from operator_etl.transform.gov_clean import transform_comments_bronze
    from operator_etl.insights.gov_metrics import build_gov_marts

    ingest_source("public_comments", gov_settings)
    con = connect(gov_settings)
    transform_comments_bronze(con)
    build_gov_marts(con, gov_settings)
    result = run_allowlisted_sql(con, "comment_quality", settings=gov_settings)
    con.close()
    assert "quarantine_rate" in result["columns"]
