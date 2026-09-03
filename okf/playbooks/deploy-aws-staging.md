---
type: Playbook
title: Deploy AWS staging
description: Terraform path for S3 + ECS Fargate + RDS Operator ETL staging
tags: [aws, terraform]
timestamp: 2026-09-03T00:00:00Z
---

# Deploy AWS staging

## Prerequisites

- AWS account + credentials
- Terraform >= 1.5
- Local MVP: `./scripts/verify.sh`

## Steps

1. Configure Terraform:
   ```bash
   cd infra/aws
   cp terraform.tfvars.example terraform.tfvars
   # set pii_vault_key and openai_api_key (REPLACE_ME* rejected)
   terraform init && terraform apply
   ```
2. Build and push image (`CLOUD_EXTRA=aws`) to the ECR URL from outputs.
3. Upload a CSV to `s3://$inbox_bucket/incoming/` or `POST /run` against the ALB URL.
4. Keep insight backend `template` until the OpenAI secret is real. See [docs/LLM.md](/docs/LLM.md).

## Skill

[`skills/operator-ship-aws/SKILL.md`](/skills/operator-ship-aws/SKILL.md) · Wiki: [docs/MULTI-CLOUD.md](/docs/MULTI-CLOUD.md)
