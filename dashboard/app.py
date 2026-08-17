from __future__ import annotations

import streamlit as st

from operator_etl.config import Settings, get_settings
from operator_etl.insights.gov_metrics import gov_quality_gate
from operator_etl.insights.metrics import fetch_table, quality_gate
from operator_etl.load.duckdb import connect

st.set_page_config(page_title="Operator ETL", layout="wide")
st.title("Operator ETL")
st.caption("Intake → warehouse → insights. KPIs hide when the quality gate fails.")

tab_gov, tab_orders = st.tabs(["Gov / FOIA", "Orders demo"])


def _warehouse_exists(settings: Settings) -> bool:
    return settings.warehouse_path.exists()


def render_gov(settings: Settings) -> None:
    if not _warehouse_exists(settings):
        st.warning(
            "No gov warehouse yet. Run:\n\n"
            "`./scripts/demo_mvp.sh` or `OPERATOR_ETL_WAREHOUSE=.tmp/mvp-demo/operator.duckdb "
            "OPERATOR_ETL_PIPELINE_NAME=public_comments OPERATOR_ETL_DOMAIN=gov uv run etl-graph`"
        )
        return

    con = connect(settings)
    try:
        gate = gov_quality_gate(con, settings)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Bronze rows", gate.bronze_rows)
        c2.metric("Silver comments", gate.silver_rows)
        c3.metric("Quarantined", gate.quarantined_rows)
        c4.metric("Gate", "PASS" if gate.passes else "BLOCKED")

        if gate.reasons:
            st.error("Quality gate: " + "; ".join(gate.reasons))

        try:
            kpis = fetch_table(con, "gold_comment_kpis")
            if not kpis.empty:
                row = kpis.iloc[0]
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Comments", int(row.get("comment_count", 0)))
                k2.metric("Dockets", int(row.get("docket_count", 0)))
                k3.metric("PII flagged", int(row.get("pii_flagged_count", 0)))
                k4.metric("PII rate", f"{float(row.get('pii_rate', 0)):.1%}")
        except Exception:
            st.info("Run FOIA graph to build gold_comment_kpis.")

        try:
            by_agency = fetch_table(con, "gold_comments_by_agency")
            if not by_agency.empty:
                st.subheader("Comments by agency")
                st.dataframe(by_agency, hide_index=True)
        except Exception:
            pass

        try:
            quarantine = fetch_table(con, "quarantine_comments")
            if quarantine is not None and not quarantine.empty:
                with st.expander(f"Quarantine ({len(quarantine)} rows)"):
                    st.dataframe(quarantine, hide_index=True)
        except Exception:
            pass

        try:
            insights = fetch_table(con, "insights")
            if insights is not None and not insights.empty:
                st.subheader("Latest insight")
                latest = insights.sort_values("created_at", ascending=False).iloc[0]
                st.write(latest.get("text", ""))
        except Exception:
            pass

        runs = fetch_table(con, "pipeline_runs")
        st.subheader("Pipeline runs")
        st.dataframe(runs.sort_values("started_at", ascending=False), hide_index=True)
    finally:
        con.close()


def render_orders(settings: Settings) -> None:
    if not _warehouse_exists(settings):
        st.warning("No warehouse yet. Run `uv run etl run --source demo`.")
        return

    con = connect(settings)
    try:
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

        if not gate.passes:
            st.info("KPI cards hidden until gate passes.")
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
        if not volume.empty:
            chart = volume.rename(columns={"order_date": "index"}).set_index("index")[["orders", "revenue"]]
            st.line_chart(chart)

        top = fetch_table(con, "gold_top_skus")
        st.subheader("Top SKUs")
        if not top.empty:
            st.bar_chart(top.set_index("sku")["revenue"])
            st.dataframe(top, hide_index=True)
    finally:
        con.close()


def main() -> None:
    base = get_settings()
    with tab_gov:
        gov_settings = Settings(
            root=base.root,
            warehouse=base.warehouse,
            pipeline_name="public_comments",
            domain="gov",
        )
        render_gov(gov_settings)
    with tab_orders:
        orders_settings = Settings(
            root=base.root,
            warehouse=base.warehouse,
            pipeline_name="demo",
            domain="orders",
        )
        render_orders(orders_settings)


main()
