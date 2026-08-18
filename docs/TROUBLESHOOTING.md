# Troubleshooting

**When to read:** Verify, pytest, dashboard, or `etl-graph` failed. First-time setup: [QUICKSTART](QUICKSTART.md).

---

## Python version

**Symptom:** `Python 3.12+ required` or `verify.sh` exits 1 at the start.

**Fix:** Install Python 3.12+. Check with `python3 --version`. The repo pins `.python-version` to `3.12`.

---

## uv missing or install blocked

**Symptom:** `uv not on PATH` with `--skip-uv-install`, or curl to astral.sh blocked.

**Fix:**

1. Install uv from [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
2. Ensure `~/.local/bin` is on `PATH`
3. Then: `uv sync --frozen --extra dev && make e2e`

Do not use a random global pip env — lockfile is `uv.lock`.

---

## Stale row counts from `etl-graph`

**Symptom:** Silver/quarantine numbers grow across runs; demo assertions fail.

**Cause:** Default warehouse **accumulates**. The proof gate uses a **fresh** path (`.tmp/mvp-demo/`).

**Fix:**

```bash
./scripts/demo_mvp.sh
# or
./scripts/verify.sh
```

---

## pytest fails after exporting gov env vars

**Symptom:** Orders tests fail or settings point at `public_comments` during `uv run pytest`.

**Cause:** `OPERATOR_ETL_PIPELINE_NAME=public_comments` / `OPERATOR_ETL_DOMAIN=gov` in the shell affect global settings.

**Fix:** Open a clean shell, or only use `make e2e` / `./scripts/verify.sh` (gov env is scoped to the demo step).

---

## Quality gate blocks KPIs

**Symptom:** Dashboard **BLOCKED**, insights withheld, `needs_human`.

**Cause:** Quarantine rate above `OPERATOR_ETL_MAX_QUARANTINE_RATE` (default 0.35) or data older than `OPERATOR_ETL_MAX_FRESHNESS_HOURS`.

**Fix:** Inspect `quarantine_*` tables (dashboard expander or `make walkthrough`). Do not lower the gate to “make the demo look green” without understanding the rows. Agency path: [FOIA-Public-Comments-Guide.md](FOIA-Public-Comments-Guide.md).

---

## `make docker-build` fails

**Symptom:** Cannot connect to Docker daemon.

**Fix:** Start Docker Desktop (or equivalent). CI still builds the image on GitHub Actions if local Docker is unavailable.

---

## Dashboard: “No gov warehouse yet”

**Symptom:** Gov / FOIA tab warning.

**Fix:** Run the FOIA demo first, then export `OPERATOR_ETL_WAREHOUSE` to `.tmp/mvp-demo/operator.duckdb`. [DASHBOARD](DASHBOARD.md).

---

## Walkthrough / DuckDB CLI not found

**Symptom:** `duckdb: command not found`.

**Fix:** Use `./scripts/walkthrough.sh` — it uses `uv run python` + the `duckdb` **package**, not a separate DuckDB binary.

---

## MCP tools empty or wrong counts

**Fix:** Restart Cursor after editing `.cursor/mcp.json`. Set `cwd` to the clone. Point `OPERATOR_ETL_WAREHOUSE` at a warehouse that has **gold** (post-verify). [MCP](MCP.md).

---

## OKF validate fails in CI or locally

```bash
python3 scripts/okf_validate.py okf --strict
```

Concept files need YAML frontmatter (`type`, `title`, `description`). New files must be linked from [okf/index.md](https://github.com/khaosans/operator-etl/blob/master/okf/index.md).

---

## LLM insight fell back to the template

**Symptom:** Graph completes, insight looks like the usual KPI sentence, and `errors` mentions `OPENAI_API_KEY`, `langchain-openai`, or `LLM insight failed`.

**Cause:** `OPERATOR_ETL_INSIGHT_BACKEND=llm` is set but the extra, key, or API call is missing/failing. That is intentional — the critic still runs on the template.

**Fix:** See [LLM.md](LLM.md). For Cloud Run, do not flip the backend to `llm` until the Secret Manager OpenAI secret is a real key. Model choice: [MODELS.md](MODELS.md).

---

## Ollama connection refused on 11434

**Symptom:** `curl http://127.0.0.1:11434/api/tags` fails, or the graph falls back to template with a connection error in `errors`.

**Cause:** Ollama is not installed or the daemon is not running.

**Fix:** Install from [ollama.com/download](https://ollama.com/download) (macOS: official app or `brew install --cask ollama-app`). Start the app / `ollama serve`. Then `ollama pull llama3.2:3b`. Recipe: [LLM.md](LLM.md#local-ollama-from-zero).

---

## Ollama: model tag missing

**Symptom:** API error about an unknown model, or `ollama list` does not show `llama3.2:3b`.

**Fix:** `ollama pull llama3.2:3b` and set `OPERATOR_ETL_LLM_MODEL=llama3.2:3b` (the tag must match `ollama list`).

---

## See also

- [QUICKSTART.md](QUICKSTART.md#if-it-fails)
- [GETTING-STARTED.md](GETTING-STARTED.md)
- [CLI.md](CLI.md)
