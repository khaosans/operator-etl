from __future__ import annotations

import streamlit as st

from operator_etl.config import get_settings
from operator_etl.insights.metrics import fetch_table, quality_gate
from operator_etl.load.duckdb import connect

st.set_page_config(page_title="Operator ETL", layout="wide")
st.title("Operator ETL")
st.caption("Intake → warehouse → insights. KPIs hide when the quality gate fails.")


def main() -> None:
    settings = get_settings()
    if not settings.warehouse_path.exists():
        st.warning("No warehouse yet. From the repo root run `uv run etl run --source demo`.")
        return

    con = connect(settings)
    try:
        _render(con, settings)
    finally:
        con.close()


def _render(con, settings) -> None:
    gate = quality_gate(con, settings)
    quality_col, status_col = st.columns(2)
    with quality_col:
        st.metric("Bronze rows", gate.bronze_rows)
        st.metric("Silver rows", gate.silver_rows)
        st.metric("Quarantined", gate.quarantined_rows)
    with status_col:
        st.metric("Quarantine rate", f"{gate.quarantine_rate:.1%}")
        freshness = f"{gate.freshness_hours:.2f}h" if gate.freshness_hours is not None else "n/a"
        st.metric("Freshness", freshness)
        st.metric("Quality gate", "PASS" if gate.passes else "BLOCKED")

    if gate.reasons:
        st.error("Quality gate: " + "; ".join(gate.reasons))

    st.subheader("Data quality")
    try:
        st.dataframe(fetch_table(con, "gold_quality"), hide_index=True)
    except Exception:
        st.info("Run `etl run` to build gold_quality.")
        return

    try:
        quarantined = fetch_table(con, "quarantine_orders")
    except Exception:
        quarantined = None
    if quarantined is not None and not quarantined.empty:
        with st.expander(f"Quarantine ({len(quarantined)} rows)"):
            st.dataframe(quarantined, hide_index=True)

    if not gate.passes:
        st.info("KPI cards, volume, and SKU breakdown stay hidden until the gate passes.")
        return

    kpis = fetch_table(con, "gold_kpis")
    if kpis.empty:
        st.info("No KPIs yet.")
        return

    row = kpis.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Orders", int(row["order_count"]))
    c2.metric("Customers", int(row["customer_count"]))
    c3.metric("Revenue", f"{float(row['revenue']):.2f}")
    c4.metric("Avg order", f"{float(row['avg_order']):.2f}")

    volume = fetch_table(con, "gold_volume_daily")
    st.subheader("Volume over time")
    if volume.empty:
        st.info("No daily volume.")
    else:
        chart = volume.rename(columns={"order_date": "index"}).set_index("index")[["orders", "revenue"]]
        st.line_chart(chart)

    top = fetch_table(con, "gold_top_skus")
    st.subheader("Top SKUs")
    if top.empty:
        st.info("No SKU breakdown.")
    else:
        st.bar_chart(top.set_index("sku")["revenue"])
        st.dataframe(top, hide_index=True)

    runs = fetch_table(con, "pipeline_runs")
    st.subheader("Pipeline runs")
    st.dataframe(runs.sort_values("started_at", ascending=False), hide_index=True)


main()
