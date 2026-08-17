from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPERATOR_ETL_")

    root: Path = Field(default_factory=_default_root)
    warehouse: Path | None = None
    max_quarantine_rate: float = 0.35
    max_freshness_hours: float = 168.0

    pipeline_name: str = "demo"
    domain: str = "orders"

    @property
    def warehouse_path(self) -> Path:
        return Path(self.warehouse) if self.warehouse else self.root / "warehouse" / "operator.duckdb"

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


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def set_settings(settings: Settings | None) -> None:
    global _settings
    _settings = settings
