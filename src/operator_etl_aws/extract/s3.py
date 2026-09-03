"""S3 object-store adapter for inbox CSV extract."""

from __future__ import annotations

from operator_etl.config import Settings, get_settings
from operator_etl.extract.object_store import ObjectStore, extract_inbox, extract_object
from operator_etl.extract.csv import ExtractResult


class S3ObjectStore:
    """S3-backed ObjectStore for ECS / EventBridge inbox triggers."""

    def __init__(self, bucket: str, settings: Settings | None = None, *, client=None):
        self.bucket = bucket
        self.settings = settings or get_settings()
        self._client = client

    def _s3(self):
        if self._client is None:
            import boto3

            self._client = boto3.client("s3", region_name=self.settings.aws_region)
        return self._client

    def list_csv_keys(self, prefix: str = "") -> list[str]:
        client = self._s3()
        keys: list[str] = []
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents") or []:
                key = obj["Key"]
                if key.endswith("/") or not key.lower().endswith(".csv"):
                    continue
                keys.append(key)
        return keys

    def download_bytes(self, key: str) -> bytes:
        client = self._s3()
        response = client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()


def extract_s3_inbox(bucket: str, prefix: str, settings: Settings | None = None) -> list[ExtractResult]:
    return extract_inbox(S3ObjectStore(bucket, settings), prefix)


def extract_s3_object(bucket: str, key: str, settings: Settings | None = None) -> ExtractResult:
    return extract_object(S3ObjectStore(bucket, settings), key)
