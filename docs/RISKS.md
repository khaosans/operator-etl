# Risks and limitations — what to know

**When to read:** Before you adopt the pattern, share it as “FOIA software,” or turn on a cloud model. This is not a System Security Plan and not an ATO.

Honest proof inventory: [FINAL-REVIEW.md](FINAL-REVIEW.md). NIST language: [NIST.md](NIST.md).

Operator ETL **reduces** three demo-class failures (PII in prompts, invented KPIs, unreplayable runs). It does **not** eliminate operational, legal, or model risk. Use the list below as a briefing, not as fear — every row is something an adopter should be able to say out loud.

---

## Residual risk (still true when `verify.sh` is green)

| Risk | What is true today | What to do |
|---|---|---|
| **PII scanner is regex** | Email / phone / SSN-like patterns. Names, addresses, and messy international formats slip through. Presidio is SPECIFIED. | Do not treat “no PII in insight” as “no PII in silver.” Review quarantine and bodies before any release. |
| **Critic checks digits, not meaning** | `0.4` in gold satisfies the critic even if the sentence calls it “40 comments.” | Read the insight. Small local models misread rates — [MODELS.md](MODELS.md). Do not loosen the critic. |
| **LLM fallback looks complete** | Missing extra, key, or API → **template** insight, note in `errors`, graph may still `complete`. | Check `insight_backend=` and `errors`. Cloud Run: do not flip to `llm` on a placeholder secret. |
| **Gold JSON can leave the box** | OpenAI / Cloud Run `llm` sends **numeric** KPIs off-machine. Bodies still never go. | If aggregates are sensitive, use Ollama or stay on template. [NIST.md](NIST.md) Map. |
| **HITL is a status, not a product** | `needs_human` is proven. Officer **approve/reject** UI is PARTIAL. Streamlit is a laptop inspector. | A human must still decide to publish. [PRODUCT-UX.md](PRODUCT-UX.md). |
| **Samples are synthetic** | `jane.doe@example.com` is fake. | Never commit real FOIA or case files. |
| **Quality gate is a threshold** | High quarantine **withholds** KPIs (fail-closed). Tune `OPERATOR_ETL_MAX_QUARANTINE_RATE` with care — hiding failure is worse than a red gate. | |
| **MCP is an allowlist, not IAM** | Three tools, no vault. This is least privilege **for the demo agent**, not agency identity management. | Do not expose MCP on a public URL without the Cloud Run auth story. |
| **Rate limiting is in-process** | Per-client sliding window middleware added. Sufficient for single-instance but not for distributed or high-traffic production. | Use Cloud Armor or an API gateway for production rate limiting. |
| **No live GCP in CI** | Terraform and adapters exist. Staging E2E is manual. | [SCALING.md](SCALING.md). |
| **Not certified** | We align selected NIST practices. Not FedRAMP, not ATO, not “NIST compliant” as a slogan. | [NIST.md](NIST.md) · FAQ. |

---

## Risks the architecture is designed to contain

These are the problems we **do** take on, with tests:

- Comment **bodies** in an unconstrained model context — ingest never sends bronze to the insight node.
- Invented leadership numbers — critic + gold marts (`tests/test_critic.py`).
- Silent row loss — quarantine with error text (`test_quarantine_preserves_bad_rows_with_errors`).
- Duplicate drops rewriting history — content hash on ingest.
- Agent SQL on raw tables — MCP deny paths.

If a proposed feature violates one of those (e.g. “just concatenate bodies into the prompt”), it is out of design, not a backlog item.

---

## Generative-AI risks we do *not* claim to cover

NIST AI 600-1 lists categories this KPI-summary demo does not address: CBRN, CSAM, environmental impact, full bias/fairness evaluation, and open-ended chat. We do not map them. Do not paste comment corpora into a general chatbot and call it Operator ETL.

Prompt injection via **comment text** is largely avoided because bodies never reach the model. If you change that, you own a new threat class.

---

## Operational pitfalls

- **Stale `OPERATOR_ETL_*` exports** — wrong domain, wrong warehouse, mysterious pytest failures.
- **One DuckDB for Gov + Orders** — dashboard tabs look empty or mixed; use two warehouse paths.
- **Calling it production FOIA software** — it is a reproducible **reference architecture**. Safe public claim: clone and run `./scripts/verify.sh`.

---

## If you cannot accept the residuals

Stay on the **template** insight, local DuckDB, and human review of silver/quarantine. That path needs no model, no cloud key, and still proves medallion + critic. Optional LLM is a wording upgrade, not a requirement.

---

## See also

- [CONCEPTS.md](CONCEPTS.md) — what we built
- [APPLY.md](APPLY.md) — other data sources
- [FINAL-REVIEW.md](FINAL-REVIEW.md) — proven / partial / specified
- [SECURITY.md](https://github.com/khaosans/operator-etl/blob/master/SECURITY.md) — secrets and PII in git
