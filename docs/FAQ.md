# FAQ

**When to read:** You have a specific question before cloning or after a first run. For setup failures see [TROUBLESHOOTING](TROUBLESHOOTING.md).

---

## Do I need an OpenAI (or other LLM) API key?

**No.** The default insight is a **template** filled from gold KPIs. The critic checks numbers against the warehouse. `make e2e` / `./scripts/verify.sh` run with no cloud LLM.

Optional LLM wording is **PARTIAL**: set `OPERATOR_ETL_INSIGHT_BACKEND=llm` after `uv sync --extra llm`. Local Ollama: `OPERATOR_ETL_LLM_BASE_URL=http://127.0.0.1:11434/v1` and `OPERATOR_ETL_LLM_MODEL=llama3.2:3b`. Missing extra, missing key, or a failed call falls back to the template. Not proven with a live API in CI. Setup: [LLM.md](LLM.md). Screenshots: [TOUR.md](TOUR.md).

---

## Is this production-ready FOIA software?

**No.** It is a **reproducible demo / reference architecture**. Proven locally: ingest, regex PII, quarantine, gold, LangGraph, critic, MCP allowlist. Not proven in CI: live GCP, Presidio, officer approval UI, Regulations.gov.

See [FINAL-REVIEW.md](FINAL-REVIEW.md). Safe public claim: *clone and run `./scripts/verify.sh`*.

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
