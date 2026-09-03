from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from operator_etl.config import Settings, get_settings

SourceKind = Literal["csv", "csv_dir", "http", "gcs", "regulations_gov"]


@dataclass(frozen=True)
class Source:
    name: str
    kind: SourceKind
    path: Path | None = None
    url: str | None = None
    bronze_table: str = "bronze_raw"
    silver_table: str = "silver_orders"
    quarantine_table: str = "quarantine_orders"
    domain: str = "orders"
    docket_id: str | None = None
    options: dict[str, Any] | None = None


def load_pipeline(settings: Settings | None = None, pipeline_name: str | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    path = settings.root / "pipelines" / f"{pipeline_name or settings.pipeline_name}.yaml"
    with path.open() as fh:
        return yaml.safe_load(fh)


def get_source(name: str, settings: Settings | None = None, pipeline_name: str | None = None) -> Source:
    settings = settings or get_settings()
    spec = load_pipeline(settings, pipeline_name)
    sources = spec.get("sources") or {}
    if name not in sources:
        known = ", ".join(sorted(sources)) or "(none)"
        raise KeyError(f"Unknown source {name!r}. Registered: {known}")
    raw = sources[name]
    kind: SourceKind = raw["kind"]
    path = Path(raw["path"]) if raw.get("path") else None
    if path and not path.is_absolute():
        path = settings.root / path
    return Source(
        name=name,
        kind=kind,
        path=path,
        url=raw.get("url"),
        bronze_table=spec.get("bronze_table", "bronze_raw"),
        silver_table=spec.get("silver_table", "silver_orders"),
        quarantine_table=spec.get("quarantine_table", "quarantine_orders"),
        domain=spec.get("domain", "orders"),
        docket_id=raw.get("docket_id"),
        options={k: v for k, v in raw.items() if k not in {"kind", "path", "url", "docket_id"}},
    )


def list_sources(settings: Settings | None = None, pipeline_name: str | None = None) -> list[str]:
    spec = load_pipeline(settings, pipeline_name)
    return sorted((spec.get("sources") or {}).keys())
