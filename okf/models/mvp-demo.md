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

## Test file mapping

Full proof matrix: [docs/FOUNDATIONS.md](../../docs/FOUNDATIONS.md)

| Assertion | Defends | Test / script |
|---|---|---|
| Graph completes, critic passes | Graph orchestration [3] | `tests/test_gov_graph.py` |
| PII not in redacted output | PII fail-closed [5] | `tests/test_pii.py` |
| Hallucinated numbers rejected | Critic faithfulness [7] | `tests/test_critic.py` |
| MCP allowlist deny/permit | MCP allowlist [4, 10] | `tests/test_mcp_tools.py` |
| Idempotent ingest | Idempotent consumers [2] | `tests/test_pipeline.py` |
| Quality gate blocks bad KPIs | Goodhart / fail-closed [6] | `tests/test_quality.py` |
| Fresh warehouse E2E smoke | FOIA domain [9] | `scripts/demo_mvp.sh` |
| Full gate (OKF + pytest + demo) | All invariants | `harness/e2e.sh` / `make e2e` |

**CI:** GitHub Actions runs the same gate on every push — see README CI badge.

Step-by-step: [docs/WALKTHROUGH.md](../../docs/WALKTHROUGH.md)

**Orders demo** (interviews): `uv run etl run --source demo` — 21 rows, 17 silver, 4 quarantined.
