---
type: OperatingModel
title: Implementation status matrix
description: Source of truth for IMPLEMENTED vs SPECIFIED — update when code ships
tags: [status, roadmap]
timestamp: 2026-08-17T00:00:00Z
---

# Implementation status

**Tests:** 24/24 pytest passing · **MVP gate:** `./harness/e2e.sh`

| Component | Status | Path |
|---|---|---|
| Bronze/silver/gold ETL | **IMPLEMENTED** | `src/operator_etl/` |
| Quarantine + quality gate | **IMPLEMENTED** | `src/operator_etl/insights/` |
| FOIA gov transform | **IMPLEMENTED** | `src/operator_etl/transform/gov_*` |
| LangGraph pipeline | **IMPLEMENTED** | `src/operator_etl_graph/` |
| PII scan + vault | **IMPLEMENTED** | `src/operator_etl_policy/` |
| Critic faithfulness | **IMPLEMENTED** | `src/operator_etl_graph/critic.py` |
| MCP allowlisted tools | **IMPLEMENTED** | `src/operator_etl_mcp/` |
| Sqlite checkpoints | **IMPLEMENTED** | `operator_etl_gcp/checkpoints.py` |
| GCP Terraform scaffold | **IMPLEMENTED** | `infra/terraform/` |
| BigQuery adapter | **PARTIAL** | `src/operator_etl_gcp/load/bigquery.py` |
| Cloud Run HTTP entry | **IMPLEMENTED** | `src/operator_etl_gcp/http/` |
| Postgres checkpoints | **IMPLEMENTED** | optional via env |
| LLM insight nodes | **SPECIFIED** | templates today |
| Presidio PII | **SPECIFIED** | regex scanner shipped |
| HITL dashboard | **PARTIAL** | gov tab in Streamlit |
| Regulations.gov API | **SPECIFIED** | — |
| BQ gold mart dialect | **PARTIAL** | DuckDB SQL; BQ lift pending |
| Public GitHub | **SPECIFIED** | repo stays private |

Update this file when status changes; sync [`docs/Operator-ETL-White-Paper.md`](/docs/Operator-ETL-White-Paper.md) badges on major releases.
