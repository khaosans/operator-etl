#!/usr/bin/env bash
# Offline Terraform checks for gcp / aws / azure — no cloud credentials required.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STACKS=(gcp aws azure)

if ! command -v terraform >/dev/null 2>&1; then
  echo "terraform not found; install Terraform >= 1.5" >&2
  exit 1
fi

for stack in "${STACKS[@]}"; do
  dir="$ROOT/infra/$stack"
  echo "== validate_infra: $stack =="
  (cd "$dir" && terraform fmt -check -recursive)
  (cd "$dir" && terraform init -backend=false -input=false >/dev/null)
  (cd "$dir" && terraform validate -no-color)
  echo "OK $stack"
done

echo "OPERATOR_ETL_INFRA_VALIDATE=PASS"
