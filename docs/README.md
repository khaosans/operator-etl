# Documentation wiki

Canonical human docs for Operator ETL. **Published:** [https://khaosans.github.io/operator-etl/](https://khaosans.github.io/operator-etl/) (GitHub Pages). **In git:** this folder (PRs + CI).

**Start here:** [index.md](index.md) (wiki home) · [QUICKSTART.md](QUICKSTART.md) (`./scripts/verify.sh`) · learn: [CONCEPTS.md](CONCEPTS.md)

This folder follows [Diátaxis](https://diataxis.fr/): **tutorials** (Start / Walkthrough), **explanation** (Understand), **how-to** (Use / Scale), **reference** (Glossary / FAQ / Testing). Do not mix a how-to into an explanation page.

Agent knowledge stays in [okf/index.md](https://github.com/khaosans/operator-etl/blob/master/okf/index.md) — do not duplicate playbooks here.

---

## Reading paths by persona

| Persona | Path |
|---|---|
| **New engineer (30 min)** | [QUICKSTART](QUICKSTART.md) → `./scripts/verify.sh` → [CONCEPTS](CONCEPTS.md) → [TOUR](TOUR.md) → [WALKTHROUGH](WALKTHROUGH.md) |
| **Architect evaluating design** | [WHY](WHY.md) → [CONCEPTS](CONCEPTS.md) → [RISKS](RISKS.md) → [NIST](NIST.md) → [FOUNDATIONS](FOUNDATIONS.md) → [FINAL-REVIEW](FINAL-REVIEW.md) |
| **FOIA / agency operator** | [PERSONAS](PERSONAS.md) → [FOIA guide](FOIA-Public-Comments-Guide.md) → [DASHBOARD](DASHBOARD.md) · later [PRODUCT-UX](PRODUCT-UX.md) |
| **New data source** | [APPLY](APPLY.md) → [ADD-A-SOURCE](ADD-A-SOURCE.md) |
| **Scaling to GCP** | [FINAL-REVIEW](FINAL-REVIEW.md) → [SCALING](SCALING.md) → [infra](https://github.com/khaosans/operator-etl/blob/master/infra/README.md) |
| **AI agent** | [AGENTS.md](https://github.com/khaosans/operator-etl/blob/master/AGENTS.md) → [operator-verify](https://github.com/khaosans/operator-etl/blob/master/skills/operator-verify/SKILL.md) → QUICKSTART |
| **External share** | [WHY](WHY.md) → [FINAL-REVIEW](FINAL-REVIEW.md) → [share](share/README.md) |

**Doc tiers:** Tier 0 = QUICKSTART · Tier 1 = wiki home / README · Tier 2 = GETTING-STARTED, WALKTHROUGH, HOW-IT-WORKS · Tier 3 = FOUNDATIONS, FINAL-REVIEW, SCALING, white paper

---

## 1. Start

| Doc | Description |
|---|---|
| [index.md](index.md) | Wiki landing — who, verify, honest scope |
| [QUICKSTART.md](QUICKSTART.md) | One-command verify + agent prompt |
| [GETTING-STARTED.md](GETTING-STARTED.md) | Install, MCP, env vars |
| [PERSONAS.md](PERSONAS.md) | Named user composites |
| [TOUR.md](TOUR.md) | Screenshots of verify, CLI, Streamlit, wiki |

Proof gate: `./scripts/verify.sh` or `make e2e`.

---

## 2. Understand

| Doc | Description |
|---|---|
| [WHY.md](WHY.md) | Problem — chatbot trap vs three planes |
| [CONCEPTS.md](CONCEPTS.md) | What we built, why it is useful, learning path |
| [HOW-IT-WORKS.md](HOW-IT-WORKS.md) | Planes, lifecycle, MCP policy |
| [APPLY.md](APPLY.md) | Same pattern on other CSVs (orders, 311, grants, …) |
| [RISKS.md](RISKS.md) | Residual risks after a green verify |
| [NIST.md](NIST.md) | AI RMF / 600-1 / SP 800-122 alignment (not certification) |
| [MODELS.md](MODELS.md) | Local vs cloud models, cards, when-to-use |
| [FOUNDATIONS.md](FOUNDATIONS.md) | Citations + proof matrix |
| [Operator-ETL-White-Paper.md](Operator-ETL-White-Paper.md) | Deep engineering spec |

---

## 3. Prove

| Doc | Description |
|---|---|
| [WALKTHROUGH.md](WALKTHROUGH.md) | Step-by-step after verify |
| [TESTING.md](TESTING.md) | What each test proves |
| [FINAL-REVIEW.md](FINAL-REVIEW.md) | Proven / partial / specified |

---

## 4. Use

| Doc | Description |
|---|---|
| [CLI.md](CLI.md) | `etl`, `etl-graph`, Make targets |
| [DASHBOARD.md](DASHBOARD.md) | Streamlit Gov / Orders tabs |
| [MCP.md](MCP.md) | Cursor MCP allowlist |
| [ADD-A-SOURCE.md](ADD-A-SOURCE.md) | Register a new CSV / HTTP source (how-to) |
| [LLM.md](LLM.md) | Optional Ollama / OpenAI-compatible insight wording — install |
| [FOIA-Public-Comments-Guide.md](FOIA-Public-Comments-Guide.md) | Agency workflow |

---

## 5. Reference

| Doc | Description |
|---|---|
| [GLOSSARY.md](GLOSSARY.md) | Bronze, critic, HITL, MCP, AI RMF, … |
| [FAQ.md](FAQ.md) | API keys, NIST certified?, quarantine |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | uv, stale warehouse, Ollama 11434 |
| [STANDARDS.md](STANDARDS.md) | Standards index including NIST |

---

## 6. Scale

| Doc | Description |
|---|---|
| [SCALING.md](SCALING.md) | Local → GCP ladder |
| [PRODUCT-UX.md](PRODUCT-UX.md) | Product officer UI backlog (SPECIFIED) |
| [infra/README](https://github.com/khaosans/operator-etl/blob/master/infra/README.md) | Terraform |

---

## 7. Contribute

| Doc | Description |
|---|---|
| [CONTRIBUTING.md](https://github.com/khaosans/operator-etl/blob/master/CONTRIBUTING.md) | PR checklist |
| [RELEASING.md](RELEASING.md) | Updates, Pages, Wiki paste |
| [PUBLIC-READINESS.md](PUBLIC-READINESS.md) | OSS checklist |
| [SECURITY.md](https://github.com/khaosans/operator-etl/blob/master/SECURITY.md) | Secrets and PII |
| [CHANGELOG.md](https://github.com/khaosans/operator-etl/blob/master/CHANGELOG.md) | Release history |
| [CODE_OF_CONDUCT.md](https://github.com/khaosans/operator-etl/blob/master/CODE_OF_CONDUCT.md) | Community standards |
| [share/README.md](share/README.md) | PDF pack |
| [wiki/Home.md](wiki/Home.md) | GitHub Wiki tab paste source |

---

## AI agent

| Doc | Description |
|---|---|
| [AGENTS.md](https://github.com/khaosans/operator-etl/blob/master/AGENTS.md) | Fast verify then skills |
| [okf/index.md](https://github.com/khaosans/operator-etl/blob/master/okf/index.md) | OKF bundle |
| [LEVERAGE.md](LEVERAGE.md) | OKF + skills + harness |
