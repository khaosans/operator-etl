#!/usr/bin/env bash
# Post-demo warehouse inspection — companion to docs/WALKTHROUGH.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WAREHOUSE="${ROOT}/.tmp/mvp-demo/operator.duckdb"

if [[ "${1:-}" == "--inspect-only" ]]; then
  if [[ ! -f "${WAREHOUSE}" ]]; then
    echo "No demo warehouse at ${WAREHOUSE}. Run: make e2e" >&2
    exit 1
  fi
else
  echo "== Running FOIA demo (fresh warehouse) =="
  ./scripts/demo_mvp.sh
fi

echo ""
echo "== Warehouse inspection: ${WAREHOUSE} =="
duckdb "${WAREHOUSE}" -c "
  SELECT 'silver' AS layer, COUNT(*) AS n FROM silver_comments
  UNION ALL SELECT 'quarantine', COUNT(*) FROM quarantine_comments
  UNION ALL SELECT 'pii_flagged', COUNT(*) FROM silver_comments WHERE pii_detected;
"

echo ""
echo "== gold_comment_kpis =="
duckdb "${WAREHOUSE}" -c "SELECT * FROM gold_comment_kpis;"

echo ""
echo "== Latest insight =="
duckdb "${WAREHOUSE}" -c "SELECT text FROM insights ORDER BY created_at DESC LIMIT 1;"

echo ""
echo "== Dashboard =="
echo "export OPERATOR_ETL_WAREHOUSE=\"${WAREHOUSE}\""
echo "export OPERATOR_ETL_PIPELINE_NAME=public_comments"
echo "export OPERATOR_ETL_DOMAIN=gov"
echo "uv run streamlit run dashboard/app.py"
echo ""
echo "Open the Gov / FOIA tab. See docs/WALKTHROUGH.md for full steps."
