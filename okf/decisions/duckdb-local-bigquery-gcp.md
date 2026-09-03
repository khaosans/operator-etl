---
type: Decision
title: DuckDB local, BigQuery GCP
description: ADR-005 — same medallion pattern, dialect-adjusted marts in production
tags: [adr, gcp, duckdb]
timestamp: 2026-08-17T00:00:00Z
---

# DuckDB local → BigQuery GCP

**Decision:** Develop and prove MVP on DuckDB file; lift to BigQuery datasets in GCP for staging/prod.

**When to lift:** After `./harness/e2e.sh` green locally and Terraform applied.

**Mapping:**

| Local | GCP |
|---|---|
| `warehouse/operator.duckdb` | `etl_*` BigQuery datasets |
| SqliteSaver | PostgresSaver (Cloud SQL) |
| stdio MCP | HTTP MCP on Cloud Run |
| `drops/inbox/` | GCS inbox bucket |

**Env switch:** `OPERATOR_ETL_BACKEND=bigquery` + project/dataset env vars. See [`infra/env.example`](/infra/env.example).

**Portability:** Core uses warehouse / object-store protocols so other clouds can add adapters without rewriting the pipeline. See [cloud-portable-adapters](/decisions/cloud-portable-adapters.md).

**Not yet complete:** Gold mart SQL dialect translation for BigQuery (PARTIAL).
