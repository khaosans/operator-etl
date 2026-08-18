from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import END, StateGraph

from operator_etl.config import Settings, get_settings
from operator_etl_gcp.checkpoints import build_checkpointer
from operator_etl_graph.nodes import (
    build_gold_node,
    critic_node,
    ingest_node,
    insight_node,
    persist_node,
    pii_gate_node,
    quality_node,
    validate_load_node,
)
from operator_etl_graph.state import PipelineState, new_run_id


def route_pii(state: PipelineState) -> Literal["validate_load", "needs_human"]:
    if state.get("pii_needs_human"):
        return "needs_human"
    return "validate_load"


def route_quality(state: PipelineState) -> Literal["build_gold", "insight_blocked"]:
    if state.get("quality_passes"):
        return "build_gold"
    return "insight_blocked"


def route_critic(state: PipelineState) -> Literal["persist", "revise", "needs_human"]:
    if state.get("critic_passed"):
        return "persist"
    if state.get("_critic_retries", 0) < 2:
        return "revise"
    return "needs_human"


def insight_blocked_node(state: PipelineState) -> dict:
    return {"insight_draft": "KPIs withheld — quality gate failed.", "status": "needs_human"}


def needs_human_node(state: PipelineState) -> dict:
    return {"status": "needs_human"}


def build_graph(settings: Settings | None = None, *, checkpointer: Any | None = None):
    settings = settings or get_settings()
    graph = StateGraph(PipelineState)

    graph.add_node("ingest", lambda s: ingest_node(s, settings))
    graph.add_node("pii_gate", pii_gate_node)
    graph.add_node("validate_load", lambda s: validate_load_node(s, settings))
    graph.add_node("quality", lambda s: quality_node(s, settings))
    graph.add_node("build_gold", lambda s: build_gold_node(s, settings))
    graph.add_node("insight", lambda s: insight_node(s, settings))
    graph.add_node("insight_blocked", insight_blocked_node)
    graph.add_node("critic", critic_node)
    graph.add_node("persist", lambda s: persist_node(s, settings))
    graph.add_node("needs_human", needs_human_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "pii_gate")
    graph.add_conditional_edges("pii_gate", route_pii, {"validate_load": "validate_load", "needs_human": "needs_human"})
    graph.add_edge("validate_load", "quality")
    graph.add_conditional_edges("quality", route_quality, {"build_gold": "build_gold", "insight_blocked": "insight_blocked"})
    graph.add_edge("build_gold", "insight")
    graph.add_edge("insight_blocked", "critic")
    graph.add_edge("insight", "critic")
    graph.add_conditional_edges("critic", route_critic, {"persist": "persist", "revise": "insight", "needs_human": "needs_human"})
    graph.add_edge("persist", END)
    graph.add_edge("needs_human", END)

    if checkpointer is None:
        checkpointer = build_checkpointer(settings)
    return graph.compile(checkpointer=checkpointer)


def run_graph(source: str = "public_comments", settings: Settings | None = None) -> PipelineState:
    settings = settings or get_settings()
    run_id = new_run_id()
    app = build_graph(settings)
    config = {"configurable": {"thread_id": run_id}}
    initial: PipelineState = {
        "run_id": run_id,
        "source": source,
        "domain": settings.domain,
        "content_hash": "",
        "rows_in": 0,
        "rows_silver": 0,
        "rows_quarantined": 0,
        "pii_findings": [],
        "pii_needs_human": False,
        "quality_passes": False,
        "quality_reasons": [],
        "gold_metrics": {},
        "insight_draft": "",
        "critic_passed": False,
        "critic_violations": [],
        "insight_id": "",
        "status": "running",
        "errors": [],
        "_llm_calls": 0,
    }
    result = app.invoke(initial, config)
    return result
