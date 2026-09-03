"""Warehouse connection protocol — cloud-portable data-plane surface."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class WarehouseConnection(Protocol):
    """Minimal warehouse API shared by DuckDB (local) and cloud adapters."""

    backend: str

    def execute(self, sql: str, params: list | None = None) -> Any: ...

    def fetchone(self) -> tuple | None: ...

    def fetchall(self) -> list[tuple]: ...

    def close(self) -> None: ...
