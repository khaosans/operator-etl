---
name: operator-ship-gcp
description: >-
  Deploy Operator ETL to GCP — Terraform, Docker, Cloud Build, Cloud Run, BigQuery.
  Use when lifting from local DuckDB MVP to staging/production infrastructure.
---

# Ship Operator ETL to GCP

**Load:** [deploy-gcp-staging.md](../../okf/playbooks/deploy-gcp-staging.md) and [infra/README.md](../../infra/README.md)

## Prerequisites

- Local MVP green: `./harness/e2e.sh`
- GCP project + APIs enabled

## Terraform

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform apply
```

## Build + deploy

```bash
gcloud builds submit --config cloudbuild.yaml
```

## Env vars

Copy [infra/env.example](../../infra/env.example) — set `OPERATOR_ETL_BACKEND=bigquery`, datasets, checkpoint URL. Optional LLM: [docs/LLM.md](../../docs/LLM.md) (`OPERATOR_ETL_INSIGHT_BACKEND` stays `template` until the OpenAI secret is real).

## Non-negotiables

- Set `pii_vault_key` and `openai_api_key` in `terraform.tfvars` (sensitive variables with validation — placeholders are rejected)
- MCP service account: gold dataset read only (see Terraform IAM)
- Never skip local e2e before promote
