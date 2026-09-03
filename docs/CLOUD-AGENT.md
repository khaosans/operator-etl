# Cloud Agent development environment

How Operator ETL boots inside a [Cursor Cloud Agent](https://cursor.com/docs/cloud-agent/setup). The setup lives in [`.cursor/environment.json`](https://github.com/khaosans/operator-etl/blob/master/.cursor/environment.json) and is versioned with the repo, so it follows branches and pull requests.

**Humans still start here:** [QUICKSTART.md](QUICKSTART.md) → `./scripts/verify.sh`. The Cloud Agent config does not replace the proof gate; it prepares a machine so an agent can run it.

---

## What the config does

| Phase | Command (summary) | Purpose |
|---|---|---|
| `install` | `uv` bootstrap, then `uv sync --frozen --extra dev` | Idempotent dependency setup — the same install half as [scripts/verify.sh](../scripts/verify.sh), without running the e2e gate. |
| `terminals` | seed `.tmp/mvp-demo/operator.duckdb` (once), then `streamlit run dashboard/app.py` on `:8501` | Long-running Gov / FOIA + Orders dashboard the agent can open and inspect. |
| `ports` | `8501` | Exposes the Streamlit dashboard. |

The dashboard terminal seeds a demo warehouse on first boot by running [scripts/demo_mvp.sh](../scripts/demo_mvp.sh) only when `.tmp/mvp-demo/operator.duckdb` is missing, so restarts do not rebuild it.

---

## Lifecycle: install vs terminals

`install` runs after checkout and again when dependencies refresh, so it must stay idempotent and terminate — it never launches a server. Re-running `uv sync --frozen` on an already-synced tree is a no-op (`Checked N packages`).

The dashboard is a long-running foreground process, so it belongs in `terminals` (visible logs, restartable), not `install`.

---

## Relationship to the proof gate

The Cloud Agent config intentionally does **not** run `./harness/e2e.sh`. The proof gate is unchanged and still runs:

- locally / on first clone via `./scripts/verify.sh` (see [QUICKSTART.md](QUICKSTART.md));
- in CI on every push via [`.github/workflows/ci.yml`](https://github.com/khaosans/operator-etl/blob/master/.github/workflows/ci.yml);
- on every `v*` tag before publish via [`.github/workflows/release.yml`](https://github.com/khaosans/operator-etl/blob/master/.github/workflows/release.yml).

An agent that needs proof should run `./scripts/verify.sh` and confirm `OPERATOR_ETL_VERIFY=PASS` — see [AGENTS.md](../AGENTS.md).

---

## Run the dashboard manually

The same thing the Cloud Agent terminal does, if you want it locally:

```bash
./scripts/demo_mvp.sh                       # seeds .tmp/mvp-demo/operator.duckdb
OPERATOR_ETL_WAREHOUSE=.tmp/mvp-demo/operator.duckdb \
OPERATOR_ETL_PIPELINE_NAME=public_comments \
OPERATOR_ETL_DOMAIN=gov \
uv run streamlit run dashboard/app.py
```

Open the **Gov / FOIA** tab: Gate=PASS, silver=10, quarantined=2, PII rate 40%.

---

## See also

- [QUICKSTART.md](QUICKSTART.md) — one-command verify (humans and agents)
- [DASHBOARD.md](DASHBOARD.md) — what the Streamlit tabs show
- [CONTRIBUTING.md](../CONTRIBUTING.md) — PR workflow after verify
- [AGENTS.md](../AGENTS.md) — agent load order and non-negotiables
