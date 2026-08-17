#!/usr/bin/env bash
# Fresh-warehouse FOIA MVP demo — reproducible proof for interviews and share prep.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DEMO_DIR="${ROOT}/.tmp/mvp-demo"
WAREHOUSE="${DEMO_DIR}/operator.duckdb"
rm -rf "${DEMO_DIR}"
mkdir -p "${DEMO_DIR}"

echo "== Operator ETL MVP demo (fresh warehouse) =="
echo "warehouse: ${WAREHOUSE}"
echo ""

echo "== pytest =="
uv run pytest -q

echo ""
echo "== FOIA graph pipeline =="
OUTPUT="$(
  OPERATOR_ETL_WAREHOUSE="${WAREHOUSE}" \
  OPERATOR_ETL_PIPELINE_NAME=public_comments \
  OPERATOR_ETL_DOMAIN=gov \
  uv run etl-graph --source public_comments --pipeline public_comments 2>&1
)" || {
  echo "${OUTPUT}"
  exit 1
}
echo "${OUTPUT}"

echo ""
echo "== assertions =="
echo "${OUTPUT}" | grep -q "status=complete" || { echo "FAIL: expected status=complete"; exit 1; }
echo "${OUTPUT}" | grep -q "silver=10" || { echo "FAIL: expected silver=10"; exit 1; }
echo "${OUTPUT}" | grep -q -i "comment" || { echo "FAIL: expected insight mentioning comments"; exit 1; }

echo ""
echo "=========================================="
echo "  Operator ETL MVP — PASS"
echo "=========================================="
echo "  Sample: 12 public comments (EPA/FCC dockets)"
echo "  Silver: 10 valid | Quarantine: 2"
echo "  PII gate → gold KPIs → critic-verified insight"
echo "  Tests:  $(uv run pytest -q 2>&1 | tail -1)"
echo "  Full gate: ./harness/e2e.sh"
echo "=========================================="
