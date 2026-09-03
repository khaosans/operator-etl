from __future__ import annotations

from operator_etl.config import Settings
from operator_etl_graph.critic import critic_check
from operator_etl_graph.insights import render_llm_insight, render_template_insight
from operator_etl_graph.nodes import insight_node
from operator_etl_policy.budgets import RunBudget
from helpers import assert_insight_grounded_in_metrics

METRICS = {
    "comment_count": 10,
    "docket_count": 2,
    "agency_count": 2,
    "pii_flagged_count": 4,
    "pii_rate": 0.4,
}

GROUNDED = (
    "Public comment intake: 10 comments across 2 dockets and 2 agencies. "
    "4 comments flagged for FOIA redaction review (PII rate 0.4)."
)


def _llm_settings(**kwargs) -> Settings:
    return Settings(
        insight_backend="llm",
        llm_model="gpt-4o-mini",
        **kwargs,
    )


def test_template_backend_uses_gold_metrics():
    draft = render_template_insight(METRICS)
    assert "10 comments" in draft
    assert_insight_grounded_in_metrics(draft, METRICS)
    state = {"gold_metrics": METRICS, "quality_passes": True}
    out = insight_node(state, Settings(insight_backend="template"))
    assert out["insight_draft"] == draft
    assert "_llm_calls" not in out


def test_llm_backend_uses_mocked_grounded_draft(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")

    def fake_invoke(settings, messages):
        human = messages[1][1]
        assert "Gold metrics (JSON):" in human
        assert "comment_count" in human
        assert "2026" not in human
        assert "jane.doe" not in human
        assert "body" not in human.lower()
        return GROUNDED

    monkeypatch.setattr("operator_etl_graph.insights._invoke_chat", fake_invoke)
    settings = _llm_settings()
    out = insight_node({"gold_metrics": METRICS, "quality_passes": True, "_llm_calls": 0}, settings)
    assert out["insight_draft"] == GROUNDED
    assert out["_llm_calls"] == 1
    assert "errors" not in out
    passed, violations = critic_check(out["insight_draft"], METRICS)
    assert passed, violations


def test_llm_invented_number_fails_critic(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    monkeypatch.setattr(
        "operator_etl_graph.insights._invoke_chat",
        lambda settings, messages: "Received 999 comments across 2 dockets.",
    )
    settings = _llm_settings()
    out = insight_node({"gold_metrics": METRICS, "quality_passes": True, "_llm_calls": 0}, settings)
    passed, violations = critic_check(out["insight_draft"], METRICS)
    assert not passed
    assert "999" in violations


def test_llm_backend_falls_back_to_template_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = _llm_settings()
    called = {"n": 0}

    def boom(settings, messages):  # pragma: no cover - must not run
        called["n"] += 1
        raise AssertionError("must not call the model without credentials")

    monkeypatch.setattr("operator_etl_graph.insights._invoke_chat", boom)
    budget = RunBudget(max_llm_calls=12)
    draft, note = render_llm_insight(METRICS, settings, budget)
    assert called["n"] == 0
    assert draft == render_template_insight(METRICS)
    assert note is not None
    assert "OPENAI_API_KEY" in note
    assert budget.llm_calls == 0

    monkeypatch.setattr(
        "operator_etl_graph.insights._invoke_chat",
        lambda settings, messages: (_ for _ in ()).throw(ImportError("langchain_openai")),
    )
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    draft2, note2 = render_llm_insight(METRICS, settings, RunBudget())
    assert draft2 == render_template_insight(METRICS)
    assert note2 is not None
    assert "langchain-openai" in note2


def test_llm_payload_strips_timestamps(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    captured: dict = {}

    def fake_invoke(settings, messages):
        captured["human"] = messages[1][1]
        return GROUNDED

    monkeypatch.setattr("operator_etl_graph.insights._invoke_chat", fake_invoke)
    metrics = {**METRICS, "as_of": "2026-08-18T00:51:51.647651", "extra_mart_col": 999}
    insight_node({"gold_metrics": metrics, "quality_passes": True, "_llm_calls": 0}, _llm_settings())
    assert "comment_count" in captured["human"]
    assert "2026" not in captured["human"]
    assert "as_of" not in captured["human"]
    assert "extra_mart_col" not in captured["human"]
    assert "999" not in captured["human"]


def test_llm_invoke_passes_max_tokens(monkeypatch):
    import sys
    import types

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    captured: dict = {}

    class FakeChat:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def invoke(self, messages):
            return type("R", (), {"content": GROUNDED})()

    fake_mod = types.ModuleType("langchain_openai")
    fake_mod.ChatOpenAI = FakeChat  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "langchain_openai", fake_mod)

    from operator_etl_graph.insights import _invoke_chat

    settings = _llm_settings(llm_max_tokens=128)
    assert _invoke_chat(settings, [("system", "s"), ("human", "h")]) == GROUNDED
    assert captured["max_tokens"] == 128
    assert captured["temperature"] == 0
