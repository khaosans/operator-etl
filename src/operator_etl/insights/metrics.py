from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime

import duckdb
import pandas as pd

from operator_etl.config import Settings, get_settings

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class QualityReport:
    passes: bool
    reasons: list[str]
    bronze_rows: int
    silver_rows: int
    quarantined_rows: int
    quarantine_rate: float
    last_ingest_at: datetime | None
    freshness_hours: float | None


def build_marts(con: duckdb.DuckDBPyConnection, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    sql_dir = settings.sql_dir
    if not sql_dir.exists():
        raise FileNotFoundError(f"SQL marts directory missing: {sql_dir}")
    for path in sorted(sql_dir.glob("*.sql")):
        con.execute(path.read_text(encoding="utf-8"))


def fetch_table(con: duckdb.DuckDBPyConnection, name: str) -> pd.DataFrame:
    """Load a warehouse table. ``name`` must be a SQL identifier (dashboard callers pass literals)."""
    if not _IDENT.fullmatch(name):
        raise ValueError(f"Refusing non-identifier table name: {name!r}")
    return con.execute(f'SELECT * FROM "{name}"').df()  # nosec B608


def quality_gate(con: duckdb.DuckDBPyConnection, settings: Settings | None = None) -> QualityReport:
    settings = settings or get_settings()
    quality = con.execute("SELECT * FROM gold_quality").fetchone()
    if quality is None:
        return QualityReport(
            passes=False,
            reasons=["gold_quality is empty — run etl run first"],
            bronze_rows=0,
            silver_rows=0,
            quarantined_rows=0,
            quarantine_rate=0.0,
            last_ingest_at=None,
            freshness_hours=None,
        )

    bronze_rows, silver_rows, quarantined_rows, last_ingest_at, quarantine_rate = quality
    reasons: list[str] = []
    freshness_hours: float | None = None
    if silver_rows == 0:
        reasons.append("no silver rows to report")
    if quarantine_rate is not None and quarantine_rate > settings.max_quarantine_rate:
        reasons.append(
            f"quarantine rate {quarantine_rate:.1%} exceeds {settings.max_quarantine_rate:.1%}"
        )
    if last_ingest_at is not None:
        stamp = (
            last_ingest_at.replace(tzinfo=UTC) if last_ingest_at.tzinfo is None else last_ingest_at
        )
        freshness_hours = (datetime.now(UTC) - stamp).total_seconds() / 3600
        if freshness_hours > settings.max_freshness_hours:
            reasons.append(
                f"last ingest was {freshness_hours:.1f}h ago (max {settings.max_freshness_hours:.0f}h)"
            )
    else:
        reasons.append("no ingest timestamp")

    return QualityReport(
        passes=not reasons,
        reasons=reasons,
        bronze_rows=int(bronze_rows or 0),
        silver_rows=int(silver_rows or 0),
        quarantined_rows=int(quarantined_rows or 0),
        quarantine_rate=float(quarantine_rate or 0),
        last_ingest_at=last_ingest_at,
        freshness_hours=freshness_hours,
    )


def render_insights(con: duckdb.DuckDBPyConnection, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    gate = quality_gate(con, settings)
    lines = [
        "Operator ETL insights",
        "",
        f"Quality: {'PASS' if gate.passes else 'BLOCKED'}",
        f"  bronze={gate.bronze_rows}  silver={gate.silver_rows}  quarantined={gate.quarantined_rows}  "
        f"quarantine_rate={gate.quarantine_rate:.1%}",
    ]
    if gate.freshness_hours is not None:
        lines.append(f"  freshness={gate.freshness_hours:.2f}h since last ingest")
    if gate.reasons:
        lines.append("  reasons:")
        for reason in gate.reasons:
            lines.append(f"    - {reason}")
    lines.append("")

    if not gate.passes:
        lines.append("KPIs withheld until the quality gate passes.")
        return "\n".join(lines)

    kpis = con.execute("SELECT * FROM gold_kpis").fetchone()
    if kpis:
        order_count, customer_count, revenue, avg_order, latest_order_at, freshness_at = kpis
        lines.extend(
            [
                "KPIs",
                f"  orders          {int(order_count)}",
                f"  customers       {int(customer_count)}",
                f"  revenue         {float(revenue):.2f}",
                f"  avg order       {float(avg_order):.2f}",
                f"  latest order    {latest_order_at}",
                f"  warehouse as of {freshness_at}",
                "",
            ]
        )

    volume = con.execute("SELECT * FROM gold_volume_daily ORDER BY order_date").fetchall()
    if volume:
        lines.append("Volume by day")
        for order_date, orders, revenue in volume:
            lines.append(f"  {order_date}  orders={int(orders)}  revenue={float(revenue):.2f}")
        lines.append("")

    top = con.execute("SELECT * FROM gold_top_skus").fetchall()
    if top:
        lines.append("Top SKUs")
        for sku, orders, revenue in top:
            lines.append(f"  {sku:16}  orders={int(orders)}  revenue={float(revenue):.2f}")

    return "\n".join(lines).rstrip() + "\n"
