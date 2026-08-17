from __future__ import annotations

import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")


def assert_no_pii_leak(text: str) -> None:
    assert not EMAIL.search(text), "email leaked in insight"
    assert not PHONE.search(text), "phone leaked in insight"
