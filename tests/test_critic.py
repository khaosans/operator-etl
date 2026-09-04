from __future__ import annotations

import re

from operator_etl_graph.critic import critic_check

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")


def test_critic_accepts_cited_metrics():
    metrics = {
        "comment_count": 10,
        "pii_rate": 0.25,
        "docket_count": 2,
        "agency_count": 2,
        "pii_flagged_count": 2,
    }
    draft = "Received 10 comments across 2 dockets. PII rate 0.25."
    passed, violations = critic_check(draft, metrics)
    assert passed, violations


def test_critic_rejects_hallucinated_number():
    metrics = {"comment_count": 10}
    draft = "Received 999 comments."
    passed, violations = critic_check(draft, metrics)
    assert not passed
    assert "999" in violations


def test_critic_exhausted_routes_needs_human():
    from operator_etl_graph.graph import route_critic

    state = {"critic_passed": False, "_critic_retries": 2}
    assert route_critic(state) == "needs_human"
