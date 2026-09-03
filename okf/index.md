---
okf_version: "0.1"
---

# Operator ETL — knowledge bundle

Portable OKF knowledge for the **Operator ETL** agentic data intake system. Agents: start here, then open a skill under `skills/`.

**Humans:** [docs/QUICKSTART.md](../docs/QUICKSTART.md) (`./scripts/verify.sh`) then [docs/index.md](../docs/index.md) (wiki home).

# Publication

* [Operator ETL](publication/operator-etl.md) — Identity, audience, share policy

# Models

* [Three planes](models/three-planes.md) — Data / Policy / Control architecture
* [Medallion layers](models/medallion-layers.md) — Bronze / silver / gold / quarantine
* [MVP demo](models/mvp-demo.md) — Expected FOIA sample numbers
* [Implementation status](models/implementation-status.md) — IMPLEMENTED vs SPECIFIED matrix

# Decisions

* [Agents never publish prod](decisions/agents-never-publish-prod.md) — No auto-release to external systems
* [DuckDB local, BigQuery GCP](decisions/duckdb-local-bigquery-gcp.md) — ADR-005 summary
* [MCP allowlist only](decisions/mcp-allowlist-only.md) — No raw SQL, no vault decrypt
* [PII fail-closed](decisions/pii-fail-closed.md) — Scan before insight; HITL on ambiguity

# Playbooks

* [Run local MVP](playbooks/run-local-mvp.md) — 2-minute FOIA proof
* [Run orders demo](playbooks/run-orders-demo.md) — Commerce interview demo
* [Extend new source](playbooks/extend-new-source.md) — Registry pattern
* [Deploy GCP staging](playbooks/deploy-gcp-staging.md) — Terraform + Cloud Build
* [Agency FOIA workflow](playbooks/agency-foia-workflow.md) — Public comments intake
* [QA before share](playbooks/qa-before-share.md) — PDF share checklist

# References

* [Final review](references/final-review.md) — Proven vs partial vs specified audit
* [Design foundations](references/design-foundations.md) — Sources → invariants → tests
* [OKF spec](references/okf-spec.md) — Spec pointer
* [Repo map](references/repo-map.md) — Code layout
* [Foundations](../docs/FOUNDATIONS.md) — Full proof matrix (human-readable)
* [Patterns](../docs/PATTERNS.md) — Plain English for medallion, critic, planes
* [Standards](../docs/STANDARDS.md) — Best practices and external standards index
* [Getting started](../docs/GETTING-STARTED.md) — Full install and setup guide
* [Security hardening](../docs/SECURITY-HARDENING.md) — HTTP guards, vault perms, CI SAST/SCA
* [operator-security skill](../skills/operator-security/SKILL.md) — Agent checklist for security PRs
