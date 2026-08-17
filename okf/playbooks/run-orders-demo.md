---
type: Playbook
title: Run orders demo
description: Commerce pipeline for interviews — deterministic ETL without graph
tags: [demo, orders]
timestamp: 2026-08-17T00:00:00Z
---

# Run orders demo

## Command

```bash
uv run etl run --source demo
```

Uses [`pipelines/demo.yaml`](/pipelines/demo.yaml) and [`samples/orders.csv`](/samples/orders.csv).

## Expected

| Metric | Value |
|---|---|
| Input rows | 21 |
| Silver orders | 17 |
| Quarantined | 4 |
| Quality gate | pass (~19% quarantine) |

## Dashboard

```bash
uv run etl dashboard
```

**Orders** tab shows KPIs, volume chart, top SKUs.

## When to use

Interview walkthrough of medallion ETL without agentic layer. FOIA MVP is the primary hero demo.
