---
type: Playbook
title: Run local MVP
description: Prove FOIA pipeline in under 2 minutes on a fresh warehouse
tags: [mvp, demo]
timestamp: 2026-08-17T00:00:00Z
---

# Run local MVP

**Full setup guide:** [docs/GETTING-STARTED.md](../../docs/GETTING-STARTED.md)

## Prerequisites

```bash
uv sync --extra dev
```

## Full proof gate

```bash
./harness/e2e.sh
```

Runs: OKF validate → pytest (29) → FOIA demo with fresh warehouse.

Step-by-step proof: [docs/WALKTHROUGH.md](../../docs/WALKTHROUGH.md)

## Demo only (skip OKF validate)

```bash
./scripts/demo_mvp.sh
```

## Expected output

- `status=complete`
- `silver=10`, `quarantined=2`
- Insight mentioning comments and FOIA redaction

## Visual check

```bash
OPERATOR_ETL_WAREHOUSE=.tmp/mvp-demo/operator.duckdb \
OPERATOR_ETL_PIPELINE_NAME=public_comments \
OPERATOR_ETL_DOMAIN=gov \
uv run streamlit run dashboard/app.py
```

Open **Gov / FOIA** tab.

See [MVP demo numbers](/models/mvp-demo.md).
