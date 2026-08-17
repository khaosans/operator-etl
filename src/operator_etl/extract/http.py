from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from operator_etl.extract.csv import ExtractResult, file_content_hash


def extract_http(url: str, *, timeout: float = 30.0, root: Path | None = None) -> ExtractResult:
    """GET a JSON list (or {data|items|orders: [...]}) and land it as rows.

    `file:` / `file://` URLs read a local JSON file so the stub works offline.
    """
    payload, source_name, content_hash = _fetch(url, timeout=timeout, root=root)
    rows = _as_row_dicts(payload)
    return ExtractResult(file_name=source_name, content_hash=content_hash, rows=rows)


def _fetch(url: str, *, timeout: float, root: Path | None) -> tuple[Any, str, str]:
    parsed = urlparse(url)
    if parsed.scheme in {"", "file"}:
        path = _local_path(url, root)
        text = path.read_text(encoding="utf-8")
        return json.loads(text), path.name, file_content_hash(path)

    response = httpx.get(url, timeout=timeout, follow_redirects=True)
    response.raise_for_status()
    digest = hashlib.sha256(response.content).hexdigest()
    name = Path(parsed.path).name or "http.json"
    return response.json(), name, digest


def _local_path(url: str, root: Path | None) -> Path:
    raw = url
    if raw.startswith("file://"):
        raw = raw[7:]
    elif raw.startswith("file:"):
        raw = raw[5:]
    path = Path(raw)
    if not path.is_absolute() and root is not None:
        path = root / path
    return path


def _as_row_dicts(payload: Any) -> list[dict[str, str]]:
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        nested = next(
            (payload[key] for key in ("data", "items", "orders", "results") if isinstance(payload.get(key), list)),
            None,
        )
        records = nested if nested is not None else [payload]
    else:
        raise ValueError(f"HTTP JSON must be a list or object, got {type(payload).__name__}")

    rows: list[dict[str, str]] = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each JSON record must be an object")
        rows.append({str(key): "" if value is None else str(value) for key, value in record.items()})
    return rows
