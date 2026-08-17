from __future__ import annotations

import json

import httpx

from operator_etl.extract.http import extract_http
from operator_etl.pipeline import run_pipeline
from operator_etl.sources import get_source, list_sources


def test_source_registry_includes_http(settings) -> None:
    assert set(list_sources(settings)) == {"demo", "http", "inbox"}
    source = get_source("http", settings)
    assert source.kind == "http"
    assert source.url == "file:samples/http_orders.json"


def test_http_file_url_extracts_orders(settings) -> None:
    extracted = extract_http("file:samples/http_orders.json", root=settings.root)
    assert extracted.file_name == "http_orders.json"
    assert len(extracted.rows) == 3
    assert extracted.rows[0]["order_id"] == "ORD-2001"


def test_http_get_json_list(settings, monkeypatch) -> None:
    payload = [
        {
            "order_id": "ORD-3001",
            "customer_id": "CUS-20",
            "ordered_at": "2026-08-14T10:00:00",
            "amount": "11.00",
            "sku": "SKU-WIDGET",
            "status": "paid",
        }
    ]
    body = json.dumps(payload).encode()

    def fake_get(url, timeout, follow_redirects):
        request = httpx.Request("GET", url)
        return httpx.Response(200, content=body, request=request)

    monkeypatch.setattr("operator_etl.extract.http.httpx.get", fake_get)
    extracted = extract_http("https://example.test/orders")
    assert extracted.file_name == "orders"
    assert extracted.rows[0]["order_id"] == "ORD-3001"


def test_http_source_lands_in_warehouse(settings) -> None:
    result = run_pipeline("http", settings)
    assert result.status == "ok"
    assert result.rows_in == 3
    assert result.rows_silver == 3
    assert result.rows_quarantined == 0
    assert "orders          3" in (result.insights or "")
