"""SPIFFE JWT-SVID auth — unit + HTTP integration.

RSA key material is generated at test time (never committed) so gitleaks stays clean.
"""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from operator_etl_gcp.http import mcp_app
from operator_etl_gcp.http.app import app
from operator_etl_policy import spiffe_auth

TRIGGER_ID = "spiffe://operator-etl.test/ns/operator-etl/sa/trigger-scheduler"
MCP_ID = "spiffe://operator-etl.test/ns/operator-etl/sa/mcp"
A2A_ID = "spiffe://operator-etl.test/ns/operator-etl/sa/a2a-client"
OTHER_ID = "spiffe://operator-etl.test/ns/operator-etl/sa/ingest"
_KID = "test-spiffe-1"


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


@pytest.fixture(scope="module")
def spiffe_keys(tmp_path_factory: pytest.TempPathFactory) -> tuple[bytes, Path]:
    """Ephemeral RSA private key + JWKS path for this test module."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    pub = key.public_key().public_numbers()
    n = pub.n.to_bytes((pub.n.bit_length() + 7) // 8, "big")
    e = pub.e.to_bytes((pub.e.bit_length() + 7) // 8, "big")
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "kid": _KID,
                "use": "sig",
                "alg": "RS256",
                "n": _b64u(n),
                "e": _b64u(e),
            }
        ]
    }
    root = tmp_path_factory.mktemp("spiffe")
    jwks_path = root / "jwks.json"
    jwks_path.write_text(json.dumps(jwks), encoding="utf-8")
    return priv_pem, jwks_path


def _mint(priv_pem: bytes, spiffe_id: str, *, expired: bool = False) -> str:
    key = serialization.load_pem_private_key(priv_pem, password=None)
    now = int(time.time())
    payload = {
        "sub": spiffe_id,
        "iat": now - 5,
        "exp": now - 60 if expired else now + 600,
        "aud": "operator-etl",
    }
    return jwt.encode(payload, key, algorithm="RS256", headers={"kid": _KID})


@pytest.fixture(autouse=True)
def _clear_jwks_cache():
    spiffe_auth.clear_trust_bundle_cache()
    yield
    spiffe_auth.clear_trust_bundle_cache()


def _spiffe_env(monkeypatch: pytest.MonkeyPatch, jwks_path: Path) -> None:
    monkeypatch.setenv("OPERATOR_ETL_AUTH_MODE", "spiffe")
    monkeypatch.setenv("OPERATOR_ETL_SPIFFE_TRUST_BUNDLE", str(jwks_path))
    monkeypatch.setenv("OPERATOR_ETL_SPIFFE_ALLOW_RUN", TRIGGER_ID)
    monkeypatch.setenv("OPERATOR_ETL_SPIFFE_ALLOW_MCP", MCP_ID)
    monkeypatch.setenv("OPERATOR_ETL_SPIFFE_ALLOW_A2A", A2A_ID)
    monkeypatch.setenv("OPERATOR_ETL_SPIFFE_AUDIENCE", "operator-etl")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10000")


def test_verify_jwt_svid_accepts_valid_token(
    monkeypatch: pytest.MonkeyPatch, spiffe_keys: tuple[bytes, Path]
) -> None:
    priv_pem, jwks_path = spiffe_keys
    _spiffe_env(monkeypatch, jwks_path)
    token = _mint(priv_pem, TRIGGER_ID)
    assert spiffe_auth.verify_jwt_svid(token) == TRIGGER_ID


def test_verify_jwt_svid_rejects_expired(
    monkeypatch: pytest.MonkeyPatch, spiffe_keys: tuple[bytes, Path]
) -> None:
    priv_pem, jwks_path = spiffe_keys
    _spiffe_env(monkeypatch, jwks_path)
    token = _mint(priv_pem, TRIGGER_ID, expired=True)
    with pytest.raises(Exception) as exc:
        spiffe_auth.verify_jwt_svid(token)
    assert getattr(exc.value, "status_code", None) == 401


def test_run_open_when_auth_mode_off(gov_settings, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPERATOR_ETL_AUTH_MODE", raising=False)
    monkeypatch.setattr("operator_etl_gcp.http.app._gov_settings", lambda pipeline: gov_settings)
    monkeypatch.setattr(
        "operator_etl_gcp.http.app.run_graph",
        lambda *, source, settings: {
            "run_id": "r1",
            "status": "complete",
            "rows_in": 0,
            "rows_silver": 0,
            "rows_quarantined": 0,
            "critic_passed": True,
            "insight_draft": "",
            "errors": [],
        },
    )
    client = TestClient(app)
    response = client.post(
        "/run",
        json={"source": "public_comments", "pipeline": "public_comments"},
    )
    assert response.status_code == 200


def test_run_requires_svid_when_spiffe(
    gov_settings, monkeypatch: pytest.MonkeyPatch, spiffe_keys: tuple[bytes, Path]
) -> None:
    priv_pem, jwks_path = spiffe_keys
    _spiffe_env(monkeypatch, jwks_path)
    monkeypatch.setattr("operator_etl_gcp.http.app._gov_settings", lambda pipeline: gov_settings)
    monkeypatch.setattr(
        "operator_etl_gcp.http.app.run_graph",
        lambda *, source, settings: {
            "run_id": "r2",
            "status": "complete",
            "rows_in": 0,
            "rows_silver": 0,
            "rows_quarantined": 0,
            "critic_passed": True,
            "insight_draft": "",
            "errors": [],
        },
    )
    client = TestClient(app)
    denied = client.post(
        "/run",
        json={"source": "public_comments", "pipeline": "public_comments"},
    )
    assert denied.status_code == 401

    wrong = client.post(
        "/run",
        headers={"Authorization": f"Bearer {_mint(priv_pem, OTHER_ID)}"},
        json={"source": "public_comments", "pipeline": "public_comments"},
    )
    assert wrong.status_code == 401

    ok = client.post(
        "/run",
        headers={"Authorization": f"Bearer {_mint(priv_pem, TRIGGER_ID)}"},
        json={"source": "public_comments", "pipeline": "public_comments"},
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "complete"


def test_azure_validation_exempt_blob_requires_svid(
    gov_settings, monkeypatch: pytest.MonkeyPatch, spiffe_keys: tuple[bytes, Path]
) -> None:
    priv_pem, jwks_path = spiffe_keys
    _spiffe_env(monkeypatch, jwks_path)
    monkeypatch.setattr("operator_etl_gcp.http.app._gov_settings", lambda pipeline: gov_settings)
    monkeypatch.setattr(
        "operator_etl_gcp.http.app.run_graph",
        lambda *, source, settings: {"status": "complete", "run_id": "run-az"},
    )
    client = TestClient(app)
    validation = client.post(
        "/events/azure",
        json=[
            {
                "id": "validation-1",
                "eventType": "Microsoft.EventGrid.SubscriptionValidationEvent",
                "data": {"validationCode": "code-xyz"},
            }
        ],
    )
    assert validation.status_code == 200
    assert validation.json() == {"validationResponse": "code-xyz"}

    blob = [
        {
            "id": "blob-1",
            "eventType": "Microsoft.Storage.BlobCreated",
            "data": {"url": "https://example.blob.core.windows.net/inbox/incoming/a.csv"},
        }
    ]
    assert client.post("/events/azure", json=blob).status_code == 401
    ok = client.post(
        "/events/azure",
        headers={"Authorization": f"Bearer {_mint(priv_pem, TRIGGER_ID)}"},
        json=blob,
    )
    assert ok.status_code == 200
    assert ok.json()["run_id"] == "run-az"


def test_mcp_http_requires_svid(
    monkeypatch: pytest.MonkeyPatch, spiffe_keys: tuple[bytes, Path]
) -> None:
    priv_pem, jwks_path = spiffe_keys
    _spiffe_env(monkeypatch, jwks_path)
    monkeypatch.setattr(
        "operator_etl_gcp.http.mcp_app.get_gold_metrics",
        lambda con, domain="gov": {"comment_count": 10},
    )
    monkeypatch.setattr(
        "operator_etl_gcp.http.mcp_app.connect",
        lambda settings: type("C", (), {"close": lambda self: None})(),
    )
    monkeypatch.setattr(
        "operator_etl_gcp.http.mcp_app.get_settings",
        lambda: object(),
    )
    client = TestClient(mcp_app.app)
    assert client.get("/tools/gold-metrics").status_code == 401
    assert (
        client.get(
            "/tools/gold-metrics",
            headers={"Authorization": f"Bearer {_mint(priv_pem, MCP_ID)}"},
        ).status_code
        == 200
    )


def test_a2a_spiffe_and_bearer_or_spiffe(
    monkeypatch: pytest.MonkeyPatch, spiffe_keys: tuple[bytes, Path]
) -> None:
    priv_pem, jwks_path = spiffe_keys
    _spiffe_env(monkeypatch, jwks_path)
    monkeypatch.setenv("OPERATOR_ETL_A2A_BEARER_TOKEN", "shared-secret")
    # SPIFFE-only: shared bearer rejected
    with pytest.raises(Exception) as exc:
        spiffe_auth.require_identity("a2a", authorization="Bearer shared-secret")
    assert getattr(exc.value, "status_code", None) == 401

    assert (
        spiffe_auth.require_identity(
            "a2a", authorization=f"Bearer {_mint(priv_pem, A2A_ID)}"
        )
        == A2A_ID
    )

    monkeypatch.setenv("OPERATOR_ETL_AUTH_MODE", "bearer_or_spiffe")
    assert spiffe_auth.require_identity("a2a", authorization="Bearer shared-secret") is None
    assert (
        spiffe_auth.require_identity(
            "a2a", authorization=f"Bearer {_mint(priv_pem, A2A_ID)}"
        )
        == A2A_ID
    )
