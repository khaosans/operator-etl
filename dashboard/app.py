from __future__ import annotations

import streamlit as st
import pandas as pd

from operator_etl.config import Settings, get_settings
from operator_etl.insights.gov_metrics import gov_quality_gate
from operator_etl.insights.metrics import fetch_table, quality_gate
from operator_etl.load.duckdb import connect

st.set_page_config(page_title="Operator ETL", layout="wide")
st.title("Operator ETL")
st.caption("Intake → warehouse → insights. KPIs hide when the quality gate fails.")

tab_gov, tab_orders, tab_observability = st.tabs(["Gov / FOIA", "Orders demo", "Observability & Spans"])


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

        st.subheader("HITL officer sign-off")
        st.caption("Approve/reject writes an audit row only — agents never auto-publish FOIA.")
        from operator_etl_policy.hitl import HitlStore

        store = HitlStore(settings=settings)
        needs = []
        if runs is not None and not runs.empty and "status" in runs.columns:
            needs = runs.loc[runs["status"] == "needs_human", "run_id"].astype(str).tolist()
        run_choices = needs or (runs["run_id"].astype(str).tolist() if runs is not None and not runs.empty else [])
        if run_choices:
            selected = st.selectbox("Run needing review", run_choices)
            officer = st.text_input("Officer id", value="foia-officer")
            reason = st.text_input("Reason", value="")
            c_approve, c_reject = st.columns(2)
            if c_approve.button("Approve", type="primary"):
                store.decide(selected, "approve", officer=officer, reason=reason or "approved")
                st.success(f"Approved {selected} (audit only)")
            if c_reject.button("Reject"):
                store.decide(selected, "reject", officer=officer, reason=reason or "rejected")
                st.warning(f"Rejected {selected}")
        decisions = store.list_decisions()
        if decisions:
            st.dataframe(
                [
                    {
                        "run_id": d.run_id,
                        "decision": d.decision,
                        "officer": d.officer,
                        "reason": d.reason,
                        "decided_at": d.decided_at,
                    }
                    for d in decisions
                ],
                hide_index=True,
            )
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


def render_observability(settings: Settings) -> None:
    if not _warehouse_exists(settings):
        st.warning("No warehouse yet. Run the FOIA graph first to populate `pipeline_runs`.")
        return

    con = connect(settings)
    try:
        runs = fetch_table(con, "pipeline_runs")
        if runs.empty:
            st.info("No pipeline runs yet.")
            return

        runs["started_at"] = pd.to_datetime(runs["started_at"], errors="coerce")
        runs["finished_at"] = pd.to_datetime(runs["finished_at"], errors="coerce")
        runs["duration_seconds"] = (runs["finished_at"] - runs["started_at"]).dt.total_seconds()
        runs["quarantine_pct"] = runs.apply(
            lambda row: float(row["rows_quarantined"] or 0) / float(row["rows_in"] or 1) if row["rows_in"] else 0.0,
            axis=1,
        )

        recent = runs.sort_values("started_at", ascending=False).head(10)
        completed = runs[runs["status"] == "ok"]
        blocked = runs[runs["status"].isin(["needs_human", "failed", "error"])]

        c1, c2, c3 = st.columns(3)
        c1.metric("Recent avg duration", f"{recent['duration_seconds'].dropna().mean() or 0:.2f}s")
        c2.metric("Avg quarantine rate", f"{recent['quarantine_pct'].mean() or 0:.1%}")
        total_evals = len(completed) + len(blocked)
        pass_rate = (len(completed) / total_evals) if total_evals else 0.0
        c3.metric("Critic pass rate", f"{pass_rate:.1%}")

        if not recent["duration_seconds"].dropna().empty:
            duration_chart = recent[["run_id", "duration_seconds"]].set_index("run_id")
            st.subheader("Recent run durations")
            st.bar_chart(duration_chart)

        st.subheader("Recent execution states")
        st.dataframe(
            recent[
                [
                    "run_id",
                    "source",
                    "status",
                    "rows_in",
                    "rows_silver",
                    "rows_quarantined",
                    "quarantine_pct",
                    "duration_seconds",
                    "started_at",
                    "finished_at",
                ]
            ],
            hide_index=True,
        )

        st.caption("Telemetry spans are metadata-only: run IDs, counts, durations, and outcomes. Raw PII and payloads are never shown.")
    finally:
        con.close()


def main() -> None:
    base = get_settings()
    with tab_gov:
        gov_settings = Settings(
            root=base.root,
            warehouse=base.warehouse_path,
            pipeline_name="public_comments",
            domain="gov",
        )
        render_gov(gov_settings)
    with tab_orders:
        orders_settings = Settings(
            root=base.root,
            warehouse=base.orders_warehouse_path,
            pipeline_name="demo",
            domain="orders",
        )
        render_orders(orders_settings)
    with tab_observability:
        gov_settings = Settings(
            root=base.root,
            warehouse=base.warehouse_path,
            pipeline_name="public_comments",
            domain="gov",
        )
        render_observability(gov_settings)


main()
