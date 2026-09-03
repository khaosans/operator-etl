"""HTTP event adapters — Azure Event Grid handshake (no live cloud)."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from operator_etl_gcp.http.app import app


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
