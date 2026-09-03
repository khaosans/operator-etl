from __future__ import annotations

from fastapi.testclient import TestClient

from a2a.server import _TASKS, wait_for_task
from operator_etl_gcp.http import app as http_app
from operator_etl_gcp.http.app import app


def _headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-a2a-token"}


def _sample_records() -> list[dict[str, str | bool]]:
    return [
        {
            "comment_id": "A2A-001",
            "docket_id": "EPA-A2A-001",
            "agency": "EPA",
            "submitted_at": "2026-07-01T09:00:00",
            "commenter_type": "individual",
            "subject": "Air rule support",
            "body": "I support the rule. Contact me at jane.doe@example.com.",
            "pii_detected": True,
        },
        {
            "comment_id": "A2A-002",
            "docket_id": "EPA-A2A-001",
            "agency": "EPA",
            "submitted_at": "2026-07-01T10:00:00",
            "commenter_type": "organization",
            "subject": "Timeline concern",
            "body": "Please revise the timeline after more public review.",
            "pii_detected": False,
        },
    ]


def _prep_a2a(monkeypatch, gov_settings) -> None:
    monkeypatch.setenv("OPERATOR_ETL_A2A_BEARER_TOKEN", "test-a2a-token")
    # Tests poll status often; do not share the process-wide sliding window with other HTTP tests.
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10000")
    http_app._RATE_LIMIT = 10_000
    http_app._rate_counts.clear()
    monkeypatch.setattr("operator_etl_gcp.http.app._gov_settings", lambda pipeline: gov_settings)
    _TASKS.clear()


def _wait_for_completion(client: TestClient, task_id: str, *, timeout: float = 30.0) -> dict:
    """Wait on the worker's completion Event, then fetch status once via JSON-RPC.

    Prefer Event join over busy-polling: CI graph runs can exceed short poll budgets,
    and Event wait stays deterministic when the worker finishes early or late.
    """
    if not wait_for_task(task_id, timeout=timeout):
        raise AssertionError(f"task did not complete in {timeout}s")
    response = client.post(
        "/a2a/v1/tasks",
        headers=_headers(),
        json={"jsonrpc": "2.0", "id": "status-1", "method": "tasks.get_status", "params": {"task_id": task_id}},
    )
    assert response.status_code == 200, f"status poll HTTP {response.status_code}: {response.text}"
    payload = response.json()["result"]
    assert payload["state"] in {"completed", "failed"}, payload
    return payload


def test_a2a_task_create_status_and_sse(gov_settings, monkeypatch) -> None:
    _prep_a2a(monkeypatch, gov_settings)

    client = TestClient(app)
    create = client.post(
        "/a2a/v1/tasks",
        headers=_headers(),
        json={
            "jsonrpc": "2.0",
            "id": "create-1",
            "method": "tasks.create",
            "params": {
                "source_type": "public_comments",
                "docket_id": "EPA-A2A-001",
                "raw_records": _sample_records(),
            },
        },
    )
    assert create.status_code == 200
    created = create.json()["result"]
    assert created["state"] == "accepted"
    task_id = created["task_id"]

    status_payload = _wait_for_completion(client, task_id)
    assert status_payload["state"] == "completed", status_payload
    assert status_payload["artifacts"]["gold_metrics"]["comment_count"] == 2
    assert status_payload["artifacts"]["critic_passed"] is True
    assert "jane.doe@example.com" not in status_payload["artifacts"]["public_brief"]

    with client.stream("GET", f"/a2a/v1/tasks/{task_id}/events", headers=_headers()) as response:
        assert response.status_code == 200
        body = "".join(chunk for chunk in response.iter_text())
    assert "event: accepted" in body
    assert "event: completed" in body
    assert "jane.doe@example.com" not in body


def test_a2a_requires_bearer_and_jsonrpc_method(gov_settings, monkeypatch) -> None:
    _prep_a2a(monkeypatch, gov_settings)
    client = TestClient(app)

    unauthorized = client.post(
        "/a2a/v1/tasks",
        json={"jsonrpc": "2.0", "id": "bad-1", "method": "tasks.get_status", "params": {"task_id": "missing"}},
    )
    assert unauthorized.status_code == 401

    missing_method = client.post(
        "/a2a/v1/tasks",
        headers=_headers(),
        json={"jsonrpc": "2.0", "id": "bad-2", "method": "tasks.unknown", "params": {}},
    )
    assert missing_method.status_code == 200
    assert missing_method.json()["error"]["code"] == -32601
