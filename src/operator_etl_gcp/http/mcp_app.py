"""HTTP MCP tool surface for Cloud Run (REST wrapper over allowlisted tools)."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from a2a.agent_card import build_agent_card
from operator_etl.config import Settings, get_settings, set_settings
from operator_etl.load.connection import connect
from operator_etl_mcp.tools import ToolDenied, get_gold_metrics, get_run_status, run_allowlisted_sql

app = FastAPI(title="Operator ETL MCP (HTTP)", version="0.2.0")


class QualitySqlRequest(BaseModel):
    query_id: str
    node: str = "quality_agent"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "operator-etl-mcp"}


@app.get("/.well-known/agent-card.json")
def agent_card(request: Request) -> dict:
    return build_agent_card(str(request.base_url).rstrip("/"))


@app.get("/tools/gold-metrics")
def gold_metrics(domain: str = "gov") -> dict:
    settings = get_settings()
    con = connect(settings)
    try:
        return get_gold_metrics(con, domain=domain)
    finally:
        con.close()


@app.post("/tools/quality-sql")
def quality_sql(body: QualitySqlRequest) -> dict:
    settings = get_settings()
    con = connect(settings)
    try:
        return run_allowlisted_sql(con, body.query_id, node=body.node, settings=settings)
    except ToolDenied as exc:
        raise HTTPException(
            status_code=403, detail={"error": "TOOL_DENIED", "reason": str(exc)}
        ) from exc
    finally:
        con.close()


@app.get("/tools/run-status/{run_id}")
def run_status(run_id: str) -> dict:
    settings = get_settings()
    con = connect(settings)
    try:
        result = get_run_status(con, run_id)
        if result.get("error") == "NOT_FOUND":
            raise HTTPException(status_code=404, detail="NOT_FOUND")
        return result
    finally:
        con.close()


def bootstrap() -> None:
    base = get_settings()
    set_settings(
        Settings(
            root=base.root,
            backend=base.backend,
            gcp_project=base.gcp_project,
            bq_dataset_gold=base.bq_dataset_gold,
            bq_dataset_bronze=base.bq_dataset_bronze,
            bq_dataset_silver=base.bq_dataset_silver,
            bq_dataset_quarantine=base.bq_dataset_quarantine,
            pipeline_name="public_comments",
            domain="gov",
        )
    )
