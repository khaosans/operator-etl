"""PII vault crypto round-trip — never exposed via MCP."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from cryptography.fernet import Fernet

from operator_etl.config import Settings, set_settings
from operator_etl_policy.vault import PiiVault, _load_or_create_key


def test_vault_tokenize_detokenize_round_trip(tmp_path: Path) -> None:
    key = Fernet.generate_key()
    vault = PiiVault(key=key, path=tmp_path / "pii_vault.json")
    token = vault.tokenize("jane@example.com", "EMAIL")
    assert token.startswith("EMAIL_")
    assert vault.detokenize(token) == "jane@example.com"
    assert vault.count() == 1


def test_vault_persists_across_instances(tmp_path: Path) -> None:
    key = Fernet.generate_key()
    path = tmp_path / "pii_vault.json"
    first = PiiVault(key=key, path=path)
    token = first.tokenize("614-555-0199", "PHONE")
    second = PiiVault(key=key, path=path)
    assert second.count() == 1
    assert second.detokenize(token) == "614-555-0199"


def test_vault_detokenize_unknown_raises(tmp_path: Path) -> None:
    vault = PiiVault(key=Fernet.generate_key(), path=tmp_path / "pii_vault.json")
    try:
        vault.detokenize("EMAIL_missing")
        raise AssertionError("expected KeyError")
    except KeyError as exc:
        assert "unknown vault token" in str(exc)


def test_vault_key_created_with_0600(tmp_path: Path) -> None:
    key_path = tmp_path / ".vault_key"
    key = _load_or_create_key(key_path)
    assert key_path.exists()
    mode = stat.S_IMODE(key_path.stat().st_mode)
    assert mode == 0o600
    assert _load_or_create_key(key_path) == key


def test_vault_json_written_0600(tmp_path: Path) -> None:
    path = tmp_path / "pii_vault.json"
    vault = PiiVault(key=Fernet.generate_key(), path=path)
    vault.tokenize("secret@example.com", "EMAIL")
    mode = stat.S_IMODE(path.stat().st_mode)
    assert mode == 0o600


def test_vault_restricts_permissive_existing_key(tmp_path: Path) -> None:
    key_path = tmp_path / ".vault_key"
    key = Fernet.generate_key()
    key_path.write_bytes(key)
    os.chmod(key_path, 0o644)
    loaded = _load_or_create_key(key_path)
    assert loaded == key
    assert stat.S_IMODE(key_path.stat().st_mode) == 0o600


def test_pii_gate_tokenizes_into_vault(tmp_path: Path) -> None:
    settings = Settings(
        root=tmp_path,
        warehouse=tmp_path / "operator.duckdb",
        domain="gov",
        pipeline_name="public_comments",
    )
    set_settings(settings)
    (tmp_path / "warehouse").mkdir(parents=True, exist_ok=True)
    from operator_etl_graph.nodes import pii_gate_node

    out = pii_gate_node(
        {
            "run_id": "r1",
            "source": "public_comments",
            "domain": "gov",
            "_records": [{"body": "Contact jane@example.com", "subject": "hi"}],
        }
    )
    assert out["pii_findings"]
    vault = PiiVault(path=tmp_path / "warehouse" / "pii_vault.json")
    assert vault.count() >= 1
    set_settings(None)
