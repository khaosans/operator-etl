from __future__ import annotations

import operator
import uuid
from typing import Annotated, Literal, TypedDict


class PipelineState(TypedDict, total=False):
    run_id: str
    task_id: str
    source: str
    domain: str
    docket_id: str
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
    artifacts: dict
    status: Literal["running", "needs_human", "failed", "complete"]
    errors: Annotated[list[str], operator.add]
    _input_records: list[dict[str, str]]
    _records: list[dict]
    _quality_report: dict
    _critic_retries: int
    _llm_calls: int


def new_run_id() -> str:
    return str(uuid.uuid4())
