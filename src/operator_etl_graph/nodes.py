from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from operator_etl.config import Settings, get_settings
from operator_etl.extract.csv import ExtractResult
from operator_etl_graph.critic import critic_check
from operator_etl_graph.insights import render_llm_insight, render_template_insight
from operator_etl_graph.state import PipelineState
from operator_etl_policy.budgets import RunBudget
from operator_etl.insights.gov_metrics import build_gov_marts, gov_quality_gate
from operator_etl.load.connection import connect
from operator_etl.load.duckdb import already_ingested, finish_run, load_bronze, start_run
from operator_etl.pipeline import collect_extracts
from operator_etl.sources import get_source
from operator_etl.transform.gov_clean import init_gov_schema, transform_comments_bronze
from operator_etl_mcp.tools import get_gold_metrics, run_allowlisted_sql
from operator_etl_policy.pii import extract_pii_values, scan_records
from operator_etl_policy.vault import PiiVault


def _vault_pii_from_records(records: list[dict[str, str]], text_columns: list[str]) -> int:
    """Encrypt raw PII into the local vault. Never returns plaintext."""
    vault = PiiVault()
    before = vault.count()
    for record in records:
        for col in text_columns:
            value = record.get(col) or ""
            if not value:
                continue
            for entity_type, raw in extract_pii_values(str(value)):
                vault.tokenize(raw, entity_type)
    return vault.count() - before


def _extract_from_state_records(state: PipelineState, source_name: str) -> ExtractResult | None:
    records = state.get("_input_records") or []
    if not records:
        return None
    payload = json.dumps(records, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return ExtractResult(
        file_name=f"{state.get('task_id', state['run_id'])}.jsonrpc.csv",
        content_hash=digest,
        rows=[{key: str(value) if value is not None else "" for key, value in row.items()} for row in records],
    )


def ingest_node(state: PipelineState, settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    source = get_source(state["source"], settings, settings.pipeline_name)
    con = connect(settings)
    init_gov_schema(con)
    start_run(con, state["run_id"], source.name)
    rows_in = 0
    records: list[dict[str, str]] = []
    content_hash = state.get("content_hash") or ""
    try:
        extracts = collect_extracts(source, settings)
        injected = _extract_from_state_records(state, source.name)
        if injected is not None:
            extracts = [injected]
        for extracted in extracts:
            content_hash = extracted.content_hash
            if already_ingested(con, extracted.content_hash):
                continue
            rows_in += load_bronze(con, source=source.name, extracted=extracted)
            records.extend(extracted.rows)
        finish_run(con, state["run_id"], status="running", rows_in=rows_in)
    finally:
        con.close()
    return {"rows_in": rows_in, "content_hash": content_hash, "_records": records}


def pii_gate_node(state: PipelineState) -> dict:
    records = state.get("_records") or []
    text_columns = ["body", "subject"]
    if not records:
        return {"pii_findings": [], "pii_needs_human": False, "vault_tokens_added": 0}
    result = scan_records(records, text_columns=text_columns)
    findings = [
        {"column": f.column, "entity_type": f.entity_type, "count": f.count, "max_confidence": f.max_confidence}
        for f in result.findings
    ]
    vaulted = _vault_pii_from_records(records, text_columns) if findings else 0
    if result.needs_human:
        return {
            "pii_findings": findings,
            "pii_needs_human": True,
            "vault_tokens_added": vaulted,
            "status": "needs_human",
            "errors": ["PII ambiguous — human review required"],
        }
    return {"pii_findings": findings, "pii_needs_human": False, "vault_tokens_added": vaulted}


def validate_load_node(state: PipelineState, settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    con = connect(settings)
    try:
        stats = transform_comments_bronze(con)
    finally:
        con.close()
    return {"rows_silver": stats.rows_silver, "rows_quarantined": stats.rows_quarantined}


def quality_node(state: PipelineState, settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    con = connect(settings)
    try:
        build_gov_marts(con, settings)
        gate = gov_quality_gate(con, settings)
        report = run_allowlisted_sql(con, "comment_quality", node="quality_agent", settings=settings)
    finally:
        con.close()
    if not gate.passes:
        return {
            "quality_passes": False,
            "quality_reasons": gate.reasons,
            "_quality_report": report,
        }
    return {"quality_passes": True, "quality_reasons": [], "_quality_report": report}


def build_gold_node(state: PipelineState, settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    con = connect(settings)
    try:
        metrics = get_gold_metrics(con, domain=state.get("domain", "gov"))
    finally:
        con.close()
    serializable = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in metrics.items()}
    return {"gold_metrics": serializable}


def insight_node(state: PipelineState, settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    m = state.get("gold_metrics") or {}
    if not state.get("quality_passes"):
        return {"insight_draft": "Insights withheld — quality gate did not pass.", "status": "needs_human"}
    if settings.insight_backend != "llm":
        return {"insight_draft": render_template_insight(m)}
    budget = RunBudget(
        max_llm_calls=settings.max_llm_calls,
        llm_calls=int(state.get("_llm_calls") or 0),
    )
    draft, note = render_llm_insight(m, settings, budget)
    result: dict = {"insight_draft": draft, "_llm_calls": budget.llm_calls}
    if note:
        result["errors"] = [note]
    return result


def critic_node(state: PipelineState) -> dict:
    passed, violations = critic_check(state.get("insight_draft", ""), state.get("gold_metrics") or {})
    if passed:
        return {"critic_passed": True, "critic_violations": []}
    retries = state.get("_critic_retries", 0)
    if not passed and retries < 2:
        return {"critic_passed": False, "critic_violations": violations, "_critic_retries": retries + 1}
    return {
        "critic_passed": False,
        "critic_violations": violations,
        "status": "needs_human",
        "errors": [f"Critic failed: uncited numbers {violations}"],
    }


def persist_node(state: PipelineState, settings: Settings | None = None) -> dict:
    if not state.get("quality_passes"):
        return {"status": "needs_human"}
    if not state.get("critic_passed"):
        return {"status": "needs_human"}
    settings = settings or get_settings()
    import uuid

    insight_id = str(uuid.uuid4())
    con = connect(settings)
    try:
        init_gov_schema(con)
        con.execute(
            """
            INSERT INTO insights (insight_id, run_id, docket_id, text, critic_passed, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                insight_id,
                state["run_id"],
                "multi",
                state.get("insight_draft", ""),
                True,
                datetime.now(UTC).replace(tzinfo=None),
            ],
        )
        finish_run(
            con,
            state["run_id"],
            status="ok",
            rows_in=state.get("rows_in", 0),
            rows_silver=state.get("rows_silver", 0),
            rows_quarantined=state.get("rows_quarantined", 0),
        )
    finally:
        con.close()
    return {
        "insight_id": insight_id,
        "status": "complete",
        "artifacts": {
            "gold_metrics": state.get("gold_metrics") or {},
            "public_brief": state.get("insight_draft", ""),
        },
    }


def needs_human_node(state: PipelineState, settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    con = connect(settings)
    try:
        finish_run(
            con,
            state["run_id"],
            status="needs_human",
            rows_in=state.get("rows_in", 0),
            rows_silver=state.get("rows_silver", 0),
            rows_quarantined=state.get("rows_quarantined", 0),
            error="; ".join(state.get("errors", [])) or None,
        )
    finally:
        con.close()
    return {"status": "needs_human"}
