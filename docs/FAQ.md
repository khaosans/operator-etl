# FAQ

**When to read:** You have a specific question before cloning or after a first run. For setup failures see [TROUBLESHOOTING](TROUBLESHOOTING.md).

---

## Do I need an OpenAI (or other LLM) API key?

**No.** The default insight is a **template** filled from gold KPIs. The critic checks numbers against the warehouse. `make e2e` / `./scripts/verify.sh` run with no cloud LLM.

Optional LLM wording is **PARTIAL**: set `OPERATOR_ETL_INSIGHT_BACKEND=llm` after `uv sync --extra llm`. Local Ollama: `OPERATOR_ETL_LLM_BASE_URL=http://127.0.0.1:11434/v1` and `OPERATOR_ETL_LLM_MODEL=llama3.2:3b`. Missing extra, missing key, or a failed call falls back to the template. Not proven with a live API in CI. Install: [LLM.md](LLM.md). Cards: [MODELS.md](MODELS.md). Screenshots: [TOUR.md](TOUR.md).

---

## How do I install a local model?

Install [Ollama](https://ollama.com/download), pull `llama3.2:3b`, then point Operator ETL at `http://127.0.0.1:11434/v1`. Full recipe: [LLM.md](LLM.md#local-ollama-from-zero). You do **not** need a discrete GPU (Apple Silicon Metal or CPU). Which tag and RAM: [MODELS.md](MODELS.md).

---

## Does gold JSON leave my machine?

**Template:** no. **Ollama on localhost:** no — JSON stays on-box. **OpenAI API / Cloud Run with `insight_backend=llm`:** yes — numeric gold KPIs go to the host. Comment bodies still never go. That boundary is NIST **Map**: [NIST.md](NIST.md) · [MODELS.md](MODELS.md#data-boundary-nist-map).

---

## Are you NIST certified?

**No.** We **align** selected practices from AI RMF 1.0, AI 600-1 (only the generative risks this demo mitigates), and SP 800-122. We do not claim NIST certification, FedRAMP, or an ATO. [NIST.md](NIST.md).

---

## Is this production-ready FOIA software?

**No.** It is a **reproducible demo / reference architecture**. Proven locally: ingest, regex PII, quarantine, gold, LangGraph, critic, MCP allowlist. Not proven in CI: live GCP, Presidio, officer approval UI, Regulations.gov.

See [FINAL-REVIEW.md](FINAL-REVIEW.md) · [RISKS.md](RISKS.md). Safe public claim: *clone and run `./scripts/verify.sh`*.

---

## Can I use this for data that is not FOIA?

**Yes, as a pattern.** The repo already runs a second domain (**orders**) on the same critic and policy plane. You change schema, gold SQL, and the insight template — you do **not** remove bronze, quarantine, the critic, or the MCP allowlist. Sketches for 311, grants, inspections: [APPLY.md](APPLY.md). YAML how-to: [ADD-A-SOURCE.md](ADD-A-SOURCE.md).

---

## What should I know about residual risk?

Green `verify.sh` does not mean production FOIA software. Regex PII misses names/addresses; the critic matches **digits** not meaning; LLM fallback can still look `complete`; cloud `llm` sends gold KPI JSON off-box; HITL is a graph status, not an approval product. Briefing: [RISKS.md](RISKS.md).

---

## Why do 2 of 12 comments go to quarantine?

The sample CSV includes rows that **should** fail validation: empty `body` and an invalid timestamp (`not-a-date`). Quarantine keeps them with error text. That is the point — bad rows are not silent.

After verify: `silver=10`, `quarantined=2`. Details: [WALKTHROUGH](WALKTHROUGH.md).

---

## Are the emails and SSNs in `samples/` real?

**No.** They are **synthetic** test patterns (`jane.doe@example.com`, `123-45-6789`). Do not commit real FOIA records. Do not post the raw CSV on social without saying it is fake PII.

---

## DuckDB vs BigQuery — which do I use?

| Environment | Warehouse |
|---|---|
| Laptop / CI / first clone | **DuckDB** file (`OPERATOR_ETL_WAREHOUSE`) |
| GCP staging (PARTIAL) | **BigQuery** via Terraform — [SCALING](SCALING.md) |

Same graph nodes and critic. Lift is a backend swap, not a rewrite of policy.

---

## Can I give an agent the whole warehouse?

**No.** MCP exposes three tools: `get_gold_metrics`, `run_quality_sql` (allowlisted IDs only), `get_run_status`. Vault decrypt and ad-hoc SQL are denied. [MCP](MCP.md).

---

## Why does a second ingest report `rows_in=0`?

Idempotency. The file **content hash** is stored in `ingest_files`. Re-dropping the same CSV skips bronze. Fresh warehouse: `./scripts/demo_mvp.sh` or `verify.sh`.

---

## The GitHub repo says public in the docs — is it public?

The **license is Apache-2.0** and docs assume a public clone URL. Visibility is a GitHub setting. If clone fails with 404, the repo may still be private — ask the owner, or use a fork you can access.

---

## Where is the wiki vs the PDF pack?

| Surface | Use |
|---|---|
| This wiki (`docs/` + GitHub Pages) | Browse and learn without attaching files |
| [share/](share/README.md) | One-pager / slides / white paper PDF for interviews |
| `okf/` | Agent-oriented knowledge bundle |

Always invite `./scripts/verify.sh` in posts.

---

## How do I add my own CSV?

See [ADD-A-SOURCE.md](ADD-A-SOURCE.md). Register it in `pipelines/*.yaml`, add a sample, add a test.

---

## See also

- [GLOSSARY.md](GLOSSARY.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [QUICKSTART.md](QUICKSTART.md)
