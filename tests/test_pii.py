from __future__ import annotations

from unittest.mock import patch

from operator_etl_policy.pii import redact_text, scan_records


def test_scan_finds_email_and_phone():
    records = [{"body": "Contact jane@example.com or 614-555-0199"}]
    result = scan_records(records)
    types = {f.entity_type for f in result.findings}
    assert "EMAIL" in types
    assert "PHONE" in types


def test_redact_strips_pii():
    text = "Email me at jane@example.com"
    redacted = redact_text(text)
    assert "jane@example.com" not in redacted
    assert "REDACTED_EMAIL" in redacted


def test_eval_no_pii_in_redacted_insight():
    body = "Call 614-555-0199 or email foo@bar.com"
    redacted = redact_text(body)
    assert "614-555-0199" not in redacted
    assert "foo@bar.com" not in redacted


def test_ambiguous_confidence_flags_needs_human():
    records = [{"body": "maybe an email somewhere"}]

    def low_conf(text: str, column: str = "body"):
        return [("EMAIL", 0.50)]

    with patch("operator_etl_policy.pii.scan_text", side_effect=low_conf):
        result = scan_records(records)
    assert result.needs_human is True
    assert result.findings
