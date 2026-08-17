#!/usr/bin/env bash
# Regenerate share PDFs and copy to docs/share/latest/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

STAMP="$(date +%Y%m%d)"
DEST="${ROOT}/docs/share/latest"
ARCHIVE="${ROOT}/docs/share/releases/${STAMP}"

echo "== Share pack build =="

echo "== Install PDF deps =="
uv sync --extra dev 2>/dev/null || uv sync --extra dev
uv pip install reportlab 2>/dev/null || pip install reportlab

echo "== Regenerate PDFs =="
uv run python docs/build_one_pager_pdf.py
uv run python docs/build_whitepaper_pdf.py
if [[ -f docs/build_slides_pdf.py ]]; then
  uv run python docs/build_slides_pdf.py 2>/dev/null || echo "(slides build skipped)"
fi

echo "== Copy to share bundle =="
rm -rf "${DEST}"
mkdir -p "${DEST}" "${ARCHIVE}"

for f in \
  docs/Operator-ETL-White-Paper.pdf \
  docs/Operator-ETL-One-Pager.pdf \
  docs/Operator-ETL-Slides.pdf \
  docs/Operator-ETL-Proposal.pdf
do
  if [[ -f "$f" ]]; then
    cp "$f" "${DEST}/"
    cp "$f" "${ARCHIVE}/"
  fi
done

# Symlink-friendly README in bundle
cp docs/share/README.md "${DEST}/README.md" 2>/dev/null || true

echo ""
echo "Share pack ready:"
echo "  ${DEST}/"
ls -la "${DEST}/"
