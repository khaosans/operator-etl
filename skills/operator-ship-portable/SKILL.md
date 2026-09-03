---
name: operator-ship-portable
description: >-
  Deploy Operator ETL on any cloud via the portable Docker + env contract.
  Use when targeting AWS, Azure, Kubernetes, or multi-cloud — not GCP-only Terraform.
---

# Ship Operator ETL (portable / any cloud)

**Load:** [deploy-container-any-cloud.md](../../okf/playbooks/deploy-container-any-cloud.md) and [cloud-portable-adapters.md](../../okf/decisions/cloud-portable-adapters.md)

## Prerequisites

- Local MVP green: `./scripts/verify.sh`
- Container runtime + secrets + (usually) Postgres

## What to do

1. Follow the any-cloud playbook — same image, portable env vars.
2. Use warehouse / object-store protocols; add provider adapters under optional extras — do not rewrite `operator_etl_graph`.
3. Map inbox events to HTTP `POST /run` (GCP Pub/Sub push is one adapter).

## Full GCP IaC

For Terraform + Cloud Build + BigQuery staging, use [operator-ship-gcp](../operator-ship-gcp/SKILL.md) instead.

## Non-negotiables

- Never publish FOIA releases automatically
- Never expose PII vault via MCP or logs
- Prove local e2e before promote
