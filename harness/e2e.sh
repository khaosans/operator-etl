#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== OKF validate =="
python3 scripts/okf_validate.py okf --strict

echo "== Skill frontmatter =="
fail=0
for skill in skills/*/SKILL.md; do
  if [[ ! -f "$skill" ]]; then
    continue
  fi
  if ! grep -q '^name:' "$skill"; then
    echo "missing name: in $skill" >&2
    fail=1
  fi
  if ! grep -q '^description:' "$skill"; then
    echo "missing description: in $skill" >&2
    fail=1
  fi
done
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

echo "== MVP demo =="
chmod +x scripts/demo_mvp.sh
./scripts/demo_mvp.sh

echo "e2e OK"
