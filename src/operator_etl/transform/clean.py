from __future__ import annotations

import json
from dataclasses import dataclass

import duckdb

from operator_etl.transform.contracts import parse_payload, validate_order


@dataclass(frozen=True)
class TransformStats:
    rows_in: int
    rows_silver: int
    rows_quarantined: int


def transform_bronze(con: duckdb.DuckDBPyConnection) -> TransformStats:
    pending = con.execute(
        """
        SELECT b._content_hash, b._row_num, b._source, b._ingested_at, b.payload
        FROM bronze_raw b
        WHERE NOT EXISTS (
            SELECT 1 FROM silver_orders s
            WHERE s._content_hash = b._content_hash
              AND s._row_num = b._row_num
        )
        AND NOT EXISTS (
            SELECT 1 FROM quarantine_orders q
            WHERE q._content_hash = b._content_hash
              AND q._row_num = b._row_num
        )
        ORDER BY b._ingested_at, b._row_num
        """
    ).fetchall()

    existing_ids = {row[0] for row in con.execute("SELECT order_id FROM silver_orders").fetchall()}
    silver_rows = 0
    quarantined = 0

    for content_hash, row_num, source, ingested_at, payload in pending:
        data = parse_payload(payload)
        order, error = validate_order(data)
        if error:
            _quarantine(con, content_hash, row_num, source, ingested_at, data, error)
            quarantined += 1
            continue
        assert order is not None
        if order.order_id in existing_ids:
            _quarantine(
                con,
                content_hash,
                row_num,
                source,
                ingested_at,
                data,
                f"duplicate order_id {order.order_id}",
            )
            quarantined += 1
            continue
        ordered_at = order.ordered_at.replace(tzinfo=None) if order.ordered_at.tzinfo else order.ordered_at
        con.execute(
            """
            INSERT INTO silver_orders
                (order_id, customer_id, ordered_at, amount, sku, status, _content_hash, _row_num, _source, _ingested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                order.order_id,
                order.customer_id,
                ordered_at,
                order.amount,
                order.sku,
                order.status,
                content_hash,
                row_num,
                source,
                ingested_at,
            ],
        )
        existing_ids.add(order.order_id)
        silver_rows += 1

    return TransformStats(rows_in=len(pending), rows_silver=silver_rows, rows_quarantined=quarantined)


def _quarantine(
    con: duckdb.DuckDBPyConnection,
    content_hash: str,
    row_num: int,
    source: str,
    ingested_at,
    payload: dict,
    error: str,
) -> None:
    con.execute(
        """
        INSERT INTO quarantine_orders
            (_content_hash, _row_num, _source, _ingested_at, payload, error)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [content_hash, row_num, source, ingested_at, json.dumps(payload, ensure_ascii=False), error],
    )
