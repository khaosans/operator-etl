from __future__ import annotations

import re

_NUMBER = re.compile(r"\b\d+(?:\.\d+)?\b")


def extract_numbers(text: str) -> list[float]:
    return [float(m.group()) for m in _NUMBER.finditer(text)]


def flatten_metrics(metrics: dict) -> list[float]:
    vals: list[float] = []
    for v in metrics.values():
        if isinstance(v, (int, float)):
            vals.append(float(v))
        elif isinstance(v, dict):
            vals.extend(flatten_metrics(v))
    return vals


def fuzzy_match(n: float, allowed: list[float], tol: float = 0.015) -> bool:
    for a in allowed:
        if abs(n - a) <= tol:
            return True
        if a != 0 and abs((n - a) / a) <= tol:
            return True
    return False


def critic_check(insight_draft: str, gold_metrics: dict) -> tuple[bool, list[str]]:
    numbers = extract_numbers(insight_draft)
    allowed = flatten_metrics(gold_metrics)
    violations = [str(int(n)) if n == int(n) else str(n) for n in numbers if not fuzzy_match(n, allowed)]
    return len(violations) == 0, violations
