"""Discord slash commands and Interactions HTTP endpoint."""

from __future__ import annotations

import json
import time
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from operator_etl.load.connection import connect
from operator_etl_chat.discord.commands import DiscordCommandHandler
from operator_etl_chat.discord.interactions import _user_hits
from operator_etl_gcp.http import app as http_app
from operator_etl_gcp.http.app import app


def _keypair_and_sign(body: bytes, timestamp: str) -> tuple[str, str]:
    private = Ed25519PrivateKey.generate()
    public_hex = private.public_key().public_bytes_raw().hex()
    signature_hex = private.sign(timestamp.encode("utf-8") + body).hex()
    return public_hex, signature_hex


def _signed_headers(body: bytes, public_hex: str, signature_hex: str, timestamp: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Signature-Ed25519": signature_hex,
        "X-Signature-Timestamp": timestamp,
    }


def test_command_kpis_sanitized(gov_settings) -> None:
    # Seed minimal gold via graph is heavy; mock get_gold_metrics.
    with patch(
        "operator_etl_chat.discord.commands.get_gold_metrics",
        return_value={
            "comment_count": 10,
            "docket_count": 2,
            "email": "should-strip@example.com",
            "insight_draft": "nope",
        },
    ):
        handler = DiscordCommandHandler(settings=gov_settings)
        result = handler.handle_command("kpis", {"domain": "gov"})
    content = result["data"]["content"]
    assert "comment_count" in content
    assert "should-strip" not in content
    assert "nope" not in content
    assert result["data"]["flags"] == 64


def test_command_status_not_found(gov_settings) -> None:
    # Touch warehouse so pipeline_runs exists.
    con = connect(gov_settings)
    con.close()
    handler = DiscordCommandHandler(settings=gov_settings)
    result = handler.handle_command("status", {"run_id": "missing-run"})
    assert "not found" in result["data"]["content"].lower()


def test_command_run_rejects_non_allowlisted_source(gov_settings) -> None:
    handler = DiscordCommandHandler(settings=gov_settings)
    result = handler.handle_command("run", {"source": "evil_source", "raw_records": [{"x": 1}]})
    assert "only" in result["data"]["content"].lower()
    assert "public_comments" in result["data"]["content"]


def test_command_run_fixed_params_only(gov_settings, monkeypatch) -> None:
    captured: dict = {}

    def _fake_run_graph(*, source, settings):
        captured["source"] = source
        captured["settings"] = settings
        return {
            "run_id": "r1",
            "status": "complete",
            "rows_silver": 10,
            "rows_quarantined": 2,
            "critic_passed": True,
            "insight_draft": "must not leak",
        }

    monkeypatch.setattr("operator_etl_chat.discord.commands.run_graph", _fake_run_graph)
    handler = DiscordCommandHandler(settings=gov_settings)
    result = handler.handle_command("run", {"source": "public_comments", "raw_records": [{"bad": True}]})
    assert captured["source"] == "public_comments"
    assert "must not leak" not in result["data"]["content"]
    assert "r1" in result["data"]["content"]


def test_interactions_ping(monkeypatch) -> None:
    body = json.dumps({"type": 1}).encode()
    timestamp = str(int(time.time()))
    public_hex, signature_hex = _keypair_and_sign(body, timestamp)
    monkeypatch.setenv("OPERATOR_ETL_DISCORD_PUBLIC_KEY", public_hex)
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10000")
    http_app._RATE_LIMIT = 10_000
    http_app._rate_counts.clear()

    client = TestClient(app)
    response = client.post(
        "/discord/interactions",
        content=body,
        headers=_signed_headers(body, public_hex, signature_hex, timestamp),
    )
    assert response.status_code == 200
    assert response.json() == {"type": 1}


def test_interactions_rejects_bad_signature(monkeypatch) -> None:
    body = json.dumps({"type": 1}).encode()
    timestamp = str(int(time.time()))
    public_hex, _ = _keypair_and_sign(body, timestamp)
    monkeypatch.setenv("OPERATOR_ETL_DISCORD_PUBLIC_KEY", public_hex)
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10000")
    http_app._RATE_LIMIT = 10_000
    http_app._rate_counts.clear()

    client = TestClient(app)
    response = client.post(
        "/discord/interactions",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-Ed25519": "00" * 64,
            "X-Signature-Timestamp": timestamp,
        },
    )
    assert response.status_code == 401


def test_interactions_guild_allowlist(monkeypatch, gov_settings) -> None:
    monkeypatch.setenv("OPERATOR_ETL_DISCORD_GUILD_ID", "allowed-guild")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10000")
    http_app._RATE_LIMIT = 10_000
    http_app._rate_counts.clear()
    _user_hits.clear()

    payload = {
        "type": 2,
        "guild_id": "other-guild",
        "channel_id": "ch-1",
        "member": {"user": {"id": "u-1"}},
        "data": {"name": "kpis", "options": []},
    }
    body = json.dumps(payload).encode()
    timestamp = str(int(time.time()))
    public_hex, signature_hex = _keypair_and_sign(body, timestamp)
    monkeypatch.setenv("OPERATOR_ETL_DISCORD_PUBLIC_KEY", public_hex)

    client = TestClient(app)
    response = client.post(
        "/discord/interactions",
        content=body,
        headers=_signed_headers(body, public_hex, signature_hex, timestamp),
    )
    assert response.status_code == 200
    assert "not allowlisted" in response.json()["data"]["content"].lower()


def test_interactions_etl_subcommand_kpis(monkeypatch, gov_settings) -> None:
    monkeypatch.setenv("OPERATOR_ETL_DISCORD_GUILD_ID", "g1")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10000")
    http_app._RATE_LIMIT = 10_000
    http_app._rate_counts.clear()
    _user_hits.clear()

    payload = {
        "type": 2,
        "guild_id": "g1",
        "channel_id": "c1",
        "member": {"user": {"id": "u-2"}},
        "data": {
            "name": "etl",
            "options": [
                {
                    "type": 1,
                    "name": "kpis",
                    "options": [{"name": "domain", "type": 3, "value": "gov"}],
                }
            ],
        },
    }
    body = json.dumps(payload).encode()
    timestamp = str(int(time.time()))
    public_hex, signature_hex = _keypair_and_sign(body, timestamp)
    monkeypatch.setenv("OPERATOR_ETL_DISCORD_PUBLIC_KEY", public_hex)

    with patch(
        "operator_etl_chat.discord.commands.get_gold_metrics",
        return_value={"comment_count": 10, "docket_count": 2},
    ):
        client = TestClient(app)
        response = client.post(
            "/discord/interactions",
            content=body,
            headers=_signed_headers(body, public_hex, signature_hex, timestamp),
        )
    assert response.status_code == 200
    content = response.json()["data"]["content"]
    assert "comment_count" in content
    assert response.json()["data"]["flags"] == 64
