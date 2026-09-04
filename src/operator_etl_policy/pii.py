from __future__ import annotations

import re
from dataclasses import dataclass, field

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


@dataclass(frozen=True)
class PiiFinding:
    column: str
    entity_type: str
    count: int
    max_confidence: float


@dataclass
class PiiScanResult:
    findings: list[PiiFinding] = field(default_factory=list)
    needs_human: bool = False
    blocked: bool = False

    @property
    def has_pii(self) -> bool:
        return bool(self.findings)


def scan_text(text: str, column: str = "body") -> list[tuple[str, float]]:
    """Return list of (entity_type, confidence) found in text."""
    hits: list[tuple[str, float]] = []
    if EMAIL.search(text):
        hits.append(("EMAIL", 0.95))
    if PHONE.search(text):
        hits.append(("PHONE", 0.90))
    if SSN.search(text):
        hits.append(("US_SSN", 0.92))
    return hits


def scan_records(
    records: list[dict[str, str]], text_columns: list[str] | None = None
) -> PiiScanResult:
    text_columns = text_columns or ["body", "subject", "comment_text"]
    agg: dict[tuple[str, str], list[float]] = {}
    ambiguous = False

    for record in records:
        for col in text_columns:
            value = record.get(col, "")
            if not value:
                continue
            for entity, conf in scan_text(str(value), col):
                key = (col, entity)
                agg.setdefault(key, []).append(conf)
                if 0.40 <= conf < 0.85:
                    ambiguous = True

    findings = [
        PiiFinding(column=col, entity_type=entity, count=len(scores), max_confidence=max(scores))
        for (col, entity), scores in agg.items()
    ]
    return PiiScanResult(findings=findings, needs_human=ambiguous and bool(findings))


# token_prefix is a redaction label (REDACTED_EMAIL), not a password.
def redact_text(text: str, token_prefix: str = "REDACTED") -> str:  # nosec B107
    out = EMAIL.sub(f"{token_prefix}_EMAIL", text)
    out = PHONE.sub(f"{token_prefix}_PHONE", out)
    out = SSN.sub(f"{token_prefix}_SSN", out)
    return out


def redact_record(record: dict[str, str], text_columns: list[str] | None = None) -> dict[str, str]:
    text_columns = text_columns or ["body", "subject", "comment_text"]
    result = dict(record)
    for col in text_columns:
        if col in result and result[col]:
            result[col] = redact_text(str(result[col]))
    return result
