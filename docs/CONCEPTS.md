# Concepts — learn the project

**When to read:** After a first `./scripts/verify.sh`, or before it if you want the story. This is a tour, not a spec.

Operator ETL is a **demo of bounded agents on a FOIA-shaped warehouse**. Python and SQL decide what data exists. Agents only orchestrate. Tests prove the invariants. No API key is required for the default path.

---

## The job

A FOIA officer (or anyone intake-ing public comments) needs three things that a chat-with-the-warehouse demo usually fails to give:

1. **An audit trail** — what file arrived, when, and what happened to each row.
2. **PII out of the model** — emails and phones in comment bodies must not ride along in a prompt.
3. **Numbers they can defend** — if a summary says “10 comments,” that 10 has to live in a table.

The sample drop is twelve synthetic comments. Ten pass validation. Two go to quarantine on purpose (empty body, bad timestamp). That 12 → 10 + 2 split is the whole point: bad rows are kept with a reason, not dropped on the floor.

---

## Why not a warehouse chatbot

Give a model SQL on the raw warehouse and three failures show up fast. Comment bodies (and the emails inside them) land in context. The model invents a count that is not in any table. Nobody can replay *which file, which run, which gate*. Operator ETL refuses that shape: the model never sees bronze, and it never gets to persist a number the critic cannot find in gold.

Pitch version: [WHY.md](WHY.md). Screenshots: [TOUR.md](TOUR.md).

---

## Three planes

Think of three jobs that must not collapse into one chatbot:

- **Data plane** — ingest, validate, aggregate. Python and SQL. This is where “10 comments” is *computed*, not guessed.
- **Policy plane** — PII scan, encrypted vault, fail-closed quality gate. If quarantine is too high, KPIs are withheld. Agents never decrypt the vault.
- **Control plane** — LangGraph runs the steps; MCP exposes three allowlisted tools; a **critic** checks that every digit in an insight exists in gold.

Runtime diagrams: [HOW-IT-WORKS.md](HOW-IT-WORKS.md).

---

## Medallion (plain language)

- **Bronze** keeps the drop forever (content-hashed so the same file is not loaded twice).
- **Silver** is rows that passed schema.
- **Quarantine** is rows that failed, with an error reason.
- **Gold** is trusted aggregates. It is the **only** set of numbers an insight may cite.

---

## What an “insight” is

The default insight is a **template** filled from gold KPIs — the sentence you see after `verify.sh`. An optional LLM may rewrite the *wording*. It still receives numeric gold JSON only, never comment bodies. Nothing is persisted until the critic passes. If the model is missing or fails, the graph falls back to the template. That is intentional.

Install a local or cloud model: [LLM.md](LLM.md). Which model, and where the JSON goes: [MODELS.md](MODELS.md).

---

## Human in the loop

Graph status `needs_human` is **not** success. An officer still has to review. Agents never auto-publish FOIA releases, insight emails, or public dumps. Decision: [agents never publish prod](https://github.com/khaosans/operator-etl/blob/master/okf/decisions/agents-never-publish-prod.md).

---

## Where standards fit

[NIST.md](NIST.md) maps this demo onto NIST AI RMF (Govern / Map / Measure / Manage), the generative-AI profile for the risks we actually mitigate, and SP 800-122 for PII. We **align** selected practices. We do not claim certification, FedRAMP, or an ATO.

---

## Learning path

[QUICKSTART](QUICKSTART.md) → **this page** → [TOUR](TOUR.md) → [NIST](NIST.md) → [MODELS](MODELS.md) → [LLM](LLM.md) → [FOUNDATIONS](FOUNDATIONS.md)

Citations and the proof matrix live in FOUNDATIONS. The deep spec is the [white paper](Operator-ETL-White-Paper.md) — not duplicated here.
