from __future__ import annotations

import operator
import re
import uuid
from typing import Annotated, Literal, TypedDict

from operator_etl_policy.pii import PiiFinding


class PipelineState(TypedDict, total=False):
    run_id: str
    source: str
    domain: str
    content_hash: str
    rows_in: int
    rows_silver: int
    rows_quarantined: int
    pii_findings: list[dict]
    pii_needs_human: bool
    quality_passes: bool
    quality_reasons: list[str]
    gold_metrics: dict
    insight_draft: str
    critic_passed: bool
    critic_violations: list[str]
    insight_id: str
    status: Literal["running", "needs_human", "failed", "complete"]
    errors: Annotated[list[str], operator.add]
    _records: list[dict]
    _quality_report: dict
    _critic_retries: int


def new_run_id() -> str:
    return str(uuid.uuid4())
