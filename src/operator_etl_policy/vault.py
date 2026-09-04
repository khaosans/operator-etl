from __future__ import annotations

import json
import logging
import os
import stat
from pathlib import Path

from cryptography.fernet import Fernet

from operator_etl.config import get_settings

logger = logging.getLogger(__name__)


class PiiVault:
    """Encrypted token store — never exposed via MCP."""

    def __init__(self, key: bytes | None = None, path: Path | None = None):
        settings = get_settings()
        self.path = path or settings.root / "warehouse" / "pii_vault.json"
        if key is None:
            key = _load_or_create_key(settings.root / "warehouse" / ".vault_key")
        self._fernet = Fernet(key)
        self._tokens: dict[str, str] = {}
        self._load()

    def tokenize(self, value: str, entity_type: str) -> str:
        import hashlib

        digest = hashlib.sha256(value.encode()).hexdigest()[:12]
        token = f"{entity_type}_{digest}"
        self._tokens[token] = self._fernet.encrypt(value.encode()).decode()
        self._save()
        return token

    def _load(self) -> None:
        if self.path.exists():
            self._tokens = json.loads(self.path.read_text())

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._tokens))
        os.chmod(self.path, stat.S_IRUSR | stat.S_IWUSR)

    def count(self) -> int:
        return len(self._tokens)


def _load_or_create_key(path: Path) -> bytes:
    if path.exists():
        mode = path.stat().st_mode
        if mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH):
            logger.warning(
                "Vault key %s has overly permissive permissions (%o), restricting to 0600",
                path,
                stat.S_IMODE(mode),
            )
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        return path.read_bytes()
    key = Fernet.generate_key()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, key)
    finally:
        os.close(fd)
    return key
