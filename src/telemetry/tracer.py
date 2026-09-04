from __future__ import annotations

from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from telemetry.config import get_runtime, get_tracer, safe_attributes

SAFE_STATE_KEYS = {
    "run_id",
    "source",
    "domain",
    "status",
    "rows_in",
    "rows_silver",
    "rows_quarantined",
    "pii_needs_human",
    "quality_passes",
    "critic_passed",
    "_critic_retries",
    "_llm_calls",
}


def state_attributes(state: dict[str, Any] | None) -> dict[str, Any]:
    if not state:
        return {}
    return safe_attributes({key: state.get(key) for key in SAFE_STATE_KEYS if key in state})


@contextmanager
def span(name: str, *, attributes: dict[str, Any] | None = None):
    tracer = get_tracer("operator-etl")
    with tracer.start_as_current_span(name, attributes=safe_attributes(attributes)) as current:
        yield current


def _record_node_metrics(name: str, result: dict[str, Any], base: dict[str, Any]) -> None:
    runtime = get_runtime()
    counters = runtime.counters
    shared = safe_attributes(base)
    if name == "ingest":
        rows_in = int(result.get("rows_in") or 0)
        if rows_in:
            counters.rows_processed.add(rows_in, {**shared, "stage": "bronze"})
    if name == "validate_load":
        rows_silver = int(result.get("rows_silver") or 0)
        rows_quarantined = int(result.get("rows_quarantined") or 0)
        if rows_silver:
            counters.rows_processed.add(rows_silver, {**shared, "stage": "silver"})
        if rows_quarantined:
            counters.rows_quarantined.add(
                rows_quarantined, {**shared, "reason": "validation_failed"}
            )
    if name == "build_gold":
        metrics = result.get("gold_metrics") or {}
        gold_rows = int(metrics.get("comment_count") or metrics.get("order_count") or 0)
        if gold_rows:
            counters.rows_processed.add(gold_rows, {**shared, "stage": "gold"})
    if name == "pii_gate":
        for finding in result.get("pii_findings") or []:
            count = int(finding.get("count") or 0)
            if count:
                counters.pii_detections.add(
                    count,
                    {**shared, "entity_type": str(finding.get("entity_type", "unknown"))},
                )
    if name == "critic":
        if "critic_passed" in result:
            counters.critic_evaluations.add(
                1,
                {**shared, "outcome": "passed" if result.get("critic_passed") else "failed"},
            )


def instrument_langgraph_node(
    name: str, fn: Callable[[dict[str, Any]], dict[str, Any]]
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def wrapped(state: dict[str, Any]) -> dict[str, Any]:
        before = state_attributes(state)
        with span(f"operator_etl.node.{name}", attributes={**before, "node.name": name}) as current:
            result = fn(state)
            current.set_attributes(safe_attributes(state_attributes(result)))
            _record_node_metrics(name, result, before)
            return result

    return wrapped


def record_branch_decision(route_name: str, decision: str, state: dict[str, Any]) -> None:
    with span(
        f"operator_etl.route.{route_name}",
        attributes={
            **state_attributes(state),
            "route.name": route_name,
            "route.decision": decision,
        },
    ):
        return


def record_run_result(result: dict[str, Any]) -> None:
    runtime = get_runtime()
    attrs = state_attributes(result)
    if "critic_passed" in result:
        runtime.counters.critic_evaluations.add(
            1,
            {**attrs, "outcome": "passed" if result.get("critic_passed") else "failed"},
        )


def record_run_exception(exc: Exception, state: dict[str, Any] | None = None) -> None:
    with span(
        "operator_etl.graph.error",
        attributes={**state_attributes(state or {}), "error.type": exc.__class__.__name__},
    ) as current:
        current.record_exception(exc)
