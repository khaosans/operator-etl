---
type: Playbook
title: Deploy Azure staging
description: Terraform path for Blob + Container Apps + Postgres Operator ETL staging
tags: [azure, terraform]
timestamp: 2026-09-03T00:00:00Z
---

# Deploy Azure staging

## Prerequisites

- Azure subscription + `az login`
- Terraform >= 1.5
- Local MVP: `./scripts/verify.sh`

## Steps

1. Configure Terraform:
   ```bash
   cd infra/azure
   cp terraform.tfvars.example terraform.tfvars
   # set pii_vault_key and openai_api_key (REPLACE_ME* rejected)
   terraform init && terraform apply
   ```
2. Build and push image (`CLOUD_EXTRA=azure`) to ACR.
3. Upload a blob under `incoming/` or `POST /run` / Event Grid → `/events/azure`.
4. Keep insight backend `template` until the OpenAI secret is real. See [docs/LLM.md](/docs/LLM.md).

## Skill

[`skills/operator-ship-azure/SKILL.md`](/skills/operator-ship-azure/SKILL.md) · Wiki: [docs/MULTI-CLOUD.md](/docs/MULTI-CLOUD.md)
