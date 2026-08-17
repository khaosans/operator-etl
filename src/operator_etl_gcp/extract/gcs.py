"""GCS inbox extraction for Cloud Run ingest triggers."""

from __future__ import annotations

import csv
import hashlib
import io
import tempfile
from pathlib import Path

from operator_etl.config import Settings, get_settings
from operator_etl.extract.csv import ExtractResult, extract_csv


def extract_gcs_object(bucket: str, object_name: str, settings: Settings | None = None) -> ExtractResult:
    """Download a CSV from GCS and return ExtractResult."""
    settings = settings or get_settings()
    from google.cloud import storage

    client = storage.Client(project=settings.gcp_project)
    blob = client.bucket(bucket).blob(object_name)
    data = blob.download_as_bytes()
    digest = hashlib.sha256(data).hexdigest()
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = [{k: (v if v is not None else "") for k, v in row.items()} for row in reader]
    return ExtractResult(
        file_name=Path(object_name).name,
        content_hash=digest,
        rows=rows,
    )


def extract_gcs_inbox(bucket: str, prefix: str, settings: Settings | None = None) -> list[ExtractResult]:
    """List CSV objects under prefix and extract each."""
    settings = settings or get_settings()
    from google.cloud import storage

    client = storage.Client(project=settings.gcp_project)
    blobs = client.list_blobs(bucket, prefix=prefix)
    results: list[ExtractResult] = []
    for blob in blobs:
        if blob.name.endswith("/") or not blob.name.lower().endswith(".csv"):
            continue
        results.append(extract_gcs_object(bucket, blob.name, settings))
    return results


def stage_gcs_to_temp(bucket: str, object_name: str, settings: Settings | None = None) -> Path:
    """Download GCS object to a temp file (for hash-compatible local extract)."""
    settings = settings or get_settings()
    from google.cloud import storage

    client = storage.Client(project=settings.gcp_project)
    blob = client.bucket(bucket).blob(object_name)
    suffix = Path(object_name).suffix or ".csv"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    blob.download_to_file(tmp)
    tmp.close()
    return Path(tmp.name)
