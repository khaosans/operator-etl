# Operator ETL wiki

**Agentic data intake for FOIA and public comments** — a **medallion** warehouse (raw → valid rows → KPIs; [PATTERNS](PATTERNS.md)), LangGraph orchestration, MCP allowlist, PII policy plane.

Python and SQL decide what data exists. Agents orchestrate within typed boundaries. Tests prove the invariants. **No LLM API key** is required for the MVP demo.

**When to read:** First page after you find the repo or this site. How this wiki is organized is below. To **learn** what we built: [CONCEPTS](CONCEPTS.md).

---

## The problem

Chat-with-the-warehouse demos fail three ways that matter for public comments and any audited intake: **PII in the prompt**, **invented counts** in the memo, and **runs you cannot replay**. Operator ETL separates deterministic ETL from bounded agents so those failures are testable instead of hoped away.

Full argument: [WHY.md](WHY.md).

---

## What we built

A **reference architecture**, not a production FOIA product: **medallion** layers (bronze → silver/quarantine → gold), PII vault, LangGraph, a critic that rejects uncited numbers, and three MCP tools with no vault access. Default insight is a **template**. Optional LLM only rewrites wording from gold KPI JSON.

Tour: [CONCEPTS.md](CONCEPTS.md) · Words: [PATTERNS.md](PATTERNS.md) · Runtime: [HOW-IT-WORKS.md](HOW-IT-WORKS.md) · Audit: [FINAL-REVIEW.md](FINAL-REVIEW.md).

---

## Prove it (3 lines)

```bash
git clone https://github.com/khaosans/operator-etl.git
cd operator-etl
./scripts/verify.sh
```

Success ends with **`OPERATOR_ETL_VERIFY=PASS`**, 59 pytest, and a FOIA demo of `status=complete`, `silver=10`, `quarantined=2`.

Full card: [QUICKSTART.md](QUICKSTART.md) · Screenshots: [TOUR.md](TOUR.md)

![Gov / FOIA dashboard after a local FOIA run](assets/screenshots/dashboard-gov-kpis.png)

---

## Why it is useful · other data · risks

| Topic | Page |
|---|---|
| Why the pattern exists | [WHY](WHY.md) · [CONCEPTS](CONCEPTS.md) · [PATTERNS](PATTERNS.md) |
| Same architecture on another CSV (311, grants, orders, …) | [APPLY](APPLY.md) |
| Residual risks (regex PII, critic digits, cloud JSON, HITL) | [RISKS](RISKS.md) |
| NIST alignment, not certification | [NIST](NIST.md) |

---

## Who this is for

