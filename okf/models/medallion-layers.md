---
type: OperatingModel
title: Medallion layers
description: Bronze, silver, gold, and quarantine — audit trail by design
tags: [warehouse, duckdb, bigquery]
timestamp: 2026-08-17T00:00:00Z
---

# Medallion layers

| Layer | Purpose | Mutability |
|---|---|---|
| **Bronze** | Raw payload preserved as JSON | Append-only |
| **Silver** | Pydantic-validated typed rows | Upsert per content hash |
| **Gold** | SQL aggregate marts | Rebuilt from silver |
| **Quarantine** | Rejected rows + error reason | Append-only audit |

**Idempotency:** SHA-256 content hash in `ingest_files` — safe at-least-once ingest.

**Local:** DuckDB file at `warehouse/operator.duckdb` (gitignored).

**GCP:** BigQuery datasets `etl_bronze_*`, `etl_silver_*`, `etl_quarantine_*`, `etl_gold_*`.

Gold SQL lives in [`sql/marts/`](/sql/marts/) (orders) and [`sql/marts/gov/`](/sql/marts/gov/) (FOIA).
