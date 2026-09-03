# Operator ETL — Executive One-Pager

**Agentic data intake for FOIA and public comments**

---

## The problem

Government agencies intake public comments and FOIA requests. Chatbots with database access fail on PII leakage, hallucinated counts, and non-auditable runs.

## The answer: three planes

| Plane | Role |
|---|---|
| **Data** | Deterministic bronze → silver → gold ETL (DuckDB local, BigQuery GCP) |
| **Policy** | PII scan, encrypted vault, fail-closed before any insight |
| **Control** | LangGraph orchestration, MCP allowlisted tools, critic verifies every number |

**Core claim:** Agents orchestrate. Python and SQL execute. Every insight number must exist in gold metrics.

---

## FOIA MVP (proven)

```bash
./harness/e2e.sh    # OKF + 59 tests + FOIA demo
```

| Metric | Result |
|---|---|
| Sample comments | 12 (EPA/FCC dockets) |
| Silver (valid) | 10 |
| Quarantined | 2 |
| PII flagged | 4+ |
| Critic | Pass — no hallucinated counts |

---

## Agentic best practices

- MCP allowlist — no raw SQL, no vault decrypt
- LangGraph checkpoints — resumable runs
- Quality gate — KPIs withheld when quarantine rate exceeds threshold
- Structured audit — `pipeline_runs` + graph state

---

## What's implemented vs next

| Now (IMPLEMENTED) | Next (PARTIAL / SPECIFIED) |
|---|---|
| Local DuckDB pipeline | BigQuery gold dialect lift |
| LangGraph + PII + critic | HITL officer dashboard |
| MCP stdio + HTTP scaffold | Regulations.gov adapter |
| GCP Terraform + Cloud Run | Production hardening |

---

## For adopters

1. **Prove:** `./harness/e2e.sh`
2. **Run:** `uv run etl-graph --source public_comments`
3. **Deploy:** `infra/terraform` + `cloudbuild.yaml`

Full engineering spec: *Operator-ETL-White-Paper.pdf*

**August 2026** · Operator ETL · Private repository — share PDFs only
