#!/usr/bin/env python3
"""OKF v0.1 §9 conformance checker (minimal).

Usage:
  python3 scripts/okf_validate.py okf [--strict]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RESERVED = {"index.md", "log.md"}
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
TYPE_RE = re.compile(r"(?m)^type:\s*(.+?)\s*$")
DATE_HEADING_RE = re.compile(r"(?m)^##\s+(\d{4}-\d{2}-\d{2})\s*$")


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str | None]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, "missing YAML frontmatter delimited by ---"
    block = m.group(1)
    data: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        data[key.strip()] = val.strip().strip('"').strip("'")
    return data, None


def validate_index(path: Path, text: str, is_root: bool, strict: bool) -> list[str]:
    errors: list[str] = []
    has_fm = text.startswith("---")
    if has_fm:
        if not is_root:
            errors.append(f"{path}: index.md must not have frontmatter (except bundle root)")
        else:
            data, err = parse_frontmatter(text)
            if err:
                errors.append(f"{path}: {err}")
            elif data is not None and "okf_version" not in data and strict:
                errors.append(f"{path}: root index should declare okf_version")
    if "# " not in text and strict:
        errors.append(f"{path}: index.md should include at least one markdown heading section")
    return errors


def validate_log(path: Path, text: str, strict: bool) -> list[str]:
    errors: list[str] = []
    if text.startswith("---"):
        errors.append(f"{path}: log.md must not have frontmatter")
    dates = DATE_HEADING_RE.findall(text)
    if strict and not dates:
        errors.append(f"{path}: log.md should use ## YYYY-MM-DD date headings")
    return errors


def validate_concept(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    data, err = parse_frontmatter(text)
    if err:
        return [f"{path}: {err}"]
    assert data is not None
    type_val = data.get("type", "").strip()
    if not type_val:
        m = FRONTMATTER_RE.match(text)
        if m and not TYPE_RE.search(m.group(1)):
            errors.append(f"{path}: frontmatter missing required non-empty `type`")
        elif not type_val:
            errors.append(f"{path}: frontmatter missing required non-empty `type`")
    return errors


def walk_bundle(root: Path, strict: bool) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"bundle path not found: {root}"]

    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        name = path.name
        is_root_index = rel.parts == ("index.md",)

        if name == "index.md":
            errors.extend(validate_index(path, text, is_root=is_root_index, strict=strict))
            continue
        if name == "log.md":
            errors.extend(validate_log(path, text, strict=strict))
            continue
        if name in RESERVED:
            continue
        errors.extend(validate_concept(path, text))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="OKF v0.1 §9 validator")
    parser.add_argument("bundle", type=Path, help="Path to OKF bundle (e.g. okf)")
    parser.add_argument("--strict", action="store_true", help="Extra soft-guidance checks")
    args = parser.parse_args()

    errors = walk_bundle(args.bundle.resolve(), strict=args.strict)
    if errors:
        print(f"OKF validation FAILED ({len(errors)} issue(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    n = sum(1 for _ in args.bundle.resolve().rglob("*.md"))
    print(f"OKF validation OK — {n} markdown files under {args.bundle}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
