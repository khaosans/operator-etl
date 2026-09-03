"""Cloud Run HTTP entrypoints — graph-runner and health checks."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from a2a.server import JsonRpcRequest, ensure_bearer_token, get_task_events, handle_jsonrpc
from operator_etl.config import Settings, get_settings, set_settings
from operator_etl_graph.graph import run_graph
from operator_etl_gcp.pubsub import decode_pubsub_push
from telemetry import initialize_telemetry

logger = logging.getLogger("operator_etl_gcp")
logging.basicConfig(level=logging.INFO, format="%(message)s")

app = FastAPI(title="Operator ETL Graph Runner", version="0.2.0")

_RATE_LIMIT = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
_rate_counts: dict[str, list[float]] = {}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next: Any) -> Response:
    import time

    if request.url.path == "/health":
        return await call_next(request)

    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = _rate_counts.setdefault(client, [])
    window[:] = [t for t in window if now - t < 60.0]
    if len(window) >= _RATE_LIMIT:
        return Response(content="Rate limit exceeded", status_code=429)
    window.append(now)
    return await call_next(request)


_MAX_BODY_BYTES = 10 * 1024 * 1024  # 10 MB


@app.middleware("http")
async def body_size_limit_middleware(request: Request, call_next: Any) -> Response:
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > _MAX_BODY_BYTES:
        return Response(content="Request body too large", status_code=413)
    return await call_next(request)


class RunRequest(BaseModel):
    source: str = Field(default="public_comments", max_length=128)
    pipeline: str = Field(default="public_comments", max_length=128)
    trigger: str = Field(default="http", max_length=64)


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
    initialize_telemetry()
    logger.info(json.dumps({"event": "graph_run_start", "source": body.source, "trigger": body.trigger}))
    try:
        result = run_graph(source=body.source, settings=settings)
    except Exception as exc:
        logger.error("graph_run_failed: %s: %s", type(exc).__name__, exc)
        raise HTTPException(status_code=500, detail="Internal pipeline error") from exc
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


@app.post("/a2a/v1/tasks", dependencies=[Depends(ensure_bearer_token)])
def a2a_tasks(body: JsonRpcRequest) -> dict[str, Any]:
    settings = _gov_settings("public_comments")
    set_settings(settings)
    initialize_telemetry()
    return handle_jsonrpc(body, settings)


@app.get("/a2a/v1/tasks/{task_id}/events", dependencies=[Depends(ensure_bearer_token)])
def a2a_task_events(task_id: str) -> StreamingResponse:
    return StreamingResponse(get_task_events(task_id), media_type="text/event-stream")


def main() -> None:
    import uvicorn

    # Cloud Run and local Docker publish :8080 on all interfaces.
    uvicorn.run("operator_etl_gcp.http.app:app", host="0.0.0.0", port=8080)  # nosec B104
