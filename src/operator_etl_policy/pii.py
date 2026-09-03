from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

_PRESIDIO_ENTITY_MAP = {
    "EMAIL_ADDRESS": "EMAIL",
    "PHONE_NUMBER": "PHONE",
    "US_SSN": "US_SSN",
    "PERSON": "PERSON",
    "LOCATION": "LOCATION",
}


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


def pii_scanner_backend() -> str:
    """regex (default) | presidio | auto (presidio if installed)."""
    return os.environ.get("OPERATOR_ETL_PII_SCANNER", "regex").strip().lower() or "regex"


def _regex_scan(text: str) -> list[tuple[str, float]]:
    hits: list[tuple[str, float]] = []
    if EMAIL.search(text):
        hits.append(("EMAIL", 0.95))
    if PHONE.search(text):
        hits.append(("PHONE", 0.90))
    if SSN.search(text):
        hits.append(("US_SSN", 0.92))
    return hits


def _presidio_available() -> bool:
    try:
        import presidio_analyzer  # noqa: F401
    except ImportError:
        return False
    return True


def _presidio_scan(text: str) -> list[tuple[str, float]]:
    from presidio_analyzer import AnalyzerEngine

    analyzer = AnalyzerEngine()
    results = analyzer.analyze(text=text, language="en")
    hits: list[tuple[str, float]] = []
    for item in results:
        entity = _PRESIDIO_ENTITY_MAP.get(item.entity_type, item.entity_type)
        hits.append((entity, float(item.score)))
    return hits


def scan_text(text: str, column: str = "body") -> list[tuple[str, float]]:
    """Return list of (entity_type, confidence) found in text."""
    backend = pii_scanner_backend()
    use_presidio = backend == "presidio" or (backend == "auto" and _presidio_available())
    if use_presidio:
        if not _presidio_available():
            raise ImportError(
                "OPERATOR_ETL_PII_SCANNER=presidio requires: uv sync --extra presidio"
            )
        return _presidio_scan(text)
    return _regex_scan(text)


def scan_records(records: list[dict[str, str]], text_columns: list[str] | None = None) -> PiiScanResult:
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


def extract_pii_values(text: str) -> list[tuple[str, str]]:
    """Return (entity_type, raw_value) pairs for vault tokenization (regex patterns)."""
    found: list[tuple[str, str]] = []
    for match in EMAIL.finditer(text):
        found.append(("EMAIL", match.group()))
    for match in PHONE.finditer(text):
        found.append(("PHONE", match.group()))
    for match in SSN.finditer(text):
        found.append(("US_SSN", match.group()))
    return found


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
