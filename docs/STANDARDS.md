# Standards and best practices

Operator ETL follows established patterns for agentic data systems, government FOIA workflows, and maintainable Python projects. This page is the single index — **plain English for each component:** [PATTERNS.md](PATTERNS.md). **Why each pattern matters and which test proves it:** [FOUNDATIONS.md](FOUNDATIONS.md).

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
| **Medallion architecture** | [PATTERNS.md](PATTERNS.md) · [FOUNDATIONS.md §1](FOUNDATIONS.md#references) — Databricks | Bronze (immutable) → silver (validated) → gold (aggregates) + quarantine |
| **Layer definitions** | [okf/models/medallion-layers.md](../okf/models/medallion-layers.md) | DuckDB local; BigQuery on GCP |
| **Idempotent ingest** | [FOUNDATIONS.md §2](FOUNDATIONS.md#references) — Kleppmann DDIA | SHA-256 in `ingest_files`; safe at-least-once delivery |
| **Fail-closed quality** | [FOUNDATIONS.md §6](FOUNDATIONS.md#references) — Goodhart; [pii-fail-closed.md](../okf/decisions/pii-fail-closed.md) | Withhold KPIs when gate fails |

---

## Agentic AI

| Standard | Reference | How we apply it |
|---|---|---|
| **Three planes** | [PATTERNS.md](PATTERNS.md#three-planes) · [okf/models/three-planes.md](../okf/models/three-planes.md) | Data / Policy / Control separation |
| **LangGraph** | [FOUNDATIONS.md §3](FOUNDATIONS.md#references) | Control plane in `operator_etl_graph/`; checkpoints for resume |
| **MCP** | [FOUNDATIONS.md §4, §10](FOUNDATIONS.md#references) | Allowlisted tools only — [okf/decisions/mcp-allowlist-only.md](../okf/decisions/mcp-allowlist-only.md) |
| **Critic / faithfulness** | [FOUNDATIONS.md §7](FOUNDATIONS.md#references) — grounded generation | Every insight number must exist in `gold_metrics` |
| **Agents never auto-publish** | [NIST.md](NIST.md) — AI RMF Govern | Human sign-off before FOIA release |

---

## NIST (alignment, not certification)

Readable mapping: **[NIST.md](NIST.md)**. We align selected practices. We do **not** claim NIST certification, FedRAMP, or an ATO.

| Standard | How we apply it |
|---|---|
| **AI RMF 1.0** (Govern / Map / Measure / Manage) | Never auto-publish; gold JSON only to models; critic + `verify.sh`; template fallback + HITL |
| **AI 600-1** Generative AI Profile | Confabulation → critic; privacy → no bronze to the model; oversight → HITL; agency → MCP allowlist. Other 600-1 categories are out of scope |
| **SP 800-122** | PII scan before insight; encrypted vault; no MCP vault access |
| **Privacy Framework 1.0** | Identify/protect PII in the comment pipeline (not a full privacy program) |
| **SP 800-53 Rev. 5** | Analogies only (AU / AC / SC / SI) — **not** an ATO overlay |

---

## Security and compliance

| Standard | Reference | How we apply it |
|---|---|---|
| **PII fail-closed** | [NIST.md](NIST.md) · [FOUNDATIONS.md §5](FOUNDATIONS.md#references) | Scan before insight; encrypted vault; no MCP vault access |
| **FOIA workflow** | [FOUNDATIONS.md §9](FOUNDATIONS.md#references) | Public comments intake and redaction queue |
| **Secrets hygiene** | [SECURITY.md](../SECURITY.md) | No `.env`, vault, or tfvars in git |
| **Least privilege (GCP)** | White paper §12.3 | Separate service accounts per workload in Terraform |
| **OWASP input validation** | [SECURITY-HARDENING.md](SECURITY-HARDENING.md) | Pydantic `max_length`, 10 MB body cap, path traversal guard |
| **SAST** | bandit | [`.github/workflows/security.yml`](../.github/workflows/security.yml) + `.bandit.yml`; `# nosec` only with a reason |
| **SCA** | pip-audit | Frozen-dep CVE check in the same Security workflow |
| **Secret scanning** | gitleaks | [`.github/workflows/secret-scan.yml`](../.github/workflows/secret-scan.yml) |
| **CODEOWNERS** | [CODEOWNERS](../CODEOWNERS) | `vault.py`, `pii.py`, `secrets.tf`, `iam.tf` require review |

Human how-to: [SECURITY-HARDENING.md](SECURITY-HARDENING.md). Agent checklist: [operator-security](https://github.com/khaosans/operator-etl/blob/master/skills/operator-security/SKILL.md).

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
| **Proof gate** | [FOUNDATIONS.md](FOUNDATIONS.md) proof matrix | `make e2e` before share, deploy, or scale claims — see [WALKTHROUGH.md](WALKTHROUGH.md) |
| **CI** | GitHub Actions | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) — e2e + Docker; [`.github/workflows/security.yml`](../.github/workflows/security.yml) — bandit + pip-audit |

---

## Implementation status

What is coded vs specified: [okf/models/implementation-status.md](../okf/models/implementation-status.md)

Update that matrix when shipping features; sync white paper badges on major releases.
