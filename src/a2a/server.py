from __future__ import annotations

import json
import os
import queue
import threading
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Iterator

from fastapi import Header, HTTPException, status
from pydantic import BaseModel, Field

from operator_etl.config import Settings, set_settings
from operator_etl_graph.graph import run_graph
from operator_etl_mcp.tools import get_run_status
from operator_etl.load.connection import connect
from telemetry.tracer import span


class JsonRpcRequest(BaseModel):
    jsonrpc: str = Field(pattern=r"^2\.0$")
    method: str
    params: dict[str, Any] = Field(default_factory=dict)
    id: str | int | None = None


class CreateTaskParams(BaseModel):
    source_type: str = Field(default="public_comments", max_length=128)
    docket_id: str = Field(default="multi", max_length=256)
    raw_records: list[dict[str, Any]] = Field(max_length=10_000)


class GetStatusParams(BaseModel):
    task_id: str


@dataclass
class TaskRecord:
    task_id: str
    run_id: str
    source_type: str
    docket_id: str
    state: str = "accepted"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    artifacts: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    stream: queue.Queue[dict[str, Any]] = field(default_factory=queue.Queue)


_TASKS: dict[str, TaskRecord] = {}
_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _configured_bearer_token() -> str:
    token = os.getenv("OPERATOR_ETL_A2A_BEARER_TOKEN")
    if not token:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="A2A bearer token not configured")
    return token


def ensure_bearer_token(authorization: str | None = Header(default=None)) -> None:
    token = _configured_bearer_token()
    expected = f"Bearer {token}"
    if authorization != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def _publish(record: TaskRecord, event: str, payload: dict[str, Any]) -> None:
    body = {"event": event, "task_id": record.task_id, "run_id": record.run_id, "timestamp": _now(), **payload}
    record.updated_at = datetime.now(UTC)
    record.history.append(body)
    record.stream.put(body)


def _sanitize_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "gold_metrics": result.get("gold_metrics") or {},
        "public_brief": result.get("insight_draft", ""),
        "critic_passed": bool(result.get("critic_passed")),
        "status": result.get("status", "unknown"),
    }


def _run_task(record: TaskRecord, settings: Settings, params: CreateTaskParams) -> None:
    with span("operator_etl.a2a.task", attributes={"task_id": record.task_id, "run_id": record.run_id}):
        try:
            record.state = "working"
            _publish(record, "working", {"state": "working"})
            set_settings(settings)
            result = run_graph(
                source=params.source_type,
                settings=settings,
                run_id=record.run_id,
                initial_state={
                    "task_id": record.task_id,
                    "docket_id": params.docket_id,
                    "_input_records": params.raw_records,
                },
            )
            sanitized = _sanitize_result(result)
            record.artifacts = sanitized
            record.state = "completed" if result.get("status") == "complete" else "failed"
            record.error = "; ".join(result.get("errors", [])) or None
            _publish(
                record,
                "completed" if record.state == "completed" else "failed",
                {
                    "state": record.state,
                    "rows_in": int(result.get("rows_in") or 0),
                    "rows_silver": int(result.get("rows_silver") or 0),
                    "rows_quarantined": int(result.get("rows_quarantined") or 0),
                    "critic_passed": bool(result.get("critic_passed")),
                    "artifacts": sanitized,
                    "error": record.error,
                },
            )
        except Exception as exc:  # noqa: BLE001
            record.state = "failed"
            record.error = str(exc)
            _publish(record, "failed", {"state": "failed", "error": record.error})


def create_task_background(settings: Settings, params: CreateTaskParams) -> TaskRecord:
    task_id = str(uuid.uuid4())
    record = TaskRecord(
        task_id=task_id,
        run_id=str(uuid.uuid4()),
        source_type=params.source_type,
        docket_id=params.docket_id,
    )
    with _LOCK:
        _TASKS[task_id] = record
    _publish(record, "accepted", {"state": "accepted", "source_type": params.source_type})
    worker = threading.Thread(target=_run_task, args=(record, settings, params), daemon=True)
    worker.start()
    return record


def _jsonrpc_result(request_id: str | int | None, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _jsonrpc_error(request_id: str | int | None, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _read_run_status(settings: Settings, run_id: str) -> dict[str, Any]:
    try:
        con = connect(settings)
    except Exception:
        return {"error": "UNAVAILABLE"}
    try:
        return get_run_status(con, run_id)
    except Exception:
        return {"error": "UNAVAILABLE"}
    finally:
        con.close()


def task_status_payload(task_id: str, settings: Settings) -> dict[str, Any]:
    record = _TASKS.get(task_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    run_status: dict[str, Any] = {}
    if record.state in {"completed", "failed"}:
        run_status = _read_run_status(settings, record.run_id)
        if run_status.get("error") in {"NOT_FOUND", "UNAVAILABLE"}:
            run_status = {}
    return {
        "task_id": record.task_id,
        "run_id": record.run_id,
        "state": record.state,
        "docket_id": record.docket_id,
        "artifacts": record.artifacts,
        "error": record.error,
        "run_status": {
            "status": run_status.get("status"),
            "rows_in": run_status.get("rows_in"),
            "rows_silver": run_status.get("rows_silver"),
            "rows_quarantined": run_status.get("rows_quarantined"),
            "started_at": str(run_status.get("started_at")) if run_status.get("started_at") else None,
            "finished_at": str(run_status.get("finished_at")) if run_status.get("finished_at") else None,
        },
    }


def handle_jsonrpc(body: JsonRpcRequest, settings: Settings) -> dict[str, Any]:
    with span("operator_etl.a2a.jsonrpc", attributes={"method": body.method}):
        if body.method == "tasks.create":
            params = CreateTaskParams.model_validate(body.params)
            record = create_task_background(settings, params)
            return _jsonrpc_result(
                body.id,
                {
                    "task_id": record.task_id,
                    "run_id": record.run_id,
                    "state": "accepted",
                },
            )
        if body.method == "tasks.get_status":
            params = GetStatusParams.model_validate(body.params)
            return _jsonrpc_result(body.id, task_status_payload(params.task_id, settings))
        return _jsonrpc_error(body.id, -32601, f"Method not found: {body.method}")


def get_task_events(task_id: str) -> Iterator[str]:
    record = _TASKS.get(task_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    for event in record.history:
        yield _sse_payload(event)
    while True:
        item = record.stream.get()
        yield _sse_payload(item)
        if item["event"] in {"completed", "failed"}:
            break


def _sse_payload(event: dict[str, Any]) -> str:
    return f"event: {event['event']}\ndata: {json.dumps(event, default=str)}\n\n"
