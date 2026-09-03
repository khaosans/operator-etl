#!/usr/bin/env python3
"""Enforce package-level coverage floors for policy / graph / MCP."""
from __future__ import annotations

import json
import sys
from pathlib import Path

THRESHOLDS = {
    "operator_etl_policy": 80.0,
    "operator_etl_graph": 80.0,
    "operator_etl_mcp": 80.0,
}


def main() -> int:
    report = Path("coverage.json")
    if not report.exists():
        print("coverage.json missing — run: make coverage", file=sys.stderr)
        return 2
    data = json.loads(report.read_text())
    failed = False
    for pkg, floor in THRESHOLDS.items():
        summaries = [
            meta["summary"]
            for path, meta in data["files"].items()
            if f"/{pkg}/" in path.replace("\\", "/")
        ]
        covered = sum(s["covered_lines"] + s.get("covered_branches", 0) for s in summaries)
        total = sum(s["num_statements"] + s.get("num_branches", 0) for s in summaries)
        pct = (100.0 * covered / total) if total else 0.0
        status = "OK" if pct >= floor else "FAIL"
        print(f"{status} {pkg}: {pct:.1f}% (floor {floor:.0f}%)")
        if pct < floor:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