| You are… | Start here |
|---|---|
| **New engineer** | [QUICKSTART](QUICKSTART.md) → [CONCEPTS](CONCEPTS.md) → [WALKTHROUGH](WALKTHROUGH.md) · [TOUR](TOUR.md) |
| **FOIA / program officer** | [FOIA guide](FOIA-Public-Comments-Guide.md) → [DASHBOARD](DASHBOARD.md) · [TOUR](TOUR.md) |
| **Architect / reviewer** | [WHY](WHY.md) → [CONCEPTS](CONCEPTS.md) → [RISKS](RISKS.md) → [NIST](NIST.md) → [FOUNDATIONS](FOUNDATIONS.md) |
| **Extending to another feed** | [APPLY](APPLY.md) → [ADD-A-SOURCE](ADD-A-SOURCE.md) |
| **Learn the project** | [CONCEPTS](CONCEPTS.md) → [APPLY](APPLY.md) → [RISKS](RISKS.md) → [MODELS](MODELS.md) |
| **AI agent** | [AGENTS.md](https://github.com/khaosans/operator-etl/blob/master/AGENTS.md) → [operator-verify](https://github.com/khaosans/operator-etl/blob/master/skills/operator-verify/SKILL.md) |

---

## How to read this wiki

Docs follow a [Diátaxis](https://diataxis.fr/) split so tutorials, explanation, how-to, and reference stay distinct.

| Kind | What you want | Where |
|---|---|---|
| **Tutorials** | Do the happy path | Start + Prove: Quickstart, Getting started, Tour, Walkthrough |
| **Explanation** | Understand problem, design, words, transfer, risk | Understand: Why, Concepts, Patterns, How it works, Apply, Risks, NIST, Models, Foundations |
| **How-to** | Achieve a task | Use + Scale: CLI, sources, LLM, dashboard, GCP |
| **Reference** | Look up a fact | Glossary, FAQ, Troubleshooting, Standards, Testing, Final review, [Versioning](VERSIONING.md) |

Personas: [PERSONAS.md](PERSONAS.md).

---

## Honest scope

| Proven locally (`make e2e`) | Not this MVP |
|---|---|
| FOIA CSV → PII → silver/quarantine → gold → critic-verified insight | Production Presidio PII |
| 59 pytest + SAST/SCA CI on every push | Live GCP / BigQuery end-to-end |
| MCP allowlist (3 tools, no vault) | Live LLM API (optional path mocked; template default) |

Full audit: [FINAL-REVIEW.md](FINAL-REVIEW.md) · Residual risks: [RISKS.md](RISKS.md)

---

## Wiki map

1. **Start** — [QUICKSTART](QUICKSTART.md) · [GETTING-STARTED](GETTING-STARTED.md) · [PERSONAS](PERSONAS.md) · [TOUR](TOUR.md)
2. **Understand** — [WHY](WHY.md) · [CONCEPTS](CONCEPTS.md) · [PATTERNS](PATTERNS.md) · [HOW-IT-WORKS](HOW-IT-WORKS.md) · [APPLY](APPLY.md) · [RISKS](RISKS.md) · [NIST](NIST.md) · [MODELS](MODELS.md) · [FOUNDATIONS](FOUNDATIONS.md)
3. **Prove** — [WALKTHROUGH](WALKTHROUGH.md) · [TESTING](TESTING.md) · [FINAL-REVIEW](FINAL-REVIEW.md) · [SECURITY-HARDENING](SECURITY-HARDENING.md)
4. **Use** — [RUNNING](RUNNING.md) · [CLI](CLI.md) · [DASHBOARD](DASHBOARD.md) · [MCP](MCP.md) · [A2A](A2A.md) · [OBSERVABILITY](OBSERVABILITY.md) · [ADD-A-SOURCE](ADD-A-SOURCE.md) · [LLM](LLM.md)
5. **Reference** — [GLOSSARY](GLOSSARY.md) · [FAQ](FAQ.md) · [TROUBLESHOOTING](TROUBLESHOOTING.md) · [STANDARDS](STANDARDS.md)
6. **Scale** — [SCALING](SCALING.md) · [MULTI-CLOUD](MULTI-CLOUD.md) · [PRODUCT-UX](PRODUCT-UX.md) · [infra/README](https://github.com/khaosans/operator-etl/blob/master/infra/README.md)
7. **Contribute** — [CONTRIBUTING](https://github.com/khaosans/operator-etl/blob/master/CONTRIBUTING.md) · [VERSIONING](VERSIONING.md) · [RELEASING](RELEASING.md) · [SECURITY](https://github.com/khaosans/operator-etl/blob/master/SECURITY.md)

**Deep spec:** [Operator-ETL-White-Paper.md](Operator-ETL-White-Paper.md) (not duplicated here).

**Agent knowledge:** [okf/index.md](https://github.com/khaosans/operator-etl/blob/master/okf/index.md) — playbooks for Cursor/Claude; humans use this wiki.

---

## See also

- [QUICKSTART.md](QUICKSTART.md) — one-command verify
- [CONCEPTS.md](CONCEPTS.md) — learn the project
- [PATTERNS.md](PATTERNS.md) — medallion, critic, planes
- [APPLY.md](APPLY.md) — other data sources
- [RISKS.md](RISKS.md) — what to know before adopting
- [GLOSSARY.md](GLOSSARY.md) — terms
- [FAQ.md](FAQ.md) — common questions
- [SECURITY-HARDENING.md](SECURITY-HARDENING.md) — HTTP guards, CI SAST/SCA, vault perms
