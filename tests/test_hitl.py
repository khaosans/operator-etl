"""HITL officer approve/reject audit store."""

from __future__ import annotations

from pathlib import Path

import pytest

from operator_etl.config import Settings, set_settings
from operator_etl_policy.hitl import HitlStore


@pytest.fixture()
def hitl_settings(tmp_path: Path):
    settings = Settings(root=tmp_path, warehouse=tmp_path / "operator.duckdb")
    set_settings(settings)
    yield settings
    set_settings(None)


def test_hitl_approve_reject_audit(hitl_settings: Settings, tmp_path: Path) -> None:
    store = HitlStore(path=tmp_path / "hitl_audit.json", settings=hitl_settings)
    approved = store.decide("run-1", "approve", officer="priya", reason="redaction complete")
    assert approved.decision == "approve"
    assert store.is_approved("run-1") is True
    rejected = store.decide("run-1", "reject", officer="priya", reason="new PII found")
    assert rejected.decision == "reject"
    assert store.is_approved("run-1") is False
    latest = store.latest_for_run("run-1")
    assert latest is not None
    assert latest.reason == "new PII found"
    assert len(store.list_decisions()) == 2


def test_hitl_persists_across_reload(hitl_settings: Settings, tmp_path: Path) -> None:
    path = tmp_path / "hitl_audit.json"
    HitlStore(path=path, settings=hitl_settings).decide("run-2", "approve", officer="ops")
    reloaded = HitlStore(path=path, settings=hitl_settings)
    assert reloaded.is_approved("run-2") is True
