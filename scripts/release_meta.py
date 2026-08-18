#!/usr/bin/env python3
"""Validate a git tag against pyproject.toml and emit GitHub Release notes.

Used by .github/workflows/release.yml. Stdlib only (Python 3.12 / tomllib).

Tag form (SemVer): v0.5.0 or v0.5.0-beta.1
pyproject PEP 440:  0.5.0 or 0.5.0b1
CHANGELOG heading:  ## [0.5.0-beta.1] — YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"

PRE_RE = re.compile(
    r"^v?(?P<base>\d+\.\d+\.\d+)(?:-(?P<pre>alpha|beta|rc)\.(?P<n>\d+))?$",
    re.IGNORECASE,
)


def normalize_tag(raw: str | None) -> str:
    """Accept v0.5.0, refs/tags/v0.5.0, or GITHUB_REF."""
    tag = (raw or "").strip()
    if tag.startswith("refs/tags/"):
        tag = tag.removeprefix("refs/tags/")
    return tag


def parse_tag(raw: str) -> tuple[str, str, str, bool]:
    """Return (display_version, pep440, docker_tag, is_prerelease)."""
    tag = normalize_tag(raw)
    match = PRE_RE.fullmatch(tag)
    if not match:
        raise SystemExit(
            f"Unsupported tag {raw!r}. Use vX.Y.Z or vX.Y.Z-beta.N (also alpha/rc)."
        )
    base = match.group("base")
    pre = (match.group("pre") or "").lower()
    n = match.group("n")
    if not pre:
        return base, base, base, False
    pep_letter = {"alpha": "a", "beta": "b", "rc": "rc"}[pre]
    pep440 = f"{base}{pep_letter}{n}"
    display = f"{base}-{pre}.{n}"
    return display, pep440, display, True


def pyproject_version(path: Path | None = None) -> str:
    """Read version from PEP 621 [project] or Poetry [tool.poetry]."""
    target = path or PYPROJECT
    with target.open("rb") as fh:
        data = tomllib.load(fh)
    version = data.get("project", {}).get("version")
    if not version:
        version = data.get("tool", {}).get("poetry", {}).get("version")
    if not version:
        raise SystemExit(
            f"No version found in {target}. Expected [project].version "
            "or [tool.poetry].version."
        )
    return str(version)


def changelog_section(
    display_version: str,
    pep440: str,
    path: Path | None = None,
) -> str:
    target = path or CHANGELOG
    text = target.read_text(encoding="utf-8")
    for heading in (display_version, pep440):
        pattern = rf"^## \[{re.escape(heading)}\][^\n]*\n"
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            continue
        start = match.end()
        nxt = re.search(r"^## \[", text[start:], re.MULTILINE)
        body = text[start : start + nxt.start() if nxt else None].strip()
        heading_line = match.group(0).strip()
        return f"{heading_line}\n\n{body}\n".strip() + "\n"
    snippet = text[:400].rstrip()
    raise SystemExit(
        f"{target.name} has no ## [{display_version}] (or [{pep440}]) section. "
        "Cut a release PR that moves [Unreleased] into that heading before tagging.\n"
        f"Found top of file:\n\n{snippet}\n"
    )


def write_github_output(mapping: dict[str, str]) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as fh:
        for key, value in mapping.items():
            if "\n" in value:
                fh.write(f"{key}<<EOF\n{value.rstrip()}\nEOF\n")
            else:
                fh.write(f"{key}={value}\n")


def resolve_tag_arg(cli_tag: str | None) -> str:
    return normalize_tag(
        cli_tag or os.environ.get("GITHUB_REF_NAME") or os.environ.get("GITHUB_REF")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tag",
        nargs="?",
        default=None,
        help="Git tag (default: GITHUB_REF_NAME, then GITHUB_REF)",
    )
    parser.add_argument(
        "--notes-file",
        type=Path,
        help="Write CHANGELOG section here (default: stdout if not in Actions)",
    )
    args = parser.parse_args()
    tag = resolve_tag_arg(args.tag)
    if not tag:
        print("Pass a tag or set GITHUB_REF_NAME / GITHUB_REF", file=sys.stderr)
        return 2

    display, pep440, docker_tag, is_prerelease = parse_tag(tag)
    pkg = pyproject_version()
    if pkg != pep440:
        raise SystemExit(
            f"Tag {tag} maps to PEP 440 {pep440!r} but pyproject.toml "
            f"version is {pkg!r}. They must match before publish."
        )
    notes = changelog_section(display, pep440)
    if args.notes_file:
        args.notes_file.write_text(notes, encoding="utf-8")
    elif not os.environ.get("GITHUB_OUTPUT"):
        sys.stdout.write(notes)

    write_github_output(
        {
            "display_version": display,
            "pep440": pep440,
            "docker_tag": docker_tag,
            "prerelease": "true" if is_prerelease else "false",
            "notes": notes,
        }
    )
    print(
        f"release_meta: tag={tag} pep440={pep440} "
        f"prerelease={is_prerelease} docker={docker_tag}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
