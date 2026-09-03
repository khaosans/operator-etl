"""Build an ObjectStore from Settings — provider adapters are optional extras."""

from __future__ import annotations

from operator_etl.config import Settings, get_settings
from operator_etl.extract.object_store import ObjectStore


def _infer_backend(settings: Settings) -> str:
    if settings.object_store_backend:
        return settings.object_store_backend
    uri = settings.inbox_uri or ""
    if uri.startswith("gs://") or settings.gcs_inbox_bucket:
        return "gcs"
    if uri.startswith("s3://") or settings.s3_inbox_bucket:
        return "s3"
    if uri.startswith("az://") or settings.azure_inbox_container:
        return "azure"
    raise ValueError(
        "No object store configured. Set OPERATOR_ETL_OBJECT_STORE_BACKEND "
        "(gcs|s3|azure) and OPERATOR_ETL_INBOX_URI (or provider bucket/container env)."
    )


def resolve_object_store(settings: Settings | None = None) -> ObjectStore:
    """Return the configured object-store adapter for inbox extract."""
    settings = settings or get_settings()
    backend = _infer_backend(settings)
    if backend == "gcs":
        from operator_etl_gcp.extract.gcs import GcsObjectStore

        bucket = settings.resolved_inbox_bucket
        if not bucket:
            raise ValueError(
                "OPERATOR_ETL_GCS_INBOX_BUCKET or gs:// OPERATOR_ETL_INBOX_URI required for gcs object store"
            )
        return GcsObjectStore(bucket, settings)
    if backend == "s3":
        from operator_etl_aws.extract.s3 import S3ObjectStore

        bucket = settings.resolved_s3_bucket
        if not bucket:
            raise ValueError(
                "OPERATOR_ETL_S3_INBOX_BUCKET or s3:// OPERATOR_ETL_INBOX_URI required for s3 object store"
            )
        return S3ObjectStore(bucket, settings)
    if backend == "azure":
        from operator_etl_azure.extract.blob import AzureBlobObjectStore

        container = settings.resolved_azure_container
        if not container:
            raise ValueError(
                "OPERATOR_ETL_AZURE_INBOX_CONTAINER or az:// OPERATOR_ETL_INBOX_URI required for azure object store"
            )
        return AzureBlobObjectStore(
            container,
            settings,
            account_name=settings.resolved_azure_account,
        )
    raise ValueError(f"Unsupported object_store_backend {backend!r} (supported: gcs, s3, azure)")
