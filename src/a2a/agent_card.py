from __future__ import annotations


def build_agent_card(base_url: str | None = None) -> dict:
    endpoints = {
        "tasks": "/a2a/v1/tasks",
        "events": "/a2a/v1/tasks/{task_id}/events",
    }
    if base_url:
        trimmed = base_url.rstrip("/")
        endpoints = {key: f"{trimmed}{value}" for key, value in endpoints.items()}
    return {
        "name": "Operator ETL FOIA & Redaction Service",
        "description": "Agentic ETL service for FOIA comment intake, PII redaction gating, and critic-approved public briefs.",
        "capabilities": ["FOIARedaction", "PublicCommentSummarization", "PIIVaulting"],
        "authentication": {"type": "bearer", "scheme": "Bearer"},
        "endpoints": endpoints,
    }
