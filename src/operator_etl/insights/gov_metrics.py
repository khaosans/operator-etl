from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import duckdb

from operator_etl.config import Settings, get_settings


@dataclass(frozen=True)
class GovQualityReport:
    passes: bool
    reasons: list[str]
    bronze_rows: int
    silver_rows: int
    quarantined_rows: int
    quarantine_rate: float
    last_ingest_at: datetime | None
    freshness_hours: float | None


def build_gov_marts(con: duckdb.DuckDBPyConnection, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    sql_dir = settings.sql_dir
    for path in sorted(sql_dir.glob("*.sql")):
        con.execute(path.read_text(encoding="utf-8"))


def gov_quality_gate(con: duckdb.DuckDBPyConnection, settings: Settings | None = None) -> GovQualityReport:
    settings = settings or get_settings()
    row = con.execute("SELECT * FROM gold_comment_quality").fetchone()
    if row is None:
        return GovQualityReport(False, ["gold_comment_quality empty"], 0, 0, 0, 0.0, None, None)
    bronze, silver, quarantined, last_ingest, rate = row
    reasons: list[str] = []
    freshness: float | None = None
    if silver == 0:
        reasons.append("no silver comments")
    if rate and rate > settings.max_quarantine_rate:
        reasons.append(f"quarantine rate {rate:.1%} exceeds {settings.max_quarantine_rate:.1%}")
    if last_ingest_at := last_ingest:
        stamp = last_ingest_at.replace(tzinfo=UTC) if last_ingest_at.tzinfo is None else last_ingest_at
        freshness = (datetime.now(UTC) - stamp).total_seconds() / 3600
        if freshness > settings.max_freshness_hours:
            reasons.append(f"stale ingest ({freshness:.1f}h)")
    return GovQualityReport(
        passes=not reasons,
        reasons=reasons,
        bronze_rows=int(bronze or 0),
        silver_rows=int(silver or 0),
        quarantined_rows=int(quarantined or 0),
        quarantine_rate=float(rate or 0),
        last_ingest_at=last_ingest,
        freshness_hours=freshness,
    )
