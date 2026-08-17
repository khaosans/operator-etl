---
type: Reference
title: Design foundations and proof matrix
description: Authoritative sources mapped to invariants, code paths, and tests
tags: [foundations, references, proof, tests]
timestamp: 2026-08-17T00:00:00Z
---

# Design foundations

Human-readable version: [docs/FOUNDATIONS.md](../../docs/FOUNDATIONS.md)

## Proof matrix (agent quick reference)

| Invariant | Ref | Code | Test |
|---|---|---|---|
| Medallion layers | [1] | `operator_etl/` | `tests/test_pipeline.py` |
| Idempotent ingest | [2] | `ingest_files` hash | `tests/test_pipeline.py` |
| Graph orchestration | [3] | `operator_etl_graph/` | `tests/test_gov_graph.py` |
| MCP allowlist | [4] | `operator_etl_mcp/` | `tests/test_mcp_tools.py` |
| PII fail-closed | [5] | `operator_etl_policy/pii.py` | `tests/test_pii.py` |
| Quality gate fail-closed | [6] | `quality_gate` | `tests/test_quality.py` |
| Critic faithfulness | [7] | `operator_etl_graph/critic.py` | `tests/test_critic.py` |
| Human sign-off | [8] | `agents-never-publish-prod.md` | policy + graph |
| FOIA domain | [9] | gov marts, FOIA guide | `scripts/demo_mvp.sh` |
| Limit LLM agency | [10] | MCP deny | `tests/test_mcp_tools.py` |

**Gate:** `make e2e` before share or deploy claims.

## References

1. Databricks Medallion Architecture — https://www.databricks.com/glossary/medallion-architecture
2. Kleppmann, DDIA Ch. 11 — idempotent consumers
3. LangGraph — https://langchain-ai.github.io/langgraph/
4. MCP spec — https://modelcontextprotocol.io/
5. NIST SP 800-122 — PII guide
6. Goodhart (1975) — quality gate rationale
7. Lewis et al. RAG (2020) — grounding via deterministic critic
8. NIST AI RMF 1.0 — human oversight
9. FOIA / 5 U.S.C. § 552 — https://www.foia.gov/
10. OWASP LLM Top 10 — excessive agency
