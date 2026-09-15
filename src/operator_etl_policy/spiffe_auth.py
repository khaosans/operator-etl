"""SPIFFE JWT-SVID verification for Control-plane HTTP surfaces.

Local MVP defaults to OPERATOR_ETL_AUTH_MODE=off. Staging/prod should use
``spiffe`` (or ``bearer_or_spiffe`` during A2A cutover). Never trust a bare
``X-SPIFFE-ID`` header without verifying the JWT-SVID signature.
"""

from __future__ import annotations

import json
import os
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import jwt
from fastapi import Header, HTTPException, status
from jwt import PyJWKSet


class AuthMode(StrEnum):
    OFF = "off"
    BEARER = "bearer"
    SPIFFE = "spiffe"
    BEARER_OR_SPIFFE = "bearer_or_spiffe"


RouteKind = Literal["run", "mcp", "a2a"]

_ALLOW_ENV: dict[RouteKind, str] = {
    "run": "OPERATOR_ETL_SPIFFE_ALLOW_RUN",
    "mcp": "OPERATOR_ETL_SPIFFE_ALLOW_MCP",
    "a2a": "OPERATOR_ETL_SPIFFE_ALLOW_A2A",
}


def get_auth_mode() -> AuthMode:
    raw = (os.getenv("OPERATOR_ETL_AUTH_MODE") or "off").strip().lower()
    try:
        return AuthMode(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Invalid OPERATOR_ETL_AUTH_MODE={raw!r}",
        ) from exc


def _parse_allowlist(raw: str | None) -> frozenset[str]:
    if not raw:
        return frozenset()
    return frozenset(part.strip() for part in raw.split(",") if part.strip())


def allowlist_for(route: RouteKind) -> frozenset[str]:
    return _parse_allowlist(os.getenv(_ALLOW_ENV[route]))


def _trust_bundle_text() -> str:
    raw = (os.getenv("OPERATOR_ETL_SPIFFE_TRUST_BUNDLE") or "").strip()
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPERATOR_ETL_SPIFFE_TRUST_BUNDLE not configured",
        )
    path = Path(raw)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return raw


@lru_cache(maxsize=4)
def _jwk_set_from_text(text: str) -> PyJWKSet:
    data = json.loads(text)
    if "keys" not in data:
        raise ValueError("trust bundle must be a JWKS object with a keys array")
    return PyJWKSet.from_dict(data)


def clear_trust_bundle_cache() -> None:
    """Test helper — drop cached JWKS after env changes."""
    _jwk_set_from_text.cache_clear()


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None
    token = authorization[len(prefix) :].strip()
    return token or None


def _signing_keys(jwks: PyJWKSet, token: str) -> list[Any]:
    """Prefer kid match; otherwise try all keys in the set."""
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        ) from exc
    kid = header.get("kid")
    keys = list(jwks.keys)
    if kid is not None:
        matched = [k for k in keys if getattr(k, "key_id", None) == kid]
        if matched:
            return matched
    return keys


def verify_jwt_svid(token: str) -> str:
    """Verify a JWT-SVID and return the SPIFFE ID from ``sub``."""
    try:
        jwks = _jwk_set_from_text(_trust_bundle_text())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SPIFFE trust bundle unavailable",
        ) from exc

    audience = (os.getenv("OPERATOR_ETL_SPIFFE_AUDIENCE") or "").strip() or None
    decode_kwargs: dict[str, Any] = {
        "algorithms": ["RS256", "ES256", "EdDSA"],
        "options": {"require": ["sub", "exp"]},
    }
    if audience:
        decode_kwargs["audience"] = audience
    else:
        decode_kwargs["options"] = {
            **decode_kwargs["options"],
            "verify_aud": False,
        }

    last_error: Exception | None = None
    for jwk in _signing_keys(jwks, token):
        try:
            claims = jwt.decode(token, jwk.key, **decode_kwargs)
            spiffe_id = str(claims.get("sub") or "")
            if not spiffe_id.startswith("spiffe://"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )
            return spiffe_id
        except HTTPException:
            raise
        except jwt.PyJWTError as exc:
            last_error = exc
            continue

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    ) from last_error


def spiffe_id_allowed(spiffe_id: str, route: RouteKind) -> bool:
    allowed = allowlist_for(route)
    if not allowed:
        return False
    return spiffe_id in allowed


def _a2a_shared_bearer_ok(authorization: str | None) -> bool:
    expected = os.getenv("OPERATOR_ETL_A2A_BEARER_TOKEN")
    if not expected:
        return False
    return authorization == f"Bearer {expected}"


def require_identity(
    route: RouteKind,
    *,
    authorization: str | None = Header(default=None),
) -> str | None:
    """Enforce auth for ``route``. Prefer ``depends_identity(route)`` in FastAPI."""
    mode = get_auth_mode()

    if route == "a2a":
        if mode in (AuthMode.OFF, AuthMode.BEARER):
            if _a2a_shared_bearer_ok(authorization):
                return None
            if not os.getenv("OPERATOR_ETL_A2A_BEARER_TOKEN"):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="A2A bearer token not configured",
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )
        if mode == AuthMode.BEARER_OR_SPIFFE:
            if _a2a_shared_bearer_ok(authorization):
                return None
            token = _bearer_token(authorization)
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )
            spiffe_id = verify_jwt_svid(token)
            if not spiffe_id_allowed(spiffe_id, "a2a"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )
            return spiffe_id
        # AuthMode.SPIFFE
        token = _bearer_token(authorization)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )
        spiffe_id = verify_jwt_svid(token)
        if not spiffe_id_allowed(spiffe_id, "a2a"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )
        return spiffe_id

    # run / mcp
    if mode in (AuthMode.OFF, AuthMode.BEARER):
        return None

    token = _bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    spiffe_id = verify_jwt_svid(token)
    if not spiffe_id_allowed(spiffe_id, route):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return spiffe_id


def depends_identity(route: RouteKind):
    """Return a FastAPI dependency that enforces auth for ``route``."""

    def _dep(authorization: str | None = Header(default=None)) -> str | None:
        return require_identity(route, authorization=authorization)

    return _dep
