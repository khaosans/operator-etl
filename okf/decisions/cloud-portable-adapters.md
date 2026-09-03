---
type: Decision
title: Cloud-portable adapters
description: ADR — GCP is the reference cloud; core uses warehouse and object-store protocols so other clouds add adapters without rewriting the pipeline
tags: [adr, multi-cloud, portability]
timestamp: 2026-09-03T00:00:00Z
---

# Cloud-portable adapters

**Decision:** Keep medallion / graph / policy cloud-agnostic. Cloud providers plug in through adapters behind portable protocols. **GCP is the reference implementation** (BigQuery + GCS + Cloud Run Terraform).

**Interfaces (core):**

| Protocol | Package | Reference adapter |
|---|---|---|
| Warehouse | `operator_etl.load.protocol` + `load.ops` | DuckDB (local), BigQuery (`operator_etl_gcp`) |
| Object store inbox | `operator_etl.extract.object_store` | GCS (`GcsObjectStore`) |
| Checkpoints | `operator_etl.checkpoints` | sqlite \| postgres (any managed Postgres) |

**Rules:**

1. Core packages never hard-require Google (or AWS/Azure) SDKs — only optional extras.
2. Provider IaC lives under `infra/<provider>/` (today: `infra/terraform/` = GCP).
3. Adding a second cloud = implement Warehouse + ObjectStore (+ event → HTTP `/run`) — do not fork the graph.
4. Env contract is portable: warehouse backend, checkpoint URL, inbox URI / object-store backend, secrets.

**Not in scope of this ADR:** shipping AWS/Azure Terraform or non-BigQuery warehouses. See [deploy-container-any-cloud](/playbooks/deploy-container-any-cloud.md).

**Related:** [DuckDB local, BigQuery GCP](/decisions/duckdb-local-bigquery-gcp.md) remains the warehouse lift path on the reference cloud.
