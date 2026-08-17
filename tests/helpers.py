from __future__ import annotations

import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")


def assert_no_pii_leak(text: str) -> None:
    assert not EMAIL.search(text), "email leaked in insight"
    assert not PHONE.search(text), "phone leaked in insight"


def assert_insight_grounded_in_metrics(insight: str, metrics: dict) -> None:
    """Every number in insight must exist in gold metrics (same rule as critic)."""
    from operator_etl_graph.critic import critic_check

    passed, violations = critic_check(insight, metrics)
    assert passed, f"uncited numbers in insight: {violations}"
