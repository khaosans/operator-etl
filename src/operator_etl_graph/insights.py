from __future__ import annotations

import json
import os

from operator_etl.config import Settings
from operator_etl_policy.budgets import BudgetExceeded, RunBudget
from telemetry.tracer import span

_SYSTEM_PROMPT = """You write a short FOIA public-comment intake summary for officers.
Use ONLY numbers that appear in the JSON gold metrics provided.
Cite every figure exactly as it appears in the JSON (for example 0.4, not 40% or 40).
You must mention comment_count, docket_count, agency_count, pii_flagged_count, and pii_rate using those exact values.
Do not invent counts, rates, dates, identifiers, or other figures.
Do not mention individual comments, emails, names, phone numbers, or other PII.
Do not quote comment bodies. Two to four sentences. Plain language."""


def render_template_insight(metrics: dict) -> str:
    return (
        f"Public comment intake summary: {int(metrics.get('comment_count', 0))} comments across "
        f"{int(metrics.get('docket_count', 0))} dockets and {int(metrics.get('agency_count', 0))} agencies. "
        f"{int(metrics.get('pii_flagged_count', 0))} comments flagged for FOIA redaction review "
        f"(PII rate {float(metrics.get('pii_rate', 0))}). "
        f"FOIA officers should prioritize redaction queue before release."
    )


def _invoke_chat(settings: Settings, messages: list[tuple[str, str]]) -> str:
    from langchain_openai import ChatOpenAI

    with span(
        "operator_etl.llm.invoke",
        attributes={"llm.model": settings.llm_model, "llm.base_url_configured": bool(settings.llm_base_url)},
    ):
        kwargs: dict = {"model": settings.llm_model, "temperature": 0}
        api_key = os.environ.get("OPENAI_API_KEY")
        if settings.llm_base_url:
            kwargs["base_url"] = str(settings.llm_base_url).rstrip("/")
        if api_key:
            kwargs["api_key"] = api_key
        elif settings.llm_base_url:
            kwargs["api_key"] = "not-needed"
        llm = ChatOpenAI(**kwargs)
        resp = llm.invoke(messages)
        content = getattr(resp, "content", resp)
        if not isinstance(content, str):
            content = str(content)
        return content.strip()


def _has_llm_credentials(settings: Settings) -> bool:
    if os.environ.get("OPENAI_API_KEY"):
        return True
    return bool(settings.llm_base_url)


def _llm_metric_payload(metrics: dict) -> dict:
    """Numeric gold KPIs only — drop timestamps so the model cannot echo dates."""
    out: dict = {}
    for key, value in metrics.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            out[key] = value
    return out


def render_llm_insight(
    metrics: dict,
    settings: Settings,
    budget: RunBudget,
) -> tuple[str, str | None]:
    """Draft an insight from gold metrics via an OpenAI-compatible API.

    Returns ``(draft, fallback_note)``. ``fallback_note`` is set when the
    template is used instead of the model (missing extra, no key, error, budget).
    Never sends bronze, comment bodies, or vault PII — gold KPI JSON only.
    """
    with span(
        "operator_etl.llm.render_insight",
        attributes={"metric_keys": len(_llm_metric_payload(metrics)), "insight_backend": settings.insight_backend},
    ):
        if not _has_llm_credentials(settings):
            return (
                render_template_insight(metrics),
                "OPENAI_API_KEY unset (and no OPERATOR_ETL_LLM_BASE_URL); using template insight",
            )
        try:
            budget.record_llm()
        except BudgetExceeded as exc:
            return render_template_insight(metrics), str(exc)

        payload = json.dumps(_llm_metric_payload(metrics), default=str, sort_keys=True)
        messages = [
            ("system", _SYSTEM_PROMPT),
            ("human", f"Gold metrics (JSON):\n{payload}"),
        ]
        try:
            draft = _invoke_chat(settings, messages)
        except ImportError:
            return (
                render_template_insight(metrics),
                "langchain-openai not installed (uv sync --extra llm); using template insight",
            )
        except Exception as exc:  # noqa: BLE001 — fail closed to template, critic still runs
            return (
                render_template_insight(metrics),
                f"LLM insight failed ({exc}); using template insight",
            )
        if not draft:
            return (
                render_template_insight(metrics),
                "LLM returned empty insight; using template insight",
            )
        return draft, None
