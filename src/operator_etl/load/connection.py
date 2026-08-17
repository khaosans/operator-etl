"""Warehouse connection factory — dispatches DuckDB (local) or BigQuery (GCP)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from operator_etl.config import Settings, get_settings

if TYPE_CHECKING:
    pass

WarehouseConnection = Any


def connect(settings: Settings | None = None) -> WarehouseConnection:
    settings = settings or get_settings()
    if settings.backend == "bigquery":
        from operator_etl_gcp.load.bigquery import connect_bigquery

        return connect_bigquery(settings)
    from operator_etl.load.duckdb import connect as connect_duckdb

    return connect_duckdb(settings)
