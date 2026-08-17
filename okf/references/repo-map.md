---
type: Reference
title: Repository map
description: Where code, SQL, tests, and infra live
tags: [repo]
timestamp: 2026-08-17T00:00:00Z
---

# Repo map

```
src/operator_etl/           Data plane — extract, load, transform, CLI
src/operator_etl_graph/     LangGraph control plane
src/operator_etl_policy/    PII + budgets
src/operator_etl_mcp/       MCP stdio server
src/operator_etl_gcp/       BigQuery, GCS, Cloud Run HTTP
pipelines/                  Source registry YAML
sql/marts/                  Gold SQL (orders)
sql/marts/gov/              Gold SQL (FOIA)
sql/allowlist.yaml          MCP SQL whitelist
samples/                    Demo CSV + HTTP JSON
tests/                      pytest (24)
evals/                      Golden eval definitions
infra/terraform/            GCP Terraform
docs/                       White paper, FOIA guide, share pack
okf/                        Knowledge bundle (this tree)
skills/                     Agent skills
harness/                    e2e gate + multi-session templates
scripts/                    demo_mvp.sh, okf_validate.py, share_pack.sh
```
