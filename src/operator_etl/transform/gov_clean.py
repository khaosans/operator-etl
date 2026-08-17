from __future__ import annotations

import json
from dataclasses import dataclass

import duckdb

from operator_etl.transform.gov_contracts import parse_payload, validate_comment

GOV_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS silver_comments (
    comment_id VARCHAR PRIMARY KEY,
    docket_id VARCHAR,
    agency VARCHAR,
    submitted_at TIMESTAMP,
    commenter_type VARCHAR,
    subject VARCHAR,
    body VARCHAR,
    foia_status VARCHAR,
    pii_detected BOOLEAN,
    _content_hash VARCHAR,
    _row_num INTEGER,
    _source VARCHAR,
    _ingested_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quarantine_comments (
    _content_hash VARCHAR,
    _row_num INTEGER,
    _source VARCHAR,
    _ingested_at TIMESTAMP,
    payload JSON,
    error VARCHAR,
    PRIMARY KEY (_content_hash, _row_num)
);

CREATE TABLE IF NOT EXISTS insights (
    insight_id VARCHAR PRIMARY KEY,
    run_id VARCHAR,
    docket_id VARCHAR,
    text VARCHAR,
    critic_passed BOOLEAN,
    created_at TIMESTAMP
);
"""


def init_gov_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(GOV_SCHEMA_SQL)


@dataclass(frozen=True)
class GovTransformStats:
    rows_in: int
    rows_silver: int
    rows_quarantined: int


def transform_comments_bronze(con: duckdb.DuckDBPyConnection) -> GovTransformStats:
    init_gov_schema(con)
    pending = con.execute(
        """
        SELECT b._content_hash, b._row_num, b._source, b._ingested_at, b.payload
        FROM bronze_raw b
        WHERE NOT EXISTS (
            SELECT 1 FROM silver_comments s
            WHERE s._content_hash = b._content_hash AND s._row_num = b._row_num
        )
        AND NOT EXISTS (
            SELECT 1 FROM quarantine_comments q
            WHERE q._content_hash = b._content_hash AND q._row_num = b._row_num
        )
        ORDER BY b._ingested_at, b._row_num
        """
    ).fetchall()

    existing = {r[0] for r in con.execute("SELECT comment_id FROM silver_comments").fetchall()}
    silver_rows = 0
    quarantined = 0

    for content_hash, row_num, source, ingested_at, payload in pending:
        data = parse_payload(payload)
        comment, error = validate_comment(data)
        if error:
            _quarantine(con, content_hash, row_num, source, ingested_at, data, error)
            quarantined += 1
            continue
        assert comment is not None
        if comment.comment_id in existing:
            _quarantine(con, content_hash, row_num, source, ingested_at, data, f"duplicate comment_id {comment.comment_id}")
            quarantined += 1
            continue
        ordered_at = comment.submitted_at.replace(tzinfo=None) if comment.submitted_at.tzinfo else comment.submitted_at
        con.execute(
            """
            INSERT INTO silver_comments
                (comment_id, docket_id, agency, submitted_at, commenter_type, subject, body,
                 foia_status, pii_detected, _content_hash, _row_num, _source, _ingested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                comment.comment_id,
                comment.docket_id,
                comment.agency,
                ordered_at,
                comment.commenter_type,
                comment.subject,
                comment.body,
                comment.foia_status,
                comment.pii_detected,
                content_hash,
                row_num,
                source,
                ingested_at,
            ],
        )
        existing.add(comment.comment_id)
        silver_rows += 1

    return GovTransformStats(rows_in=len(pending), rows_silver=silver_rows, rows_quarantined=quarantined)


def _quarantine(con, content_hash, row_num, source, ingested_at, payload, error):
    con.execute(
        """
        INSERT INTO quarantine_comments
            (_content_hash, _row_num, _source, _ingested_at, payload, error)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [content_hash, row_num, source, ingested_at, json.dumps(payload, ensure_ascii=False), error],
    )
