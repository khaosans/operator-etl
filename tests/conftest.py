from __future__ import annotations

from pathlib import Path

import pytest

from operator_etl.config import Settings, set_settings

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    configured = Settings(
        root=REPO_ROOT,
        warehouse=tmp_path / "operator.duckdb",
        pipeline_name="demo",
        domain="orders",
        insight_backend="template",
    )
    set_settings(configured)
    yield configured
    set_settings(None)


@pytest.fixture
def gov_settings(tmp_path: Path) -> Settings:
    configured = Settings(
        root=REPO_ROOT,
        warehouse=tmp_path / "operator.duckdb",
        pipeline_name="public_comments",
        domain="gov",
        insight_backend="template",
    )
    set_settings(configured)
    yield configured
    set_settings(None)
