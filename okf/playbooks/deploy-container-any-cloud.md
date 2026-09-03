---
type: Playbook
title: Deploy container on any cloud
description: Run the Operator ETL Docker image on Cloud Run, ECS, Azure Container Apps, or Kubernetes with the same env contract
tags: [multi-cloud, docker, deploy]
timestamp: 2026-09-03T00:00:00Z
---

# Deploy container on any cloud

## Goal

Ship the same image ([`Dockerfile`](/Dockerfile)) wherever you have: a **container runtime**, **object storage** (inbox), **warehouse** (or keep DuckDB ephemeral), and **Postgres** (checkpoints). GCP Terraform remains the full IaC reference; other clouds map events to HTTP.

## Prerequisites

- Local MVP green: `./scripts/verify.sh` or `./harness/e2e.sh`
- Container registry + runtime (Cloud Run / ECS / ACA / K8s)
- Secrets store for `PII_VAULT_KEY` (and optional LLM key)

## Portable env contract

| Variable | Role |
|---|---|
| `OPERATOR_ETL_BACKEND` | `duckdb` or `bigquery` (reference warehouse) |
| `OPERATOR_ETL_CHECKPOINT_BACKEND` | `sqlite` or `postgres` |
| `OPERATOR_ETL_CHECKPOINT_DATABASE_URL` | Managed Postgres URL when using postgres |
| `OPERATOR_ETL_OBJECT_STORE_BACKEND` | `gcs` today; future `s3` / `azure` |
| `OPERATOR_ETL_INBOX_URI` | e.g. `gs://bucket/prefix` (portable inbox pointer) |
| `OPERATOR_ETL_GCS_INBOX_BUCKET` | Legacy GCP alias — still supported |
| `OPERATOR_ETL_DOMAIN` / `PIPELINE_NAME` | Usually `gov` / `public_comments` |

Provider-specific fields (`OPERATOR_ETL_GCP_PROJECT`, region, BQ datasets) apply only when using the GCP adapters. Full example: [`infra/env.example`](/infra/env.example).

## Steps

1. Build the image from repo root (`docker build` or Cloud Build).
2. Run the graph HTTP entry (`operator_etl_gcp.http.app:app` today) with the env contract above.
3. Point object-store inbox + warehouse adapters at your cloud (GCS/BigQuery on GCP; add adapters for others).
4. Map cloud events to HTTP — GCS→Pub/Sub→`/pubsub/push` is the GCP trigger adapter. On AWS/Azure/K8s, invoke `POST /run` (or equivalent) from EventBridge / Event Grid / CronJob. **Do not change graph nodes.**
5. Keep MCP gold-read allowlist and never auto-publish FOIA releases.

## GCP full stack

When you need Terraform + Pub/Sub + BigQuery: [deploy-gcp-staging](/playbooks/deploy-gcp-staging.md) · skill [`operator-ship-gcp`](/skills/operator-ship-gcp/SKILL.md).

## Skill

Agents: [`skills/operator-ship-portable/SKILL.md`](/skills/operator-ship-portable/SKILL.md).
