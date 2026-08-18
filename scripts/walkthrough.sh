#!/usr/bin/env bash
# Post-demo warehouse inspection — companion to docs/WALKTHROUGH.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WAREHOUSE="${ROOT}/.tmp/mvp-demo/operator.duckdb"

inspect_warehouse() {
  uv run python - <<PY
import duckdb
con = duckdb.connect("${WAREHOUSE}")
print("== layer counts ==")
print(con.execute("""
  SELECT 'silver' AS layer, COUNT(*) AS n FROM silver_comments
  UNION ALL SELECT 'quarantine', COUNT(*) FROM quarantine_comments
  UNION ALL SELECT 'pii_flagged', COUNT(*) FROM silver_comments WHERE pii_detected
""").fetchdf().to_string(index=False))
print("")
print("== gold_comment_kpis ==")
print(con.execute("SELECT * FROM gold_comment_kpis").fetchdf().to_string(index=False))
print("")
print("== latest insight ==")
row = con.execute("SELECT text FROM insights ORDER BY created_at DESC LIMIT 1").fetchone()
print(row[0] if row else "(none)")
con.close()
PY
}

if [[ "${1:-}" == "--inspect-only" ]]; then
  if [[ ! -f "${WAREHOUSE}" ]]; then
    echo "No demo warehouse at ${WAREHOUSE}. Run: ./scripts/verify.sh" >&2
    exit 1
  fi
else
  echo "== Running FOIA demo (fresh warehouse) =="
  ./scripts/demo_mvp.sh
fi

echo ""
echo "== Warehouse inspection: ${WAREHOUSE} =="
inspect_warehouse

echo ""
echo "== Dashboard =="
echo "export OPERATOR_ETL_WAREHOUSE=\"${WAREHOUSE}\""
echo "export OPERATOR_ETL_PIPELINE_NAME=public_comments"
echo "export OPERATOR_ETL_DOMAIN=gov"
echo "uv run streamlit run dashboard/app.py"
echo ""
echo "Open the Gov / FOIA tab. See docs/WALKTHROUGH.md for full steps."
