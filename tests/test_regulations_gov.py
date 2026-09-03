"""Regulations.gov adapter — offline sample fallback."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from operator_etl.config import Settings, set_settings
from operator_etl.extract.regulations_gov import fetch_comments_for_docket, load_sample_fallback, rows_to_extract
from operator_etl.pipeline import collect_extracts
from operator_etl.sources import get_source


def test_rows_to_extract_hashes_deterministic() -> None:
    rows = [
        {
            "comment_id": "c1",
            "docket_id": "EPA-HQ-OAR-2024-0001",
            "agency": "EPA",
            "submitted_at": "2024-01-01",
            "commenter_type": "public",
            "subject": "hi",
            "body": "body",
            "foia_status": "pending_review",
        }
    ]
    a = rows_to_extract(rows, file_name="x.csv")
    b = rows_to_extract(rows, file_name="x.csv")
    assert a.content_hash == b.content_hash
    assert a.rows == rows


def test_fetch_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REGULATIONS_GOV_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="REGULATIONS_GOV_API_KEY"):
        fetch_comments_for_docket("EPA-HQ-OAR-2024-0001")


def test_fetch_parses_api_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REGULATIONS_GOV_API_KEY", "test-key")
    client = MagicMock()
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {
        "data": [
            {
                "id": "DOC-1",
                "attributes": {
                    "agencyId": "EPA",
                    "postedDate": "2024-06-01",
                    "title": "Comment",
                    "comment": "Please consider air quality.",
                    "submitterType": "individual",
                },
            }
        ],
        "meta": {"hasNextPage": False},
    }
    client.get.return_value = resp
    rows = fetch_comments_for_docket("EPA-HQ-OAR-2024-0001", client=client)
    assert rows[0]["comment_id"] == "DOC-1"
    assert rows[0]["agency"] == "EPA"
    assert "air quality" in rows[0]["body"]


def test_collect_extracts_falls_back_to_sample(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REGULATIONS_GOV_API_KEY", raising=False)
    root = Path(__file__).resolve().parents[1]
    settings = Settings(
        root=root,
        warehouse=tmp_path / "operator.duckdb",
        domain="gov",
        pipeline_name="public_comments",
    )
    set_settings(settings)
    source = get_source("regulations_gov", settings, "public_comments")
    extracts = collect_extracts(source, settings)
    assert len(extracts) == 1
    assert extracts[0].rows
    set_settings(None)


def test_load_sample_fallback() -> None:
    root = Path(__file__).resolve().parents[1]
    result = load_sample_fallback(root / "samples" / "public_comments.csv")
    assert result.file_name == "public_comments.csv"
    assert len(result.rows) == 12
