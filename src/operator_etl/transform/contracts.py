from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

REQUIRED_FIELDS = ("order_id", "customer_id", "ordered_at", "amount", "sku", "status")


class SilverOrder(BaseModel):
    order_id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    ordered_at: datetime
    amount: float = Field(gt=0)
    sku: str = Field(min_length=1)
    status: str = Field(min_length=1)

    @field_validator("order_id", "customer_id", "sku", "status", mode="before")
    @classmethod
    def strip_required(cls, value: Any) -> str:
        if value is None:
            raise ValueError("required")
        text = str(value).strip()
        if not text:
            raise ValueError("empty")
        return text

    @field_validator("amount", mode="before")
    @classmethod
    def parse_amount(cls, value: Any) -> Any:
        if isinstance(value, str):
            text = value.strip().replace("$", "").replace(",", "")
            if not text:
                raise ValueError("empty amount")
            return text
        return value


def parse_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, str):
        return json.loads(payload)
    if isinstance(payload, dict):
        return payload
    raise TypeError(f"Unexpected payload type {type(payload)!r}")


def validate_order(payload: Any) -> tuple[SilverOrder | None, str | None]:
    data = parse_payload(payload)
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        return None, f"missing fields: {', '.join(missing)}"
    try:
        return SilverOrder.model_validate(data), None
    except ValidationError as exc:
        return None, "; ".join(err["msg"] for err in exc.errors())
