# Glossary

Short definitions for terms used across Operator ETL. Each entry links to the page that owns the concept.

**When to read:** A word on another page is unclear. This is not a tutorial — start at [QUICKSTART](QUICKSTART.md) or [CONCEPTS](CONCEPTS.md).

---

## Planes

| Term | Meaning |
|---|---|
| **Plane** | A job that must not be mixed with the others (compute vs protect vs orchestrate). [PATTERNS](PATTERNS.md#three-planes) |
| **Data plane** | Python and SQL that ingest, validate, and aggregate. No LLM on raw rows. [HOW-IT-WORKS](HOW-IT-WORKS.md) |
| **Policy plane** | PII scan, encrypted vault, fail-closed quality gate. Agents never get vault decrypt. |
| **Control plane** | LangGraph pipeline, MCP tools, critic. Orchestration only. |

---

## Medallion layers

**Medallion** is a three-layer warehouse: keep the raw drop, keep only valid rows, publish only aggregates (KPIs). The medal names are labels for **trust**, not metal. Lesson: [PATTERNS.md](PATTERNS.md#medallion-bronze--silver--gold).

| Term | Meaning |
|---|---|
| **Medallion** | Pattern: raw → valid → trusted aggregates. Databricks name; we add quarantine. |
| **Bronze** | The original file, kept forever (`bronze_raw`). Hashed so the same drop is not loaded twice. |
| **Silver** | Rows that passed the schema (`silver_comments` or `silver_orders`). |
| **Gold** | Counts and rates leadership may cite (`gold_comment_kpis`). Insights may use **only** these numbers. |
| **Quarantine** | Invalid rows **kept** with an error reason — not deleted. Demo: 2 of 12 comments. |

---

## Agentic control

| Term | Meaning |
|---|---|
| **LangGraph** | A checklist of steps in order (ingest → PII → … → critic → persist), implemented as a graph library. |
| **Critic** | A **rule**, not another model: every digit in the insight must already exist in gold. Hallucinated `999` fails. [PATTERNS](PATTERNS.md#critic-faithfulness) |
| **Insight** | Short narrative persisted to the `insights` table after the critic passes. Default is a gold-KPI **template**; optional LLM wording is [LLM.md](LLM.md). Cards and when-to-use: [MODELS.md](MODELS.md). |
| **HITL** | A human still decides. Graph status `needs_human` is **not** success. [PATTERNS](PATTERNS.md#hitl-human-in-the-loop) |
| **`needs_human`** | Terminal graph status: do not treat as success; an officer must review. |
| **MCP** | Model Context Protocol. Agents call **typed tools**, not ad-hoc SQL. [MCP](MCP.md) |
| **Allowlist** | YAML of permitted SQL IDs (`sql/allowlist.yaml`). Unknown query IDs raise `ToolDenied`. |

---

## PII and FOIA

| Term | Meaning |
|---|---|
| **PII** | Personally identifiable information (emails, phones, SSN-like patterns in the sample). Sample data is **synthetic**. |
| **PII vault** | Encrypted store of originals (`warehouse/pii_vault.json`, gitignored). Not exposed via MCP. |
| **Redaction** | Replacing detected PII in agent-facing text (`REDACTED_EMAIL`, etc.). |
| **FOIA** | Freedom of Information Act workflow framing — intake comments, flag PII, produce defensible summaries. [FOIA guide](FOIA-Public-Comments-Guide.md) |
| **Docket** | Regulatory case ID (e.g. `EPA-HQ-OAR-2026-001`) grouping comments. |

---

## Proof and ops

| Term | Meaning |
|---|---|
| **Proof gate** | `./scripts/verify.sh` or `make e2e`: OKF validate + pytest + FOIA demo on a **fresh** warehouse. |
| **`OPERATOR_ETL_VERIFY=PASS`** | Banner from `verify.sh` when the gate succeeds. |
| **OKF** | Open Knowledge Format — agent wiki under `okf/`. Humans use this docs wiki. [LEVERAGE](LEVERAGE.md) |
| **Fail-closed** | When the gate is unhappy, **hide** the KPIs rather than show them with a warning. [PATTERNS](PATTERNS.md#fail-closed-quality) |
| **IMPLEMENTED / PARTIAL / SPECIFIED** | Status labels. Only **IMPLEMENTED** is proven in CI. [implementation-status](https://github.com/khaosans/operator-etl/blob/master/okf/models/implementation-status.md) |

---

## Models and NIST

| Term | Meaning |
|---|---|
| **Ollama** | Local model runtime. OpenAI-compatible API at `http://127.0.0.1:11434/v1`. Gold JSON stays on-box. [LLM.md](LLM.md) |
| **OpenAI-compatible** | Chat Completions `/v1` API. `ChatOpenAI` talks to OpenAI, Ollama, or another host via `OPERATOR_ETL_LLM_BASE_URL`. |
| **Model card** | Vendor’s intended-use, eval, and license page. We **summarize and link** — we do not copy cards. [MODELS.md](MODELS.md) |
| **NIST AI RMF** | AI Risk Management Framework 1.0 — functions **Govern, Map, Measure, Manage**. We align selected practices; not certified. [NIST.md](NIST.md) |
| **Govern / Map / Measure / Manage** | RMF functions: policy & no auto-publish; know data boundary; test with critic/`verify.sh`; fallback and HITL. |
| **SP 800-122** | NIST guide to PII confidentiality. Here: scan, vault, no PII in agent/model context. |
| **AI 600-1** | Generative AI Profile companion to the RMF. We map only risks this KPI demo mitigates. |

---

## See also

- [CONCEPTS.md](CONCEPTS.md)
- [PATTERNS.md](PATTERNS.md)
- [APPLY.md](APPLY.md)
- [RISKS.md](RISKS.md)
- [NIST.md](NIST.md)
- [FAQ.md](FAQ.md)
- [HOW-IT-WORKS.md](HOW-IT-WORKS.md)
- [FOUNDATIONS.md](FOUNDATIONS.md)
