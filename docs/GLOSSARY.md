# Glossary

Short definitions for terms used across Operator ETL. Each entry links to the page that owns the concept.

**When to read:** A word on another page is unclear. This is not a tutorial — start at [QUICKSTART](QUICKSTART.md) or [CONCEPTS](CONCEPTS.md).

---

## Planes

| Term | Meaning |
|---|---|
| **Data plane** | Python and SQL that ingest, validate, and aggregate. No LLM on raw rows. [HOW-IT-WORKS](HOW-IT-WORKS.md) |
| **Policy plane** | PII scan, encrypted vault, fail-closed quality gate. Agents never get vault decrypt. |
| **Control plane** | LangGraph pipeline, MCP tools, critic. Orchestration only. |

---

## Medallion layers

| Term | Meaning |
|---|---|
| **Bronze** | Immutable raw intake (`bronze_raw`). Content-hashed so the same file is not loaded twice. |
| **Silver** | Validated rows (`silver_comments` or `silver_orders`). Pydantic/schema passed. |
| **Gold** | Trusted SQL aggregates (`gold_comment_kpis`, `gold_kpis`). What insights may cite. |
| **Quarantine** | Invalid rows kept with an **error reason** — never silently dropped. Demo: 2 of 12 comments. |

---

## Agentic control

| Term | Meaning |
|---|---|
| **LangGraph** | Explicit graph of nodes (ingest → PII → validate → quality → gold → insight → critic → persist). |
| **Critic** | Deterministic check: every number in an insight draft must exist in gold metrics. Hallucinated `999` fails. [TESTING](TESTING.md) |
| **Insight** | Short narrative persisted to the `insights` table after the critic passes. Default is a gold-KPI **template**; optional LLM wording is [LLM.md](LLM.md). Cards and when-to-use: [MODELS.md](MODELS.md). |
| **HITL** | Human-in-the-loop. Graph status `needs_human` when quality fails, critic retries exhaust, or PII is ambiguous. |
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
| **Fail-closed** | Quality gate **withholds** KPIs/insights when quarantine is too high or data is stale — no warn-and-show. |
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
- [NIST.md](NIST.md)
- [FAQ.md](FAQ.md)
- [HOW-IT-WORKS.md](HOW-IT-WORKS.md)
- [FOUNDATIONS.md](FOUNDATIONS.md)
