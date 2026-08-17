# Standards and best practices

Operator ETL follows established patterns for agentic data systems, government FOIA workflows, and maintainable Python projects. This page is the single index — detailed rationale lives in linked OKF concepts and the white paper.

---

## Knowledge and documentation

| Standard | Reference | How we apply it |
|---|---|---|
| **OKF v0.1** | [Google Knowledge Catalog OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) | [`okf/`](../okf/index.md) bundle with typed frontmatter; validate with `python3 scripts/okf_validate.py okf --strict` |
| **Progressive disclosure** | OKF `index.md` pattern | Root [`okf/index.md`](../okf/index.md) → playbooks → code |
| **README conventions** | [Make a README](https://www.makeareadme.com/) | Prerequisites, quick start, commands, doc map in [README.md](../README.md) |

---

## Data architecture

| Standard | Reference | How we apply it |
|---|---|---|
| **Medallion architecture** | Databricks medallion pattern | Bronze (immutable) → silver (validated) → gold (aggregates) + quarantine |
| **Layer definitions** | [okf/models/medallion-layers.md](../okf/models/medallion-layers.md) | DuckDB local; BigQuery on GCP |
| **Idempotent ingest** | Content-hash dedupe | SHA-256 in `ingest_files`; safe at-least-once delivery |
| **Fail-closed quality** | [okf/decisions/pii-fail-closed.md](../okf/decisions/pii-fail-closed.md) | Withhold KPIs when gate fails |

---

## Agentic AI

| Standard | Reference | How we apply it |
|---|---|---|
| **Three planes** | [okf/models/three-planes.md](../okf/models/three-planes.md) | Data / Policy / Control separation |
| **LangGraph** | [LangGraph docs](https://langchain-ai.github.io/langgraph/) | Control plane in `operator_etl_graph/`; checkpoints for resume |
| **MCP** | [Model Context Protocol](https://modelcontextprotocol.io/) | Allowlisted tools only — [okf/decisions/mcp-allowlist-only.md](../okf/decisions/mcp-allowlist-only.md) |
| **Critic / faithfulness** | Internal pattern | Every insight number must exist in `gold_metrics` |
| **Agents never auto-publish** | [okf/decisions/agents-never-publish-prod.md](../okf/decisions/agents-never-publish-prod.md) | Human sign-off before FOIA release |

---

## Security and compliance

| Standard | Reference | How we apply it |
|---|---|---|
| **PII fail-closed** | [okf/decisions/pii-fail-closed.md](../okf/decisions/pii-fail-closed.md) | Scan before insight; encrypted vault; no MCP vault access |
| **FOIA workflow** | [docs/FOIA-Public-Comments-Guide.md](FOIA-Public-Comments-Guide.md) | Public comments intake and redaction queue |
| **Secrets hygiene** | [SECURITY.md](../SECURITY.md) | No `.env`, vault, or tfvars in git |
| **Least privilege (GCP)** | White paper §12.3 | Separate service accounts per workload in Terraform |

---

## Engineering decisions (ADRs)

Documented in [docs/Operator-ETL-White-Paper.md](Operator-ETL-White-Paper.md) §3:

| ADR | Decision |
|---|---|
| ADR-001 | Medallion bronze / silver / gold |
| ADR-002 | LangGraph over implicit agent loops |
| ADR-003 | MCP as agent boundary |
| ADR-004 | Fail-closed quality gate |
| ADR-005 | DuckDB local → BigQuery GCP — [okf/decisions/duckdb-local-bigquery-gcp.md](../okf/decisions/duckdb-local-bigquery-gcp.md) |

---

## Python and repository

| Standard | Reference | How we apply it |
|---|---|---|
| **src layout** | [PyPA src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) | Packages under `src/` |
| **uv** | [Astral uv](https://docs.astral.sh/uv/) | `pyproject.toml` + `uv.lock` |
| **Proof gate** | Internal harness | `./harness/e2e.sh` before share/deploy claims |
| **CI** | GitHub Actions | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) — e2e + Docker build |

---

## Implementation status

What is coded vs specified: [okf/models/implementation-status.md](../okf/models/implementation-status.md)

Update that matrix when shipping features; sync white paper badges on major releases.
