"""HTTP event adapters — Azure Event Grid handshake (no live cloud)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from operator_etl_gcp.http.app import _safe_log_str, app


def test_safe_log_str_neutralizes_newlines_and_controls() -> None:
    assert "\n" not in _safe_log_str("evil\nINFO fake")
    assert "\r" not in _safe_log_str("evil\rinjected")
    assert _safe_log_str("ok-source") == "ok-source"
    assert _safe_log_str("a\x00b\x1fc") == "a_b_c"
    assert len(_safe_log_str("x" * 200)) == 128


def test_run_accepts_source_with_newline_without_crashing(gov_settings, monkeypatch) -> None:
    monkeypatch.setattr("operator_etl_gcp.http.app._gov_settings", lambda pipeline: gov_settings)
    monkeypatch.setattr(
        "operator_etl_gcp.http.app.run_graph",
        lambda *, source, settings: {
            "run_id": "run-safe-1",
            "status": "complete",
            "rows_in": 0,
            "rows_silver": 0,
            "rows_quarantined": 0,
            "critic_passed": True,
            "insight_draft": "",
            "errors": [],
        },
    )
    client = TestClient(app)
    response = client.post(
        "/run",
        json={"source": "public_comments\nfake", "pipeline": "public_comments", "trigger": "http"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "complete"


def test_azure_event_grid_subscription_validation() -> None:
    client = TestClient(app)
    body = [
        {
            "id": "validation-1",
            "eventType": "Microsoft.EventGrid.SubscriptionValidationEvent",
            "data": {"validationCode": "abc-validate-123"},
        }
    ]
    response = client.post("/events/azure", json=body)
    assert response.status_code == 200
    assert response.json() == {"validationResponse": "abc-validate-123"}


def test_azure_event_grid_blob_created_triggers_run(gov_settings, monkeypatch) -> None:
    monkeypatch.setattr("operator_etl_gcp.http.app._gov_settings", lambda pipeline: gov_settings)

    def fake_run_graph(*, source, settings):
        return {"status": "complete", "run_id": "run-azure-1"}

    monkeypatch.setattr("operator_etl_gcp.http.app.run_graph", fake_run_graph)
    client = TestClient(app)
    body = [
        {
            "id": "blob-1",
            "eventType": "Microsoft.Storage.BlobCreated",
            "data": {"url": "https://example.blob.core.windows.net/inbox/incoming/a.csv"},
        }
    ]
    response = client.post("/events/azure", json=body)
    assert response.status_code == 200
    assert response.json()["status"] == "complete"
    assert response.json()["run_id"] == "run-azure-1"
