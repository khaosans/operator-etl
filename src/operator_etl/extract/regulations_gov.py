"""Regulations.gov comment fetch — sample fallback when API key absent."""

from __future__ import annotations

import csv
import io
import os
from typing import Any

import hashlib

import httpx

from operator_etl.extract.csv import ExtractResult


REGULATIONS_GOV_BASE = "https://api.regulations.gov/v4"


def _headers() -> dict[str, str]:
    key = os.environ.get("REGULATIONS_GOV_API_KEY", "").strip()
    headers = {"Accept": "application/json"}
    if key:
        headers["X-Api-Key"] = key
    return headers


def fetch_comments_for_docket(
    docket_id: str,
    *,
    max_pages: int = 3,
    client: httpx.Client | None = None,
) -> list[dict[str, str]]:
    """Fetch comment documents for a docket. Requires REGULATIONS_GOV_API_KEY for live calls."""
    key = os.environ.get("REGULATIONS_GOV_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "REGULATIONS_GOV_API_KEY is required for live regulations.gov intake; "
            "use samples/public_comments.csv for local demos"
        )

    owns_client = client is None
    client = client or httpx.Client(timeout=30.0, headers=_headers())
    rows: list[dict[str, str]] = []
    try:
        page = 1
        while page <= max_pages:
            resp = client.get(
                f"{REGULATIONS_GOV_BASE}/comments",
                params={
                    "filter[docketId]": docket_id,
                    "page[size]": 250,
                    "page[number]": page,
                },
            )
            resp.raise_for_status()
            payload: dict[str, Any] = resp.json()
            data = payload.get("data") or []
            if not data:
                break
            for item in data:
                attrs = item.get("attributes") or {}
                rows.append(
                    {
                        "comment_id": str(item.get("id") or attrs.get("commentId") or ""),
                        "docket_id": docket_id,
                        "agency": str(attrs.get("agencyId") or ""),
                        "submitted_at": str(attrs.get("postedDate") or attrs.get("receiveDate") or ""),
                        "commenter_type": str(attrs.get("submitterType") or "public"),
                        "subject": str(attrs.get("title") or ""),
                        "body": str(attrs.get("comment") or attrs.get("commentOnDocumentId") or ""),
                        "foia_status": "pending_review",
                    }
                )
            meta = (payload.get("meta") or {}).get("hasNextPage")
            if not meta:
                break
            page += 1
    finally:
        if owns_client:
            client.close()
    return rows


def rows_to_extract(rows: list[dict[str, str]], *, file_name: str) -> ExtractResult:
    if not rows:
        payload = b""
    else:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        payload = buf.getvalue().encode("utf-8")
    return ExtractResult(
        file_name=file_name,
        content_hash=hashlib.sha256(payload).hexdigest(),
        rows=rows,
    )


def load_sample_fallback(sample_path) -> ExtractResult:
    """Deterministic offline path used when live API is unavailable."""
    text = sample_path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows = [dict(row) for row in reader]
    return rows_to_extract(rows, file_name=sample_path.name)
