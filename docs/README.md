# Documentation index

All Operator ETL documentation, organized by audience. **Start at [README.md](../README.md)** — problem, design, trade-offs, and quick start — then use this index for depth.

---

## Reading paths by persona

| Persona | Path |
|---|---|
| **New engineer (30 min)** | README → GETTING-STARTED → `make e2e` → WALKTHROUGH |
| **Architect evaluating design** | README trade-offs → FOUNDATIONS → FINAL-REVIEW → white paper §3 ADRs |
| **FOIA / agency operator** | FOIA guide → WALKTHROUGH dashboard step → HOW-IT-WORKS lifecycle |
| **Scaling to GCP** | FINAL-REVIEW pre-scale → SCALING → [infra/README.md](../infra/README.md) |
| **AI agent** | AGENTS.md → okf/index → skills |
| **External share** | FINAL-REVIEW scope → share/README → `make share` |

**Doc tiers:** Tier 1 = README · Tier 2 = GETTING-STARTED, WALKTHROUGH, HOW-IT-WORKS · Tier 3 = FOUNDATIONS, FINAL-REVIEW, SCALING, white paper

---

## New developer or operator

Start here after cloning:

1. [README.md](../README.md) — primary entry: problem, design, trust, trade-offs, quick start
2. [GETTING-STARTED.md](GETTING-STARTED.md) — install, verify, MCP, env vars, troubleshooting
3. [WALKTHROUGH.md](WALKTHROUGH.md) — step-by-step: see the test case work
4. [STANDARDS.md](STANDARDS.md) — patterns and best practices we follow

Proof gate: `make e2e` from repo root.

| Goal | Doc |
|---|---|
| **Why this design** | [FOUNDATIONS.md](FOUNDATIONS.md) |
| **Understand the system** | [HOW-IT-WORKS.md](HOW-IT-WORKS.md) |
| **See test case work** | [WALKTHROUGH.md](WALKTHROUGH.md) |
| **Scale to GCP** | [SCALING.md](SCALING.md) |
| **Final audit** | [FINAL-REVIEW.md](FINAL-REVIEW.md) |

---

## Agency / FOIA workflow

| Doc | Description |
|---|---|
| [FOIA-Public-Comments-Guide.md](FOIA-Public-Comments-Guide.md) | Full agency workflow and data model |
| [okf/playbooks/agency-foia-workflow.md](../okf/playbooks/agency-foia-workflow.md) | OKF playbook (links to guide) |
| [okf/models/mvp-demo.md](../okf/models/mvp-demo.md) | Expected demo numbers |

---

## Architect / engineer

| Doc | Description |
|---|---|
| [Operator-ETL-White-Paper.md](Operator-ETL-White-Paper.md) | Full engineering spec, ADRs, GCP |
| [Operator-ETL-White-Paper.pdf](Operator-ETL-White-Paper.pdf) | PDF version |
| [STANDARDS.md](STANDARDS.md) | Standards index |
| [okf/models/implementation-status.md](../okf/models/implementation-status.md) | IMPLEMENTED vs SPECIFIED matrix |
| [infra/README.md](../infra/README.md) | GCP Terraform deploy |

---

## AI agent

| Doc | Description |
|---|---|
| [AGENTS.md](../AGENTS.md) | Required load order |
| [okf/index.md](../okf/index.md) | OKF knowledge bundle |
| [docs/LEVERAGE.md](LEVERAGE.md) | OKF + skills + harness mental model |
| [skills/](../skills/) | Task-specific agent skills |

---

## Share / post externally

Repo is **private**. Attach PDFs only — not the GitHub URL.

| Doc | Description |
|---|---|
| [share/README.md](share/README.md) | What to attach, suggested post copy |
| [share/latest/](share/latest/) | Current PDF bundle |

Regenerate: `make share`

---

## Contributing and policy

| Doc | Description |
|---|---|
| [CONTRIBUTING.md](../CONTRIBUTING.md) | PR checklist |
| [SECURITY.md](../SECURITY.md) | Secrets and PII policy |
| [CHANGELOG.md](../CHANGELOG.md) | Release history |
| [okf/playbooks/qa-before-share.md](../okf/playbooks/qa-before-share.md) | Pre-share checklist |
