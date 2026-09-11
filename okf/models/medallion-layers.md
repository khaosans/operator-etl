---
type: OperatingModel
title: Medallion layers
description: Bronze, silver, gold, and quarantine — audit trail by design
tags: [warehouse, duckdb, bigquery]
timestamp: 2026-09-11T00:00:00Z
---

# Medallion layers

Product craft for Operator ETL. Fleet-wide DS contract (file hash vs business key vs entity fingerprint, insert-once + quarantine — not MERGE upsert) lives in platform OKF:

- `$AI_OPERATOR_INFRA_ROOT/okf/models/medallion-and-idempotency.md`

| Layer | Purpose | Mutability |
|---|---|---|
| **Bronze** | Raw payload preserved as JSON | Append-only; gated by `ingest_files.content_hash` (file bytes) |
| **Silver** | Pydantic-validated typed rows | Insert-once on business PK (`comment_id` / `order_id`); duplicate PK or `entity_fingerprint` → quarantine |
| **Gold** | SQL aggregate marts | Rebuilt from silver |
| **Quarantine** | Rejected rows + error reason | Append-only audit |

**Idempotency keys (keep distinct):**

1. **File hash** — SHA-256 in `ingest_files` — safe at-least-once ingest (same bytes → skip bronze).
2. **Business PK** — silver source identity; insert-once.
3. **`entity_fingerprint`** — `sha256(normalize(docket_id) || '\0' || normalize(body))` on `silver_comments` for semantic cross-delivery dupes.

**Local:** DuckDB file at `warehouse/operator.duckdb` (gitignored).

**GCP:** BigQuery datasets `etl_bronze_*`, `etl_silver_*`, `etl_quarantine_*`, `etl_gold_*`.

Gold SQL lives in [`sql/marts/`](/sql/marts/) (orders) and [`sql/marts/gov/`](/sql/marts/gov/) (FOIA).
