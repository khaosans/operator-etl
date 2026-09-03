"""Object-store inbox protocol — portable CSV extract from cloud buckets."""

from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path
from typing import Protocol, runtime_checkable

from operator_etl.extract.csv import ExtractResult


@runtime_checkable
class ObjectStore(Protocol):
    """Minimal object-store API for CSV inbox ingestion."""

    def list_csv_keys(self, prefix: str = "") -> list[str]: ...

    def download_bytes(self, key: str) -> bytes: ...


def extract_object(store: ObjectStore, key: str) -> ExtractResult:
    """Download a CSV object and return ExtractResult."""
    data = store.download_bytes(key)
    digest = hashlib.sha256(data).hexdigest()
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = [{k: (v if v is not None else "") for k, v in row.items()} for row in reader]
    return ExtractResult(
        file_name=Path(key).name,
        content_hash=digest,
        rows=rows,
    )


def extract_inbox(store: ObjectStore, prefix: str = "") -> list[ExtractResult]:
    """List CSV keys under prefix and extract each."""
    return [extract_object(store, key) for key in store.list_csv_keys(prefix)]


class MemoryObjectStore:
    """In-memory ObjectStore for tests."""

    def __init__(self, objects: dict[str, bytes] | None = None):
        self._objects = dict(objects or {})

    def list_csv_keys(self, prefix: str = "") -> list[str]:
        keys = []
        for key in sorted(self._objects):
            if prefix and not key.startswith(prefix):
                continue
            if key.endswith("/") or not key.lower().endswith(".csv"):
                continue
            keys.append(key)
        return keys

    def download_bytes(self, key: str) -> bytes:
        return self._objects[key]
