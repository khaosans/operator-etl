from __future__ import annotations

from operator_etl.config import Settings
from conftest import REPO_ROOT


def test_orders_warehouse_is_independent_of_gov(tmp_path):
    s = Settings(
        root=REPO_ROOT,
        warehouse=tmp_path / "gov.duckdb",
        orders_warehouse=tmp_path / "orders.duckdb",
        insight_backend="template",
    )
    assert s.warehouse_path == tmp_path / "gov.duckdb"
    assert s.orders_warehouse_path == tmp_path / "orders.duckdb"


def test_orders_warehouse_defaults_to_repo_warehouse(tmp_path):
    s = Settings(
        root=REPO_ROOT,
        warehouse=tmp_path / "gov.duckdb",
        insight_backend="template",
    )
    assert s.orders_warehouse_path == REPO_ROOT / "warehouse" / "operator.duckdb"
