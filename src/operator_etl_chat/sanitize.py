"""Allowlisted field sanitizers for chat payloads — no PII, vault, or raw rows."""

from __future__ import annotations

from typing import Any

# Fields permitted in HITL alerts and slash-command replies.
HITL_ALLOWED_KEYS = frozenset(
    {
        "run_id",
        "pipeline",
        "status",
        "rows_in",
        "rows_silver",
        "rows_quarantined",
        "critic_passed",
        "domain",
        "message",
    }
)

KPI_ALLOWED_KEYS = frozenset(
    {
        "comment_count",
        "docket_count",
        "agency_count",
        "pii_flagged_count",
        "pii_rate",
        "order_count",
        "revenue_sum",
        "customer_count",
    }
)

RUN_STATUS_ALLOWED_KEYS = frozenset(
    {
        "run_id",
        "pipeline_name",
        "domain",
        "status",
        "rows_in",
        "rows_silver",
        "rows_quarantined",
        "started_at",
        "finished_at",
        "error",
    }
)

_BLOCKED_SUBSTRINGS = (
    "vault",
    "decrypt",
    "bronze",
    "silver_row",
    "comment_body",
    "email",
    "ssn",
    "phone",
    "raw_record",
    "insight_draft",
    "public_brief",
)


def _is_blocked_key(key: str) -> bool:
    lower = key.lower()
    return any(blocked in lower for blocked in _BLOCKED_SUBSTRINGS)


def sanitize_hitl_payload(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep only allowlisted HITL alert fields."""
    out: dict[str, Any] = {}
    for key, value in raw.items():
        if key not in HITL_ALLOWED_KEYS or _is_blocked_key(key):
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            out[key] = value
    if "status" not in out:
        out["status"] = "needs_human"
    if "message" not in out:
        out["message"] = "HITL review required — open the Operator ETL dashboard."
    return out


def sanitize_kpis(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep gold KPI aggregates only."""
    return {
        k: v
        for k, v in raw.items()
        if k in KPI_ALLOWED_KEYS and not _is_blocked_key(k) and isinstance(v, (str, int, float, bool))
    }


def sanitize_run_status(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep pipeline_runs audit fields; drop free-text error bodies that may leak data."""
    out: dict[str, Any] = {}
    for key, value in raw.items():
        if key not in RUN_STATUS_ALLOWED_KEYS or _is_blocked_key(key):
            continue
        if key == "error" and value is not None:
            # Surface only that an error exists — never raw exception text to Discord.
            out[key] = "see_dashboard"
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            out[key] = value
    return out


def format_hitl_discord_content(payload: dict[str, Any]) -> str:
    """Render a short Discord message from a sanitized HITL payload."""
    clean = sanitize_hitl_payload(payload)
    run_id = clean.get("run_id", "unknown")
    pipeline = clean.get("pipeline", "unknown")
    status = clean.get("status", "needs_human")
    silver = clean.get("rows_silver", "?")
    quarantined = clean.get("rows_quarantined", "?")
    msg = clean.get("message", "HITL review required.")
    return (
        f"**Operator ETL — HITL escalation**\n"
        f"run_id=`{run_id}` pipeline=`{pipeline}` status=`{status}`\n"
        f"silver={silver} quarantined={quarantined}\n"
        f"{msg}"
    )


def format_dict_discord_content(title: str, data: dict[str, Any]) -> str:
    """Render a compact Discord reply from a sanitized dict."""
    if not data:
        return f"**{title}**\n(no data)"
    lines = [f"**{title}**"]
    for key, value in sorted(data.items()):
        lines.append(f"`{key}`={value}")
    return "\n".join(lines)
