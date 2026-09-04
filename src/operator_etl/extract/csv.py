from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExtractResult:
    file_name: str
    content_hash: str
    rows: list[dict[str, str]]


def file_content_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 64), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_csv(path: Path) -> ExtractResult:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = [
            {key: (value if value is not None else "") for key, value in row.items()}
            for row in reader
        ]
    return ExtractResult(file_name=path.name, content_hash=file_content_hash(path), rows=rows)


def extract_csv_dir(directory: Path) -> list[ExtractResult]:
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        return []
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".csv")
    return [extract_csv(path) for path in files]
