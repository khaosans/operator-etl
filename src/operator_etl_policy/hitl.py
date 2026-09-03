"""HITL officer approve/reject audit trail — never auto-publish."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from operator_etl.config import Settings, get_settings

DecisionKind = Literal["approve", "reject"]


@dataclass(frozen=True)
class HitlDecision:
    run_id: str
    decision: DecisionKind
    reason: str
    officer: str
    decided_at: str
    insight_id: str | None = None


class HitlStore:
    """Append-only JSON audit of officer sign-offs before publish."""

    def __init__(self, path: Path | None = None, settings: Settings | None = None):
        settings = settings or get_settings()
        self.path = path or settings.root / "warehouse" / "hitl_audit.json"
        self._rows: list[dict] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            self._rows = list(raw) if isinstance(raw, list) else []

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._rows, indent=2))

    def decide(
        self,
        run_id: str,
        decision: DecisionKind,
        *,
        reason: str = "",
        officer: str = "officer",
        insight_id: str | None = None,
    ) -> HitlDecision:
        if decision not in ("approve", "reject"):
            raise ValueError("decision must be approve or reject")
        row = HitlDecision(
            run_id=run_id,
            decision=decision,
            reason=reason,
            officer=officer,
            decided_at=datetime.now(UTC).replace(tzinfo=None).isoformat(),
            insight_id=insight_id,
        )
        self._rows.append(asdict(row))
        self._save()
        return row

    def latest_for_run(self, run_id: str) -> HitlDecision | None:
        for row in reversed(self._rows):
            if row.get("run_id") == run_id:
                return HitlDecision(**row)
        return None

    def is_approved(self, run_id: str) -> bool:
        latest = self.latest_for_run(run_id)
        return latest is not None and latest.decision == "approve"

    def list_decisions(self) -> list[HitlDecision]:
        return [HitlDecision(**row) for row in self._rows]
