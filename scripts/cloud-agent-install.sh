#!/usr/bin/env bash
# Cloud Agent / environment-build install: ensure uv, then frozen sync.
# Must terminate. Do not start Streamlit or other long-running services here.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "== cloud-agent-install: uv missing — installing via astral.sh =="
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "FAIL: uv not on PATH after install. Expected ${HOME}/.local/bin/uv" >&2
  exit 1
fi

echo "== cloud-agent-install: $(uv --version) =="
uv sync --frozen --extra dev
echo "== cloud-agent-install: done =="
