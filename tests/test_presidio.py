"""Presidio scanner path (mocked — no heavy NLP deps required in CI)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from operator_etl_policy import pii


def test_presidio_scanner_uses_analyzer_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPERATOR_ETL_PII_SCANNER", "presidio")

    fake_result = MagicMock()
    fake_result.entity_type = "EMAIL_ADDRESS"
    fake_result.score = 0.72

    fake_engine = MagicMock()
    fake_engine.analyze.return_value = [fake_result]

    fake_module = MagicMock()
    fake_module.AnalyzerEngine.return_value = fake_engine

    with (
        patch("operator_etl_policy.pii._presidio_available", return_value=True),
        patch.dict("sys.modules", {"presidio_analyzer": fake_module}),
    ):
        hits = pii.scan_text("Contact someone maybe")
        assert hits == [("EMAIL", 0.72)]
        result = pii.scan_records([{"body": "Contact someone maybe"}])
    assert result.needs_human is True


def test_presidio_missing_extra_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPERATOR_ETL_PII_SCANNER", "presidio")
    with patch("operator_etl_policy.pii._presidio_available", return_value=False):
        with pytest.raises(ImportError, match="presidio"):
            pii.scan_text("jane@example.com")


def test_regex_backend_default_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPERATOR_ETL_PII_SCANNER", "regex")
    hits = pii.scan_text("jane@example.com")
    assert ("EMAIL", 0.95) in hits
