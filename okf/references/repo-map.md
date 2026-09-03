---
type: Reference
title: Repository map
description: Where code, SQL, tests, and infra live
tags: [repo]
timestamp: 2026-09-03T00:00:00Z
---

# Repo map

```
src/operator_etl/           Data plane — extract, load, transform, CLI, checkpoints
src/operator_etl_graph/     LangGraph control plane
src/operator_etl_policy/    PII + budgets
src/operator_etl_mcp/       MCP stdio server
src/operator_etl_gcp/       GCP adapters — BigQuery, GCS, Cloud Run HTTP
src/operator_etl_aws/       AWS adapters — S3 ObjectStore
src/operator_etl_azure/     Azure adapters — Blob ObjectStore
src/a2a/                    A2A JSON-RPC task surface
src/telemetry/              OpenTelemetry / OpenInference (no raw PII)
pipelines/                  Source registry YAML
sql/marts/                  Gold SQL (orders)
sql/marts/gov/              Gold SQL (FOIA)
sql/allowlist.yaml          MCP SQL whitelist
samples/                    Demo CSV + HTTP JSON
tests/                      pytest (76)
evals/                      Golden eval definitions
infra/gcp/                  GCP Terraform (reference + BigQuery)
infra/aws/                  AWS Terraform (L2 S3/ECS/RDS)
infra/azure/                Azure Terraform (L2 Blob/ACA/Postgres)
docs/                       White paper, FOIA guide, share pack
okf/                        Knowledge bundle (this tree)
skills/                     Agent skills
harness/                    e2e gate + multi-session templates
scripts/                    verify.sh, walkthrough.sh, demo_mvp.sh, okf_validate.py, share_pack.sh
```
