---
type: OperatingModel
title: MVP demo expected results
description: Canonical numbers for FOIA sample — use in tests, demos, and share copy
tags: [mvp, foia, demo]
timestamp: 2026-08-17T00:00:00Z
---

# MVP demo — expected results

**Source:** `samples/public_comments.csv` via `public_comments` registry entry.

**Command:**

```bash
./scripts/demo_mvp.sh
# or full gate:
./harness/e2e.sh
```

| Metric | Expected |
|---|---|
| Bronze rows in | 12 |
| Silver comments | 10 |
| Quarantined | 2 (empty body, invalid date) |
| PII flagged | ≥ 4 |
| Graph status | `complete` |
| Critic | passed |
| Quality gate | pass (quarantine rate ≤ 35%) |

**Insight template cites:** comment count, docket count, agency count, PII flagged count, PII rate — all from `gold_comment_kpis`.

**Orders demo** (interviews): `uv run etl run --source demo` — 21 rows, 17 silver, 4 quarantined.
