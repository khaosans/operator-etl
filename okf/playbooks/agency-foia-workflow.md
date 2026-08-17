---
type: Playbook
title: Agency FOIA workflow
description: Map Operator ETL components to FOIA officer steps
tags: [foia, gov]
timestamp: 2026-08-17T00:00:00Z
---

# Agency FOIA workflow

Full guide: [`docs/FOIA-Public-Comments-Guide.md`](/docs/FOIA-Public-Comments-Guide.md)

| Agency step | Operator ETL |
|---|---|
| Receive comment export | `ingest` → bronze |
| PII review before release | `pii_gate` + vault |
| Reject malformed rows | `quarantine_comments` |
| Program summary | `insight` from gold only |
| Defensible numbers | `critic` verification |
| Audit trail | `pipeline_runs` + checkpoints |

**Run locally:** [Run local MVP](/playbooks/run-local-mvp.md)

**Do not** auto-publish releases — see [agents never publish prod](/decisions/agents-never-publish-prod.md).
