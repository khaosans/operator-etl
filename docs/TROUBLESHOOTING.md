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

## See also

- [QUICKSTART.md](QUICKSTART.md#if-it-fails)
- [GETTING-STARTED.md](GETTING-STARTED.md)
- [CLI.md](CLI.md)
