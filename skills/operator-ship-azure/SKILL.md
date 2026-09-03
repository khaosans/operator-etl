---
name: operator-ship-azure
description: >-
  Deploy Operator ETL to Azure — Terraform (Blob, Event Grid, Container Apps,
  Postgres), Docker with --extra azure. Use for Azure staging/production L2.
---

# Ship Operator ETL to Azure

**Load:** [deploy-azure-staging.md](../../okf/playbooks/deploy-azure-staging.md) and [infra/azure/README.md](../../infra/azure/README.md)

## Prerequisites

- Local MVP green: `./scripts/verify.sh`
- Azure subscription + `az login`; Terraform >= 1.5

## Terraform

```bash
cd infra/azure
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform apply
```

## Image

```bash
docker build --build-arg CLOUD_EXTRA=azure -t operator-etl:azure .
```

## Non-negotiables

- Set real `pii_vault_key` / `openai_api_key` (no `REPLACE_ME*`)
- Keep `OPERATOR_ETL_INSIGHT_BACKEND=template` until the OpenAI secret is real
- Never auto-publish FOIA releases
- Portable skill: [operator-ship-portable](../operator-ship-portable/SKILL.md)
