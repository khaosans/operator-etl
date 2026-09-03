from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_root() -> Path:
    return Path(__file__).resolve().parents[2]


BackendKind = Literal["duckdb", "bigquery"]
CheckpointBackend = Literal["sqlite", "postgres"]
InsightBackend = Literal["template", "llm"]
ObjectStoreBackend = Literal["gcs"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPERATOR_ETL_")

    root: Path = Field(default_factory=_default_root)
    warehouse: Path | None = None
    orders_warehouse: Path | None = None
    max_quarantine_rate: float = 0.35
    max_freshness_hours: float = 168.0

    pipeline_name: str = "demo"
    domain: str = "orders"

    # Runtime warehouse — duckdb (local) or bigquery (GCP reference cloud)
    backend: BackendKind = "duckdb"
    checkpoint_backend: CheckpointBackend = "sqlite"
    checkpoint_database_url: str | None = None

    # Optional LLM insights — default template so CI needs no API key
    insight_backend: InsightBackend = "template"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str | None = None
    max_llm_calls: int = 12

    # Portable object-store inbox (adapters: gcs today; s3/azure later)
    object_store_backend: ObjectStoreBackend | None = None
    inbox_uri: str | None = None

    # GCP reference adapter fields (used when backend=bigquery / object_store=gcs)
    gcp_project: str | None = None
    gcs_inbox_bucket: str | None = None
    bq_dataset_bronze: str = "etl_bronze"
    bq_dataset_silver: str = "etl_silver"
    bq_dataset_quarantine: str = "etl_quarantine"
    bq_dataset_gold: str = "etl_gold"
    gcp_region: str = "us-central1"

    @property
    def uses_bigquery(self) -> bool:
        return self.backend == "bigquery"

    @property
    def is_gcp(self) -> bool:
        """Deprecated alias for uses_bigquery — kept for existing callers/tests."""
        return self.uses_bigquery

    @property
    def resolved_inbox_bucket(self) -> str | None:
        """Bucket name from gcs_inbox_bucket or gs://inbox_uri."""
        if self.gcs_inbox_bucket:
            return self.gcs_inbox_bucket
        if self.inbox_uri and self.inbox_uri.startswith("gs://"):
            rest = self.inbox_uri[len("gs://") :]
            return rest.split("/", 1)[0] or None
        return None

    @property
    def resolved_inbox_prefix(self) -> str:
        """Optional key prefix from gs://bucket/prefix inbox_uri."""
        if self.inbox_uri and self.inbox_uri.startswith("gs://"):
            rest = self.inbox_uri[len("gs://") :]
            if "/" in rest:
                return rest.split("/", 1)[1]
        return ""

    @property
    def warehouse_path(self) -> Path:
        return Path(self.warehouse) if self.warehouse else self.root / "warehouse" / "operator.duckdb"

    @property
    def orders_warehouse_path(self) -> Path:
        if self.orders_warehouse:
            return Path(self.orders_warehouse)
        return self.root / "warehouse" / "operator.duckdb"

    @property
    def checkpoint_path(self) -> Path:
        return self.root / "warehouse" / "checkpoints.db"

    @property
    def inbox_dir(self) -> Path:
        return self.root / "drops" / "inbox"

    @property
    def samples_dir(self) -> Path:
        return self.root / "samples"

    @property
    def sql_dir(self) -> Path:
        if self.domain == "gov":
            return self.root / "sql" / "marts" / "gov"
        return self.root / "sql" / "marts"

    @property
    def pipeline_path(self) -> Path:
        return self.root / "pipelines" / f"{self.pipeline_name}.yaml"

    @property
    def dashboard_path(self) -> Path:
        return self.root / "dashboard" / "app.py"

    def table_ref(self, layer: Literal["bronze", "silver", "quarantine", "gold"], table: str) -> str:
        """BigQuery table reference: project.dataset.table"""
        datasets = {
            "bronze": self.bq_dataset_bronze,
            "silver": self.bq_dataset_silver,
            "quarantine": self.bq_dataset_quarantine,
            "gold": self.bq_dataset_gold,
        }
        project = self.gcp_project or "local"
        return f"{project}.{datasets[layer]}.{table}"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def set_settings(settings: Settings | None) -> None:
    global _settings
    _settings = settings
