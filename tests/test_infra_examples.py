"""Infra example hygiene — no assigned secret values in committed env examples."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_EXAMPLES = [
    ROOT / "infra" / "env.example",
    ROOT / "infra" / "env.aws.example",
    ROOT / "infra" / "env.azure.example",
]

# Assigned values look like secrets to gitleaks; examples must comment these out.
_SECRET_ASSIGN = re.compile(r"^(PII_VAULT_KEY|OPENAI_API_KEY)\s*=\s*\S+", re.MULTILINE)


def test_env_examples_do_not_assign_secret_values() -> None:
    for path in ENV_EXAMPLES:
        text = path.read_text(encoding="utf-8")
        match = _SECRET_ASSIGN.search(text)
        assert match is None, f"{path} must not assign {match.group(1)} (comment only)"
        assert "PII_VAULT_KEY" in text
        assert "OPENAI_API_KEY" in text
