from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

REQUIRED = ("comment_id", "docket_id", "agency", "submitted_at", "commenter_type", "body")


class SilverComment(BaseModel):
    comment_id: str = Field(min_length=1)
    docket_id: str = Field(min_length=1)
    agency: str = Field(min_length=1)
    submitted_at: datetime
    commenter_type: str = Field(min_length=1)
    subject: str = ""
    body: str = Field(min_length=1)
    foia_status: str = "pending_review"
    pii_detected: bool = False

    @field_validator("comment_id", "docket_id", "agency", "commenter_type", mode="before")
    @classmethod
    def strip_required(cls, value: Any) -> str:
        if value is None:
            raise ValueError("required")
        text = str(value).strip()
        if not text:
            raise ValueError("empty")
        return text


def parse_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, str):
        return json.loads(payload)
    if isinstance(payload, dict):
        return payload
    raise TypeError(f"Unexpected payload type {type(payload)!r}")


def validate_comment(payload: Any) -> tuple[SilverComment | None, str | None]:
    data = parse_payload(payload)
    missing = [f for f in REQUIRED if f not in data or data[f] in (None, "")]
    if missing:
        return None, f"missing fields: {', '.join(missing)}"
    if "pii_detected" in data:
        data["pii_detected"] = str(data["pii_detected"]).lower() in ("true", "1", "yes")
    try:
        return SilverComment.model_validate(data), None
    except ValidationError as exc:
        return None, "; ".join(err["msg"] for err in exc.errors())
