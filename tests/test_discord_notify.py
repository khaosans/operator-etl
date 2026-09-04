"""Discord HITL webhook notifier — sanitized, env-gated, fail-soft."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from operator_etl.load.connection import connect
from operator_etl.load.ops import start_run
from operator_etl_chat.discord.webhook_notifier import DiscordWebhookNotifier, notify_hitl_discord
from operator_etl_chat.sanitize import format_hitl_discord_content, sanitize_hitl_payload
from operator_etl_graph.nodes import needs_human_node


def test_sanitize_strips_pii_and_insight_fields() -> None:
    dirty = {
        "run_id": "run-1",
        "pipeline": "public_comments",
        "status": "needs_human",
        "rows_silver": 10,
        "rows_quarantined": 2,
        "insight_draft": "secret narrative",
        "email": "jane@example.com",
        "vault_token": "should-drop",
        "comment_body": "raw comment text",
    }
    clean = sanitize_hitl_payload(dirty)
    assert clean["run_id"] == "run-1"
    assert "insight_draft" not in clean
    assert "email" not in clean
    assert "vault_token" not in clean
    assert "comment_body" not in clean
    text = format_hitl_discord_content(dirty)
    assert "jane@example.com" not in text
    assert "secret narrative" not in text
    assert "run-1" in text


def test_notifier_noop_without_webhook(monkeypatch) -> None:
    monkeypatch.delenv("OPERATOR_ETL_DISCORD_WEBHOOK_URL", raising=False)
    assert notify_hitl_discord({"run_id": "x", "status": "needs_human"}) is False


def test_notifier_rejects_non_discord_host(monkeypatch) -> None:
    monkeypatch.setenv("OPERATOR_ETL_DISCORD_WEBHOOK_URL", "https://evil.example/api/webhooks/1/2")
    assert DiscordWebhookNotifier().notify_hitl({"run_id": "x"}) is False


def test_notifier_posts_sanitized_content(monkeypatch) -> None:
    url = "https://discord.com/api/webhooks/123/abc"
    monkeypatch.setenv("OPERATOR_ETL_DISCORD_WEBHOOK_URL", url)
    mock_response = MagicMock()
    mock_response.status_code = 204
    with patch(
        "operator_etl_chat.discord.webhook_notifier.httpx.post", return_value=mock_response
    ) as post:
        ok = DiscordWebhookNotifier().notify_hitl(
            {
                "run_id": "run-42",
                "pipeline": "public_comments",
                "rows_silver": 10,
                "rows_quarantined": 2,
                "insight_draft": "must not appear",
                "email": "leak@example.com",
            }
        )
    assert ok is True
    post.assert_called_once()
    kwargs = post.call_args
    assert kwargs.args[0] == url
    content = kwargs.kwargs["json"]["content"]
    assert "run-42" in content
    assert "must not appear" not in content
    assert "leak@example.com" not in content


def test_needs_human_invokes_notifier(gov_settings) -> None:
    calls: list[dict] = []

    def _fake_notify(payload: dict) -> bool:
        calls.append(payload)
        return True

    run_id = "run-hitl-notify-001"
    con = connect(gov_settings)
    try:
        start_run(con, run_id, "public_comments")
    finally:
        con.close()

    with patch(
        "operator_etl_chat.discord.webhook_notifier.notify_hitl_discord",
        side_effect=_fake_notify,
    ):
        result = needs_human_node(
            {
                "run_id": run_id,
                "rows_in": 12,
                "rows_silver": 10,
                "rows_quarantined": 2,
                "errors": [],
            },
            settings=gov_settings,
        )
    assert result["status"] == "needs_human"
    assert len(calls) == 1
    assert calls[0]["run_id"] == run_id
    assert "insight_draft" not in calls[0]
