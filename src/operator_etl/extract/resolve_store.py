"""Build an ObjectStore from Settings — provider adapters are optional extras."""

from __future__ import annotations

from operator_etl.config import Settings, get_settings
from operator_etl.extract.object_store import ObjectStore


def resolve_object_store(settings: Settings | None = None) -> ObjectStore:
    """Return the configured object-store adapter for inbox extract."""
    settings = settings or get_settings()
    backend = settings.object_store_backend
    if backend is None:
        # Infer from legacy GCS bucket or gs:// inbox URI
        if settings.inbox_uri and settings.inbox_uri.startswith("gs://"):
            backend = "gcs"
        elif settings.gcs_inbox_bucket:
            backend = "gcs"
        else:
            raise ValueError(
                "No object store configured. Set OPERATOR_ETL_OBJECT_STORE_BACKEND=gcs "
                "and OPERATOR_ETL_GCS_INBOX_BUCKET (or OPERATOR_ETL_INBOX_URI=gs://bucket/prefix)."
            )
    if backend == "gcs":
        from operator_etl_gcp.extract.gcs import GcsObjectStore

        bucket = settings.resolved_inbox_bucket
        if not bucket:
            raise ValueError(
                "OPERATOR_ETL_GCS_INBOX_BUCKET or gs:// OPERATOR_ETL_INBOX_URI required for gcs object store"
            )
        return GcsObjectStore(bucket, settings)
    raise ValueError(f"Unsupported object_store_backend {backend!r} (supported: gcs)")
