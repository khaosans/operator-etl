---
type: Playbook
title: Deploy GCP staging
description: Terraform + Cloud Build path for staging environment
tags: [gcp, terraform]
timestamp: 2026-08-17T00:00:00Z
---

# Deploy GCP staging

## Prerequisites

- GCP project with billing
- `gcloud` authenticated
- Terraform >= 1.5

## Steps

1. Enable APIs (see [`infra/README.md`](/infra/README.md))
2. Configure Terraform:
   ```bash
   cd infra/terraform
   cp terraform.tfvars.example terraform.tfvars
   terraform init && terraform apply
   ```
3. Replace Secret Manager placeholders (PII vault key, OpenAI key). Keep `OPERATOR_ETL_INSIGHT_BACKEND=template` until the OpenAI secret is real, then flip to `llm`. See [docs/LLM.md](/docs/LLM.md).
4. Build and deploy:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```
5. Upload test file:
   ```bash
   gsutil cp samples/public_comments.csv gs://INBOX/incoming/test.csv
   ```

## Verify

POST to graph-runner `/run` with identity token (see infra README).

**Local MVP must pass first:** `./harness/e2e.sh`
