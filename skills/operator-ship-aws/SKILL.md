---
name: operator-ship-aws
description: >-
  Deploy Operator ETL to AWS — Terraform (S3, EventBridge, ECS Fargate, RDS),
  Docker with --extra aws. Use for AWS staging/production L2.
---

# Ship Operator ETL to AWS

**Load:** [deploy-aws-staging.md](../../okf/playbooks/deploy-aws-staging.md) and [infra/aws/README.md](../../infra/aws/README.md)

## Prerequisites

- Local MVP green: `./scripts/verify.sh`
- AWS account + credentials; Terraform >= 1.5

## Terraform

```bash
cd infra/aws
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform apply
```

## Image

```bash
docker build --build-arg CLOUD_EXTRA=aws -t operator-etl:aws .
```

## Non-negotiables

- Set real `pii_vault_key` / `openai_api_key` (no `REPLACE_ME*`)
- Keep `OPERATOR_ETL_INSIGHT_BACKEND=template` until the OpenAI secret is real
- Never auto-publish FOIA releases
- Portable skill: [operator-ship-portable](../operator-ship-portable/SKILL.md)
