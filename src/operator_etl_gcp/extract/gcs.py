"""GCS object-store adapter — reference cloud inbox implementation."""

from __future__ import annotations

import tempfile
from pathlib import Path

from operator_etl.config import Settings, get_settings
from operator_etl.extract.csv import ExtractResult
from operator_etl.extract.object_store import ObjectStore, extract_inbox, extract_object


class GcsObjectStore:
    """GCS-backed ObjectStore for Cloud Run / Pub/Sub inbox triggers."""

    def __init__(self, bucket: str, settings: Settings | None = None):
        self.bucket = bucket
        self.settings = settings or get_settings()
        self._client = None

    def _storage_client(self):
        if self._client is None:
            from google.cloud import storage

            self._client = storage.Client(project=self.settings.gcp_project)
        return self._client

    def list_csv_keys(self, prefix: str = "") -> list[str]:
        client = self._storage_client()
        keys: list[str] = []
        for blob in client.list_blobs(self.bucket, prefix=prefix):
            if blob.name.endswith("/") or not blob.name.lower().endswith(".csv"):
                continue
            keys.append(blob.name)
        return keys

    def download_bytes(self, key: str) -> bytes:
        client = self._storage_client()
        return client.bucket(self.bucket).blob(key).download_as_bytes()


def _store(bucket: str, settings: Settings | None = None) -> ObjectStore:
    return GcsObjectStore(bucket, settings)


def extract_gcs_object(bucket: str, object_name: str, settings: Settings | None = None) -> ExtractResult:
    """Download a CSV from GCS and return ExtractResult."""
    return extract_object(_store(bucket, settings), object_name)


def extract_gcs_inbox(bucket: str, prefix: str, settings: Settings | None = None) -> list[ExtractResult]:
    """List CSV objects under prefix and extract each."""
    return extract_inbox(_store(bucket, settings), prefix)


def stage_gcs_to_temp(bucket: str, object_name: str, settings: Settings | None = None) -> Path:
    """Download GCS object to a temp file (for hash-compatible local extract)."""
    data = _store(bucket, settings).download_bytes(object_name)
    suffix = Path(object_name).suffix or ".csv"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(data)
    tmp.close()
    return Path(tmp.name)
