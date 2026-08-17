"""Cloud Run HTTP entrypoints — graph-runner and health checks."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from operator_etl.config import Settings, get_settings, set_settings
from operator_etl_graph.graph import run_graph
from operator_etl_gcp.pubsub import decode_pubsub_push

logger = logging.getLogger("operator_etl_gcp")
logging.basicConfig(level=logging.INFO, format="%(message)s")

app = FastAPI(title="Operator ETL Graph Runner", version="0.2.0")


class RunRequest(BaseModel):
    source: str = "public_comments"
    pipeline: str = "public_comments"
    trigger: str = "http"


def _gov_settings(pipeline: str) -> Settings:
    base = get_settings()
    return Settings(
        root=base.root,
        backend=base.backend,
        checkpoint_backend=base.checkpoint_backend,
        checkpoint_database_url=base.checkpoint_database_url,
        gcp_project=base.gcp_project,
        gcs_inbox_bucket=base.gcs_inbox_bucket,
        bq_dataset_bronze=base.bq_dataset_bronze,
        bq_dataset_silver=base.bq_dataset_silver,
        bq_dataset_quarantine=base.bq_dataset_quarantine,
        bq_dataset_gold=base.bq_dataset_gold,
        gcp_region=base.gcp_region,
        pipeline_name=pipeline,
        domain="gov",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "graph-runner"}


@app.post("/run")
def run_pipeline(body: RunRequest) -> dict[str, Any]:
    settings = _gov_settings(body.pipeline)
    set_settings(settings)
    logger.info(json.dumps({"event": "graph_run_start", "source": body.source, "trigger": body.trigger}))
    try:
        result = run_graph(source=body.source, settings=settings)
    except Exception as exc:
        logger.exception("graph_run_failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    logger.info(json.dumps({"event": "graph_run_complete", "run_id": result.get("run_id"), "status": result.get("status")}))
    return {
        "run_id": result.get("run_id"),
        "status": result.get("status"),
        "rows_in": result.get("rows_in"),
        "rows_silver": result.get("rows_silver"),
        "rows_quarantined": result.get("rows_quarantined"),
        "critic_passed": result.get("critic_passed"),
        "insight_draft": result.get("insight_draft"),
        "errors": result.get("errors", []),
    }


@app.post("/pubsub/push")
async def pubsub_push(request: Request) -> dict[str, str]:
    """Pub/Sub push handler for GCS OBJECT_FINALIZE → graph run."""
    body = await request.json()
    try:
        event = decode_pubsub_push(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not event.is_csv:
        return {"status": "skipped", "reason": "not a csv object"}
    settings = _gov_settings("public_comments")
    set_settings(settings)
    logger.info(json.dumps({"event": "gcs_ingest", "bucket": event.bucket, "object": event.object_name}))
    # GCS-triggered runs use comment_inbox source; graph ingest picks up staged file via gcs path
    result = run_graph(source="gcs_inbox", settings=settings)
    return {"status": result.get("status", "unknown"), "run_id": result.get("run_id", "")}


def main() -> None:
    import uvicorn

    uvicorn.run("operator_etl_gcp.http.app:app", host="0.0.0.0", port=8080)
