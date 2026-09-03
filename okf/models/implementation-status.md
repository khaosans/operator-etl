---
type: OperatingModel
title: Implementation status matrix
description: Source of truth for IMPLEMENTED vs SPECIFIED — update when code ships
tags: [status, roadmap]
timestamp: 2026-08-17T00:00:00Z
---

# Implementation status

**Tests:** 78 pytest passing · coverage fail_under=75 · **MVP gate:** `./harness/e2e.sh`

| Component | Status | Proven in CI | Path |
|---|---|---|---|
| Bronze/silver/gold ETL | **IMPLEMENTED** | Yes | `src/operator_etl/` |
| Quarantine + quality gate | **IMPLEMENTED** | Yes | `src/operator_etl/insights/` |
| FOIA gov transform | **IMPLEMENTED** | Yes | `src/operator_etl/transform/gov_*` |
| LangGraph pipeline | **IMPLEMENTED** | Yes | `src/operator_etl_graph/` |
| PII scan + vault | **IMPLEMENTED** | Yes | `src/operator_etl_policy/` |
| Critic faithfulness | **IMPLEMENTED** | Yes | `src/operator_etl_graph/critic.py` |
| MCP allowlisted tools | **IMPLEMENTED** | Yes | `src/operator_etl_mcp/` |
| HITL `needs_human` routes | **IMPLEMENTED** | Yes | `tests/test_gov_graph.py`, `test_critic.py` |
| Sqlite checkpoints | **IMPLEMENTED** | Yes | `operator_etl_gcp/checkpoints.py` |
| GCP Terraform scaffold | **IMPLEMENTED** | Unit only | `infra/terraform/` |
| BigQuery adapter | **IMPLEMENTED** | Unit + dialect | bronze + gold dialect; live optional (`-m integration`) |
| Cloud Run HTTP entry | **IMPLEMENTED** | Unit only | `src/operator_etl_gcp/http/` |
| Postgres checkpoints | **IMPLEMENTED** | Env config | optional via env |
| HITL dashboard | **IMPLEMENTED** | Yes | approve/reject audit + Streamlit + `etl hitl-*` |
| Product officer UX | **SPECIFIED** | — | responsive, streaming, gen UI — [docs/PRODUCT-UX.md](../../docs/PRODUCT-UX.md) |
| LLM insight nodes | **PARTIAL** | Mocked in CI | optional `llm`; laptop Ollama `llama3.2:3b` critic-passed; not CI |
| Presidio PII | **IMPLEMENTED** | Mocked path | `OPERATOR_ETL_PII_SCANNER=presidio` (`--extra presidio`) |
| Regulations.gov API | **IMPLEMENTED** | Offline fallback | `kind: regulations_gov` + sample fallback |
| BQ gold mart dialect | **IMPLEMENTED** | Dialect unit | `sql/marts/gov/bq/` + rewrite tests; live optional |
| Public GitHub | **IMPLEMENTED** | — | https://github.com/khaosans/operator-etl (Apache-2.0) |
| Path traversal guard | **IMPLEMENTED** | Yes | `src/operator_etl/extract/http.py`, `tests/test_http.py` |
| SAST / SCA CI | **IMPLEMENTED** | Yes | `.github/workflows/security.yml`, `.bandit.yml` |
| Vault file permissions | **IMPLEMENTED** | Yes | `src/operator_etl_policy/vault.py` (0600) |
| Rate limiting | **IMPLEMENTED** | Yes | `src/operator_etl_gcp/http/app.py` middleware |
| Input size limits | **IMPLEMENTED** | Yes | 10 MB body cap; Pydantic `max_length` |
| Terraform sensitive vars | **IMPLEMENTED** | — | `infra/terraform/secrets.tf` + `variables.tf` |

| Coverage fail_under | **IMPLEMENTED** | Yes | `make test` / demo_mvp (`fail_under=75` + package floors) |
| Cloud Monitoring alerts | **IMPLEMENTED** | Terraform | `infra/terraform/monitoring.tf` |
| Staging smoke checklist | **IMPLEMENTED** | Docs + workflow | `infra/README.md`, `.github/workflows/staging-e2e.yml` |
| Vault crypto tests | **IMPLEMENTED** | Yes | `tests/test_vault.py` |

Audit: [docs/FINAL-REVIEW.md](../../docs/FINAL-REVIEW.md)

Update this file when status changes; sync [`docs/Operator-ETL-White-Paper.md`](/docs/Operator-ETL-White-Paper.md) badges on major releases.
