"""Decode GCS Pub/Sub push notifications into ingest events."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class GcsIngestEvent:
    bucket: str
    object_name: str
    content_type: str | None = None
    size_bytes: int | None = None

    @property
    def is_csv(self) -> bool:
        return self.object_name.lower().endswith(".csv")


def decode_pubsub_push(body: dict) -> GcsIngestEvent:
    """Parse Cloud Pub/Sub push envelope wrapping a GCS JSON_API_V1 notification."""
    message = body.get("message") or {}
    data_b64 = message.get("data")
    if not data_b64:
        raise ValueError("Pub/Sub message missing data field")
    payload = json.loads(base64.b64decode(data_b64).decode("utf-8"))
    bucket = payload.get("bucket") or payload.get("bucketId") or ""
    name = payload.get("name") or payload.get("objectId") or ""
    if not bucket or not name:
        raise ValueError(f"Unrecognized GCS notification payload: {payload!r}")
    return GcsIngestEvent(
        bucket=bucket,
        object_name=name,
        content_type=payload.get("contentType"),
        size_bytes=int(payload["size"]) if payload.get("size") else None,
    )
